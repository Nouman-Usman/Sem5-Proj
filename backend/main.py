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
import csv
from dotenv import load_dotenv
import recommend_lawyer
import gc  # Add at top with other imports
from history import AzureTableChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
from chat_summary_storage import AzureChatSummaryStorage
load_dotenv()


class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[Document]
    session_id: str  # Add session_id to state schema


class RAGAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("PINECONE_API")
        self.legal_index_name = "apna-waqeel2"
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
        self.summary_storage = AzureChatSummaryStorage(self.connection_string)
        self._initialize_summary_prompt()
        gc.collect()
        self.chat_summaries = {}
        self._initialize_summary_prompt()

    def _initialize_summary_prompt(self):
        self.summary_prompt = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
            Summarize the key points of this conversation in a concise way. Focus only on the most important information 
            that would be relevant for future context. Keep the summary under 100 words.
            
            Previous summary: {prev_summary}
            New messages:
            {new_messages}
            
            Provide an updated summary that incorporates the new information with the previous summary.
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["prev_summary", "new_messages"]
        )
        self.summarize_chain = self.summary_prompt | self.llm | StrOutputParser()

    def get_chat_history(self, session_id):
        if session_id:
            summary_data = self.summary_storage.get_summary(session_id)
            if summary_data["expired"]:
                print("Previous summary expired, starting fresh context")
            return summary_data["summary"]
        return ""

    def update_chat_summary(self, session_id: str, new_messages: List[dict]) -> str:
        prev_summary_data = self.summary_storage.get_summary(session_id)
        prev_summary = prev_summary_data["summary"]
        access_count = prev_summary_data["access_count"]
        
        formatted_messages = "\n".join([
            f"Human: {msg['content']}" if msg['type'] == 'human' 
            else f"Assistant: {msg['content']}" 
            for msg in new_messages
        ])
        
        # If frequently accessed, include more context from previous summary
        if access_count > 5:
            updated_summary = self.summarize_chain.invoke({
                "prev_summary": prev_summary,
                "new_messages": formatted_messages,
                "instruction": "This is a frequently accessed conversation, maintain more detail in the summary."
            })
        else:
            updated_summary = self.summarize_chain.invoke({
                "prev_summary": prev_summary,
                "new_messages": formatted_messages
            })
        
        # Save with merge if not expired
        self.summary_storage.save_summary(
            session_id, 
            updated_summary, 
            merge=not prev_summary_data["expired"]
        )
        return updated_summary

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
        # urls = [
        #     "https://lilianweng.github.io/posts/2023-06-23-agent/",
        #     "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
        #     "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
        # ]
        # docs = [WebBaseLoader(url).load() for url in urls]
        # docs_list = [item for sublist in docs for item in sublist]
        # text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        #     chunk_size=250, chunk_overlap=0
        # )
        # doc_splits = text_splitter.split_documents(docs_list)
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
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a legal assistant for question-answering tasks in the context of Pakistani law. Use the following pieces of retrieved legal information to answer the query. If you are unsure about the answer, simply state that. Provide well structured answers. |eot_id|><|start_header_id|>user<|end_header_id|>
            Question: {question} 
            Context: {context} 
            Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["question", "context"],
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
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an expert legal assistant specializing in routing user questions to a legal document repository or a web search. Use the legal document repository (vectorstore) for questions about case law, legal statutes, contracts, or legal research topics. Focus on legal terminology, even if the keywords are broadly related to legal topics. Otherwise, use web-search for general or factual inquiries. Provide a binary choice 'web_search' or 'vectorstore' based on the question. Return a JSON with a single key 'datasource' and no preamble or explanation. Question to route: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        input_variables=["question"],
        )
        self.question_router = (
            self.question_router_prompt | self.llm | JsonOutputParser()
        )

    def get_chat_history(self, session_id):
        if session_id:
            return self.summary_storage.get_summary(session_id)
        return ""

    def clear_session_memory(self, session_id: str):
        self.summary_storage.delete_summary(session_id)

    def generate(self, state: Dict) -> Dict:
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]
        session_id = state.get("session_id")
        
        session_id = state.get("session_id")
        
        chat_history = self.get_chat_history(session_id)
        
        context = f"Previous conversation:\n{chat_history}\n\nRelevant documents:\n" + "\n".join(
            [doc.page_content for doc in documents]
        )
        
        gc.collect()
        
        generation = self.rag_chain.invoke({
            "context": context, 
            "question": question,
        })
        
        if(filtered_metadata := blob.get_blob_urls([doc.metadata['file_name'] for doc in documents if 'file_name' in doc.metadata])):
            final_answer = f"{generation} \n Reference: {', '.join(filtered_metadata)}"
        else:
            final_answer = generation
            
        del generation
        gc.collect()
            
        return {
            "documents": documents,
            "question": question,
            "generation": final_answer,
            "session_id": session_id
        }

    def retrieve(self, state: Dict) -> Dict:
        print("---RETRIEVE---")
        question = state["question"]
        session_id = state.get("session_id")
        documents = self.retriever.invoke(question)
        documents = documents[:5] if len(documents) > 5 else documents
        gc.collect()
        return {"documents": documents, "question": question, "session_id": session_id}

    def generate(self, state: Dict) -> Dict:
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]
        gc.collect()
        
        generation = self.rag_chain.invoke({
            "context": documents, 
            "question": question,
        })
        
        # if(filtered_metadata := blob.get_blob_urls([doc.metadata['file_name'] for doc in documents if 'file_name' in doc.metadata])):
        #     final_answer = f"{generation} \n Reference: {', '.join(filtered_metadata)}"
        # else:
        #     final_answer = generation
        final_answer = generation    
        del generation
        gc.collect()
            
        return {
            "documents": documents,
            "question": question,
            "generation": final_answer,
        }

    def grade_documents(self, state: Dict) -> Dict:
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]
        session_id = state.get("session_id")
        filtered_docs = []
        web_search = "No"
        for d in (documents):
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
            "session_id": session_id
        }

    def web_search(self, state: Dict) -> Dict:
        print("---WEB SEARCH---")
        question = state["question"]
        session_id = state.get("session_id")
        documents = state.get("documents", [])
        
        docs = self.web_search_tool.invoke({"query": question})
        
        # Limit results to prevent memory issues
        if isinstance(docs, list):
            docs = docs[:3]

        # ...existing code...
        
        gc.collect()
        return {"documents": docs, "question": question, "session_id": session_id}

    def route_question(self, state: Dict) -> str:
        print("---ROUTE QUESTION---")
        question = state["question"]
        source = self.question_router.invoke({"question": question})
        if source["datasource"] == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "websearch"
        elif source["datasource"] == "vectorstore":
            print("---ROUTE QUESTION TO RAG---")
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
        generation = state["generation"]
        try:
            score = self.hallucination_grader.invoke(
                {"documents": documents, "generation": generation}
            )
            grade = score["score"]
            if grade == "yes":
                print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
                score = self.answer_grader.invoke(
                    {"question": question, "generation": generation}
                )
                grade = score["score"]
                if grade == "yes":
                    print("---DECISION: GENERATION ADDRESSES QUESTION---")
                    return "useful"
                else:
                    print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                    return "not useful"
            else:
                pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
                return "not supported"
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return "not supported"

    def build_workflow(self):
        workflow = StateGraph(state_schema=GraphState)
        workflow.add_node("websearch", self.web_search)
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("generate", self.generate)
        workflow.set_conditional_entry_point(
            self.route_question,
            {
                "websearch": "websearch",
                "vectorstore": "retrieve",
            },
        )
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
        workflow.add_conditional_edges(
            "generate",
            self.grade_generation_v_documents_and_question,
            {
                "not supported": "generate",
                "useful": END,
                "not useful": "websearch",
            },
        )
        return workflow.compile()

    def run(self, question: str, session_id: str = None):
        try:
            if session_id:
                chat_history = AzureTableChatMessageHistory(
                    session_id=session_id,
                    connection_string=self.connection_string
                )
                
                # Add user question to history
                chat_history.add_message(HumanMessage(content=question))
                
                # Get last few messages for summary update
                last_messages = [
                    {"type": "human", "content": question}
                ]
                
                # Update summary with new messages
                self.update_chat_summary(session_id, last_messages)
            
            # Perform sentiment analysis on the question
            sentiment = self.analyze_sentiment(question)
            print(f"Sentiment: {sentiment}")
            
            # Recommend a lawyer based on the sentiment category
            recommendation = recommend_lawyer.recommend_lawyer(sentiment)
            print(recommendation)
            # breakpoint()
            # Continue with the existing workflow
            app = self.build_workflow()
            inputs = {"question": question, "session_id": session_id}
            last_output = None
            for output in app.stream(inputs):
                for key, value in output.items():
                    pprint(f"Finished running: {key}:")
                    print("Output:")
                    pprint(value)
                    last_output = value
                gc.collect()  # Collect garbage after each iteration
            
            result = last_output["generation"]
            
            if session_id:
                chat_history.add_message(AIMessage(content=result))
                self.update_chat_summary(session_id, [
                    {"type": "assistant", "content": result}
                ])
            
            gc.collect()
            return result
        
        finally:
            gc.collect()


if __name__ == "__main__":
    agent = RAGAgent()  
    # First access
    agent.run("What are my rights?", session_id="user123")
    agent.run("Can you elaborate on that?", session_id="user123")