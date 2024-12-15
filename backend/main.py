import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_groq import ChatGroq
import uuid
from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import END, StateGraph
from typing import List, Dict, TypedDict, Any, Optional
from pprint import pprint
import blob
from pinecone import Pinecone
import json
from transformers import pipeline
import logging
import csv
from dotenv import load_dotenv
import recommend_lawyer
import gc
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from lawyer_store import LawyerStore
from langchain.memory import ConversationBufferWindowMemory
import datetime
import pyodbc
from crud import ChatMessageCRUD, ChatSessionCRUD  # Add this import

load_dotenv()


class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[Document]
    source: List[str]


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
        self.connection_string = os.getenv("SQL_CONN_STRING")
        if not self.connection_string:
            raise ValueError("SQL_CONN_STRING environment variable is not set")
        self.lawyer_store = LawyerStore(connection_string=self.connection_string)
        gc.collect()
        self.max_context_length = 4096
        self.memory = ConversationBufferWindowMemory(k=5)
        self.chats_loaded = False

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
        print(f"Sentiment: {sentiment}")
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
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a legal assistant for question-answering tasks in the context of Pakistani law. Structure your responses in Markdown format following this template:

# Legal Response
[Provide a clear, concise summary of the answer]

## Detailed Explanation
[Provide a detailed explanation of the legal concepts, requirements, or procedures]

## Key Points
[List the most important points or steps as bullet points]
* Point 1
* Point 2
* Point 3

## Legal Context
[If relevant, provide any important legal context, citations, or references]

Previous conversation context:
{chat_history}

Question: {question} 
Retrieved information: {context} 

Remember to:
1. Use Markdown headers (# for main title, ## for sections)
2. Use bullet points (*) for lists
3. Use bold (**) for emphasis on important terms
4. Include relevant legal citations where applicable
5. Use <br> for line breaks

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

    def generate(self, state: Dict) -> Dict:
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]
        sources = []
        chat_context = self.memory.load_memory_variables({})["history"]

        doc_texts = []
        total_length = len(question) + len(chat_context)
        for doc in documents:
            doc_text = doc.page_content[:1000]
            if total_length + len(doc_text) > self.max_context_length:
                break
            doc_texts.append(doc_text)
            total_length += len(doc_text)
            # Extract source from document metadata if available
            if isinstance(doc, Document):
                if "source" in doc.metadata:
                    if not doc.metadata["source"].startswith("/kaggle"):                        
                        sources.append(doc.metadata["source"])
                elif "file_name" in doc.metadata:
                    sources.append(doc.metadata["file_name"])

        context = "\n".join(doc_texts)
        gc.collect()
        generation = self.rag_chain.invoke({
            "context": context,
            "question": question,
            "chat_history": chat_context
        })

        if filtered_metadata := blob.get_blob_urls([
            doc.metadata["file_name"]
            for doc in documents
            if "file_name" in doc.metadata
        ]):
            sources.extend(filtered_metadata)

        # Add sources section in Markdown
        # source_list = "\n".join([f"* {source}" for source in sources])
        final_answer = f"{generation}"

        del generation
        gc.collect()

        return {
            "documents": documents,
            "question": question,
            "generation": final_answer,
            "source": sources
        }

    def retrieve(self, state: Dict) -> Dict:
        print("---RETRIEVE---")
        question = state["question"]
        documents = self.retriever.invoke(question)
        documents = documents[:5] if len(documents) > 5 else documents
        gc.collect()
        return {
            "documents": documents,
            "question": question,
            "source": [],  # Initialize empty source list
        }

    def grade_documents(self, state: Dict) -> Dict:
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]
        source = state["source"]
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
            "source": source,
        }

    def web_search(self, state: Dict) -> Dict:
        print("---WEB SEARCH---")
        question = state["question"]
        documents = state.get("documents", [])
        sources = state.get("source", [])  # Get existing sources or initialize empty list

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
            "source": sources,  # Maintain source state
        }

    def route_question(self, state: Dict) -> str:
        print("---ROUTE QUESTION---")
        question = state["question"]
        try:
            route = "vectorstore"
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
        if web_search == "Yes":
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
        source = state["source"]
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

    def update_query(self, question: str, chat_history: str) -> str:
        print("---UPDATE QUERY---")
        prompt = f"""
        Given the following chat history, update the user's query to be more structured and clear:
        
        Chat History:
        {chat_history}
        
        Original Query: {question}
        
        Updated Query:
        """
        updated_query_result = self.llm.invoke(prompt)
        updated_query = updated_query_result.content.strip()
        return updated_query

    def get_chat_topic(self, question: str) -> str:
        print("---GET CHAT TOPIC---")
        prompt = f"""
        Provide me with the three to four words that best describe the topic of the chat:
        {question}
        """
        topic_result = self.llm.invoke(prompt)
        topic = topic_result.content.strip()
        return topic

    def build_workflow(self):
        workflow = StateGraph(state_schema=GraphState)

        # Add nodes with attempt tracking capabilities
        workflow.add_node("websearch", self.web_search)
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("update_query", self.update_query)  # Add update_query node
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
                "generate": "update_query",  # Route to update_query before generate
            },
        )

        workflow.add_edge(
            "update_query", "generate"
        )  # Add edge from update_query to generate
        workflow.add_edge("websearch", "generate")

        # Add conditional edges for generation grading
        workflow.add_conditional_edges(
            "generate",
            self.grade_generation_v_documents_and_question,
            {"not supported": "generate", "not useful": "websearch", "useful": END},
        )

        return workflow.compile()

    def run(
        self,
        question: str,
        chat_history: List[Dict] = None,
    ) -> Dict[str, Any]:
        try:
            if chat_history is None:
                chat_history = []
            else:
                for message in chat_history:
                    # Handle pyodbc.Row objects by accessing columns directly
                    try:
                        # Try dictionary access first
                        role = message.get('Type') if isinstance(message, dict) else message.role
                        content = message.get('content') if isinstance(message, dict) else message.content
                        
                        if role == 'Human Message' or role == 'user':
                            self.memory.save_context({'input': content}, {'output': ''})
                        elif role == 'AI Message' or role == 'assistant':
                            self.memory.save_context({'input': ''}, {'output': content})
                    except AttributeError:
                        # If message is a tuple/row, try positional access
                        # Assuming the order is (role, content, ...)
                        if isinstance(message, tuple):
                            role, content = message[0], message[1]
                            if role in ('Human Message', 'user'):
                                self.memory.save_context({'input': content}, {'output': ''})
                            elif role in ('AI Message', 'assistant'):
                                self.memory.save_context({'input': ''}, {'output': content})

            chat_context = self.memory.load_memory_variables({})["history"]
            updated_question = self.update_query(question, chat_context)
            sentiment = self.analyze_sentiment(updated_question)
            logging.info(f"Sentiment: {sentiment}")
            # recommendations = self.lawyer_store.get_top_lawyers(sentiment)
            # logging.info(f"Lawyer recommendations: {recommendations}")

            app = self.build_workflow()
            inputs = {
                "question": updated_question,
                "chat_history": chat_context,
                "source": [],  # Initialize source in initial state
            }
            last_output = None
            try:
                for output in app.stream(inputs):
                    for key, value,  in output.items():
                        pprint(f"Finished running: {key}:")
                        print("Output:")
                        last_output = value                        
                    gc.collect()
                result = last_output["generation"]
                logging.info(f"Result: {result}")
                # print(f"Result: {last_output['source']}")
                # breakpoint()
                response_text = result if isinstance(result, str) else str(result)
                response = {
                    "chat_response": response_text,
                    "references": last_output["source"],
                    "Sentiment": sentiment,
                }
                return response

            except Exception as e:
                print(f"Error in RAG workflow: {e}")
                return {
                    "chat_response": "I apologize, but I encountered an error processing your request.",
                    "references": [],
                    "recommended_lawyers": [],
                }

        finally:
            gc.collect()

    def retrieve_dataset(self):
        """Retrieve all documents from the Pinecone index"""
        try:
            # Use vectorstore's similarity search to get all documents
            documents = self.vectorstore.similarity_search(query="", k=100)
            documents = [
                doc
                for doc in documents
                if doc.page_content and doc.page_content.strip()
            ]
            print(f"Retrieved {len(documents)} documents from vectorstore")
            return documents
        except Exception as e:
            print(f"Error retrieving dataset: {e}")
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

    def save_context(self, user_input: str, assistant_output: str):
        self.memory.save_context({"input": user_input}, {"output": assistant_output})

    def is_valid_uuid(self, uuid_str: str) -> bool:
        try:
            uuid.UUID(uuid_str)
            return True
        except (ValueError, AttributeError, TypeError):
            return False
