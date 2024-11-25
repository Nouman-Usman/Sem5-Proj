import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
# from langchain_community.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_groq import ChatGroq
from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import END, StateGraph
from typing import List, Dict, TypedDict
from pprint import pprint
import blob
from pinecone import Pinecone
import json
from transformers import pipeline
import logging
import csv
from dotenv import load_dotenv
import recommend_lawyer
import gc  # Add at top with other imports
from history import AzureTableChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from lawyer_store import LawyerStore

load_dotenv()


class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[Document]
    chat_id: str  # Add chat_id to state schema
    user_id: str


class RAGAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("PINECONE_API")
        self.legal_index_name = "apna-waqeel3"
        self.web_search_index_name = "web-search-legal"
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.legal_index_name)
        self.web_search_index = self.pc.Index(self.web_search_index_name)
        self.llm = ChatGroq(
            temperature=0, model="llama3-groq-70b-8192-tool-use-preview"
        )
        self.vectorstore = None
        self.retriever = None
        self.web_search_tool = TavilySearchResults(k=3)
        self._initialize_vectorstore()
        self._initialize_prompts()
        self.connection_string = os.getenv("BLOB_CONN_STRING")
        self.lawyer_store = LawyerStore(connection_string=self.connection_string)
        gc.collect()
        self.max_context_length = 4096  # Add max context length

    def get_chat_history(self, chat_id):  # Changed from chat_id
        if (chat_id):
            try:
                chat_history = AzureTableChatMessageHistory(
                    chat_id=chat_id,  # Changed from chat_id
                    user_id=self.user_id,
                    connection_string=self.connection_string
                )
                messages = chat_history.messages[-4:]  # Get last 4 messages
                return "\n".join(
                    [
                        (
                            f"Human: {msg.content}"
                            if isinstance(msg, HumanMessage)
                            else f"Assistant: {msg.content}"
                        )
                        for msg in messages
                    ]
                )
            except Exception as e:
                print(f"Error getting chat history: {e}")
                return ""
        return ""

    def _load_lawyers(self):
        with open("lawyers.csv", mode="r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                self.lawyers.append(row)
        print("Lawyers data loaded successfully.")

    def _recommend_lawyer(self, specialty):
        relevant_lawyers = [
            lawyer
            for lawyer in self.lawyers
            if lawyer["Type (Specialty)"].lower() == specialty.lower()
        ]
        if not relevant_lawyers:
            return "No lawyer found for this specialty."

        best_lawyer = max(relevant_lawyers, key=lambda l: float(l["Ratings"]))
        return (
            f"Recommended lawyer: {best_lawyer['Lawyer Name']}, Specialty: {best_lawyer['Type (Specialty)']}, "
            f"Experience: {best_lawyer['Experience (Years)']} years, Ratings: {best_lawyer['Ratings']}/5, "
            f"Location: {best_lawyer['Location']}."
        )

    def analyze_sentiment(self, question: str) -> str:
        print("---SENTIMENT ANALYSIS---")
        prompt = f"""
        Analyze the sentiment of the following text and categorize it into one of the following categories:
        1. Civil 
        2. Criminal 
        3. Corporate
        4. Constitutional
        5. Tax 
        6. Family
        7. Intellectual Property
        8. Labor and Employment 
        9. Immigration 
        10. Human Rights
        11. Environmental
        12. Banking and Finance
        13. Cyber Law 
        14. Alternate Dispute Resolution (ADR)

Please return only the category name that best fits the text: "{question}"
"""
        sentiment_result = self.llm.invoke(prompt)
        sentiment = sentiment_result.content.strip()
        return sentiment

    def _initialize_vectorstore(self):
        embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
        self.vectorstore = PineconeVectorStore(index=self.index, embedding=embeddings)
        # self.vectorstore.add_documents(doc_splits)
        self.retriever = self.vectorstore.as_retriever()
        print("Vectorstore initialized and documents added.")

    def _initialize_prompts(self):
        self.retrieval_grader_prompt = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing relevance 
            of a retrieved document to a user question. If the document contains keywords related to the user question, 
            grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
            Provide the binary score as a JSON with a single key 'score' and no premable or explaination.
             <|eot_id|><|start_header_id|>user<|end_header_id|>
            Here is the retrieved document: \n\n {document} \n\n
            Here is the user question: {question} \n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """,
            input_variables=["question", "document"],
        )
        self.retrieval_grader = (
            self.retrieval_grader_prompt | self.llm | JsonOutputParser()
        )

        self.generate_prompt = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a legal assistant for question-answering tasks in the context of Pakistani law. Use the following pieces of retrieved legal information and conversation history to answer the query. If the question is asking for elaboration, provide more detailed information about the previous response. If you are unsure about the answer, simply state that. Provide well structured answers.

Previous conversation context:
{chat_history}

Question: {question} 
Retrieved information: {context} 

Provide a detailed response that builds upon the previous context when appropriate.
<|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["question", "context", "chat_history"],
        )
        self.rag_chain = self.generate_prompt | self.llm | StrOutputParser()

        self.hallucination_grader_prompt = PromptTemplate(
            template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether 
            an answer is grounded in / supported by a set of facts. Give a binary score 'yes' or 'no' score to indicate 
            whether the answer is grounded in / supported by a set of facts. Provide the binary score as a JSON with a 
            single key 'score' and no preamble or explanation. <|eot_id|><|start_header_id|>user<|end_header_id|>
            Here are the facts:
            \n ------- \n
            {documents} 
            \n ------- \n
            Here is the answer: {generation}  <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["generation", "documents"],
        )
        self.hallucination_grader = (
            self.hallucination_grader_prompt | self.llm | JsonOutputParser()
        )

        self.answer_grader_prompt = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether an 
            answer is useful to resolve a question. Give a binary score 'yes' or 'no' to indicate whether the answer is 
            useful to resolve a question. Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
             <|eot_id|><|start_header_id|>user<|end_header_id|> Here is the answer:
            \n ------- \n
            {generation} 
            \n ------- \n
            Here is the question: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["generation", "question"],
        )
        self.answer_grader = self.answer_grader_prompt | self.llm | JsonOutputParser()

        self.question_router_prompt = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert legal assistant specializing in routing user questions.
For questions about case law, legal statutes, contracts, or legal research topics, use vectorstore.
For general inquiries or factual questions, use web search.
Return only one of these two exact strings: "vectorstore" or "web_search"

Question to route: {question}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["question"],
        )

        self.question_router = (
            self.question_router_prompt | self.llm | StrOutputParser()
        )

    def get_chat_history(self, chat_id):
        if chat_id:
            return self.summary_storage.get_summary(chat_id)
        return ""

    def clear_session_memory(self, chat_id: str):
        self.summary_storage.delete_summary(chat_id)

    def generate(self, state: Dict) -> Dict:
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]
        chat_id = state.get("chat_id")
        user_id = state.get("user_id")
        chat_context = ""
        if chat_id and user_id:
            try:
                chat_history = self.get_chat_messages(user_id, chat_id)[-2:]
                if chat_history:
                    chat_context = "\n".join(
                        [
                            (
                                f"Human: {msg.content[:500]}"  
                                if isinstance(msg, HumanMessage)
                                else f"Assistant: {msg.content[:500]}"
                            )
                            for msg in chat_history
                        ]
                    )
            except Exception as e:
                print(f"Error getting chat history: {e}")
        doc_texts = []
        total_length = len(question) + len(chat_context)
        for doc in documents:
            doc_text = doc.page_content[:1000]  
            if total_length + len(doc_text) > self.max_context_length:
                break
            doc_texts.append(doc_text)
            total_length += len(doc_text)

        context = "\n".join(doc_texts)

        gc.collect()

        generation = self.rag_chain.invoke(
            {"context": context, "question": question, "chat_history": chat_context}
        )

        if filtered_metadata := blob.get_blob_urls(
            [
                doc.metadata["file_name"]
                for doc in documents
                if "file_name" in doc.metadata
            ]
        ):
            final_answer = f"{generation} \n Reference: {', '.join(filtered_metadata)}"
        else:
            for doc in documents:
                if "source" in doc.metadata:
                    source = doc.metadata["source"]
                    print(f"Source: {source}")
                else:
                    source = [] 
            
            # Source is a list of sources, so we need to join them in the final generation
            # final_answer = f"{generation} \n Source: {', '.join(source)}"
            # breakpoint()
            final_answer = f"{generation}"
            # final_answer = generation
        del generation
        gc.collect()

        return {
            "documents": documents,
            "question": question,
            "generation": final_answer,
            "chat_id": chat_id,
            "user_id": user_id,
        }

    def store_session(self, chat_id: str, session_data: dict):
        """Store session data in Azure Table"""
        try:
            chat_history = AzureTableChatMessageHistory(
                chat_id=chat_id,
                user_id=session_data['user_id'],
                connection_string=self.connection_string
            )
            
            # Store session data (already contains serialized dates)
            chat_history.store_session_data(session_data)
            
        except Exception as e:
            logging.error(f"Error storing session: {e}")
            raise

    def web_search(self, state: Dict) -> Dict:
        print("---WEB SEARCH---")
        question = state["question"]
        chat_id = state.get("chat_id")
        user_id = state.get("user_id")  # Add user_id
        documents = state.get("documents", [])

        try:
            docs = self.web_search_tool.invoke({"query": question})

            # Limit results to prevent memory issues
            if isinstance(docs, list):
                docs = docs[:3]

            # Convert search results to Document objects
            web_documents = []
            for doc in docs:
                web_documents.append(
                    Document(
                        page_content=f"Title: {doc.get('title', '')}\nContent: {doc.get('content', '')}",
                        metadata={
                            "source": doc.get("url", ""),
                            "score": doc.get("score", 0),
                        },
                    )
                )
            if documents:
                web_documents.extend(documents)

        except Exception as e:
            print(f"Web search error: {e}")
            web_documents = documents
        gc.collect()
        return {
            "documents": web_documents,
            "question": question,
            "chat_id": chat_id,
            "user_id": user_id,
        }

    def retrieve(self, state: Dict) -> Dict:
        print("---RETRIEVE---")
        question = state["question"]
        chat_id = state.get("chat_id")
        user_id = state.get("user_id")
        documents = self.retriever.invoke(question)
        documents = documents[:5] if len(documents) > 5 else documents
        gc.collect()
        return {
            "documents": documents,
            "question": question,
            "chat_id": chat_id,
            "user_id": user_id,  # Include user_id in return
        }

    def grade_documents(self, state: Dict) -> Dict:
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]
        chat_id = state.get("chat_id")
        filtered_docs = []
        web_search = "No"
        for d in documents:
            score = self.retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score["score"]
            if grade.lower() == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
                # filtered_metadata.append(m)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                web_search = "Yes"
                continue
        return {
            "documents": filtered_docs,
            "question": question,
            "web_search": web_search,
            "chat_id": chat_id,
        }

    def web_search(self, state: Dict) -> Dict:
        print("---WEB SEARCH---")
        question = state["question"]
        chat_id = state.get("chat_id")
        documents = state.get("documents", [])

        try:
            docs = self.web_search_tool.invoke({"query": question})

            # Limit results to prevent memory issues
            if isinstance(docs, list):
                docs = docs[:3]

            # Convert search results to Document objects
            web_documents = []
            for doc in docs:
                web_documents.append(
                    Document(
                        page_content=f"Title: {doc.get('title', '')}\nContent: {doc.get('content', '')}",
                        metadata={
                            "source": doc.get("url", ""),
                            "score": doc.get("score", 0),
                        },
                    )
                )
            if documents:
                web_documents.extend(documents)

        except Exception as e:
            print(f"Web search error: {e}")
            web_documents = documents
        gc.collect()
        return {
            "documents": web_documents,
            "question": question,
            "chat_id": chat_id,
        }

    def route_question(self, state: Dict) -> str:
        print("---ROUTE QUESTION---")
        question = state["question"]
        try:
            route = self.question_router.invoke({"question": question}).strip().lower()
            if route == "web_search":
                print("---ROUTE QUESTION TO WEB SEARCH---")
                return "websearch"
            else:
                print("---ROUTE QUESTION TO RAG---")
                return "vectorstore"
        except Exception as e:
            print(f"Routing error: {e}, defaulting to vectorstore")
            return "vectorstore"

    def decide_to_generate(self, state: Dict) -> str:
        print("---ASSESS GRADED DOCUMENTS---")
        web_search = state["web_search"]
        if (web_search == "Yes"):
            print(
                "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
            )
            return "websearch"
        else:
            print("---DECISION: GENERATE---")
            return "generate"

    def grade_generation_v_documents_and_question(self, state: Dict) -> str:
        print("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]
        attempts = state.get("attempts", 0)  # Track retry attempts

        # If we've tried too many times, return the result anyway
        if attempts >= 2:
            print("---MAX RETRIES REACHED, RETURNING CURRENT GENERATION---")
            return "useful"

        try:
            score = self.hallucination_grader.invoke(
                {"documents": documents, "generation": generation}
            )
            grade = score["score"]
            if grade.lower() == "yes":
                print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
                score = self.answer_grader.invoke(
                    {"question": question, "generation": generation}
                )
                grade = score["score"]
                if grade.lower() == "yes":
                    print("---DECISION: GENERATION ADDRESSES QUESTION---")
                    return "useful"
                else:
                    print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                    if attempts < 2:
                        return "not useful"
                    return "useful"
            else:
                print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
                if attempts < 2:
                    return "not supported"
                return "useful"
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return "useful"  # Fall back to accepting the generation

    def build_workflow(self):
        workflow = StateGraph(state_schema=GraphState)

        # Add nodes with attempt tracking capabilities
        workflow.add_node("websearch", self.web_search)
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node(
            "generate",
            lambda x: {**x, "attempts": x.get("attempts", 0) + 1} | self.generate(x),
        )

        # Set entry point
        workflow.set_conditional_entry_point(
            self.route_question,
            {
                "websearch": "websearch",
                "vectorstore": "retrieve",
            },
        )

        # Add basic edges
        workflow.add_edge("retrieve", "grade_documents")

        workflow.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "websearch": "websearch",
                "generate": "generate",
            },
        )

        workflow.add_edge("websearch", "generate")

        # Add conditional edges for generation grading
        workflow.add_conditional_edges(
            "generate",
            self.grade_generation_v_documents_and_question,
            {"not supported": "generate", "not useful": "websearch", "useful": END},
        )

        return workflow.compile()

    def run(self, question: str, user_id: str, chat_id: str = None, chat_history: List[Dict] = None):
        try:
            if chat_history is None:
                chat_history = []

            # Process the question
            sentiment = self.analyze_sentiment(question)
            logging.info(f"Sentiment: {sentiment}")
            
            # Get lawyer recommendations using LawyerStore
            recommendation = self._get_lawyer_recommendations(sentiment)
            logging.info(f"Lawyer recommendation: {recommendation}")

            app = self.build_workflow()
            inputs = {
                "question": question,
                "chat_id": chat_id,
                "user_id": user_id,
                "chat_history": chat_history  # Include chat history in inputs
            }
            last_output = None

            try:
                for output in app.stream(inputs):
                    for key, value in output.items():
                        pprint(f"Finished running: {key}:")
                        print("Output:")
                        pprint(value)
                        last_output = value
                    gc.collect()

                result = last_output["generation"]

                if chat_id and result:
                    chat_history_obj = AzureTableChatMessageHistory(
                        chat_id=chat_id,
                        user_id=user_id,
                        connection_string=self.connection_string,
                    )
                    chat_history_obj.add_message(HumanMessage(content=question))
                    chat_history_obj.add_message(AIMessage(content=result))

                # Extract references from documents
                references = []
                for doc in last_output["documents"]:
                    if "source" in doc.metadata:
                        references.append(doc.metadata["source"])

                return result, references

            except Exception as e:
                print(f"Error in RAG workflow: {e}")
                return (
                    "I apologize, but I encountered an error processing your request.",
                    []
                )

        finally:
            gc.collect()

    def get_user_chat_history(self, user_id: str, chat_id: str) -> List[str]:
        """Get all chat sessions for a user"""
        chat_history = AzureTableChatMessageHistory(
            chat_id=chat_id,  # Changed from chat_id
            user_id=user_id,
            connection_string=self.connection_string
        )

        return chat_history.get_user_chats(user_id)

    def get_chat_messages(self, user_id: str, chat_id: str) -> List[BaseMessage]:
        """Get all messages for a specific chat"""
        chat_history = AzureTableChatMessageHistory(
            chat_id=chat_id,  # Changed from chat_id
            user_id=user_id,
            connection_string=self.connection_string,
        )
        return chat_history.get_chat_messages(user_id, chat_id)

    def retrieve_dataset(self):
        """Retrieve all documents from the Pinecone index"""
        try:
            # Use vectorstore's similarity search to get all documents
            documents = self.vectorstore.similarity_search(
                query="",  
                k=100  
            )            
            documents = [
                doc for doc in documents 
                if doc.page_content and doc.page_content.strip()
            ]            
            print(f"Retrieved {len(documents)} documents from vectorstore")
            return documents            
        except Exception as e:
            print(f"Error retrieving dataset: {e}")
            return []
    def get_chat_history_messages(self, user_id: str, chat_id: str) -> List[Dict]:
        """Get full chat history with messages for a specific chat"""
        try:
            chat_history = AzureTableChatMessageHistory(
                chat_id=chat_id,
                user_id=user_id,
                connection_string=self.connection_string
            )
            messages = []
            for msg in chat_history.messages:
                messages.append({
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content,
                })
            return messages
        except Exception as e:
            logging.error(f"Error retrieving chat history: {e}")
            return []

    def _get_lawyer_recommendations(self, category: str) -> str:
        """Get formatted lawyer recommendations"""
        try:
            top_lawyers = self.lawyer_store.get_top_lawyers(category, limit=2)
            
            if not top_lawyers:
                return "No lawyers found for this specialty."
            
            recommendation = "Top recommended lawyers:\n\n"
            for lawyer in top_lawyers:
                recommendation += (
                    f"- {lawyer['name']}\n"
                    f"  Specialty: {lawyer['specialization']}\n"
                    f"  Experience: {lawyer['experience']}\n"
                    f"  Rating: {lawyer['rating']}/5\n"
                    f"  Location: {lawyer['location']}\n"
                    f"  Contact: {lawyer['contact']}\n\n"
                )
            
            return recommendation
        except Exception as e:
            logging.error(f"Error getting lawyer recommendations: {e}")
            return "Unable to retrieve lawyer recommendations at this time."

if __name__ == "__main__":
    agent = RAGAgent()
    question = "How to file a FIR in Pakistan?"
    user_id = "test_user"
    chat_id = "test_session"  # Changed from chat_id
    result = agent.run(question, user_id, chat_id)
    print(result)