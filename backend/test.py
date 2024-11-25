import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
import gc
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_groq import ChatGroq
from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import END, StateGraph
from typing import List, Dict, TypedDict, Generator
from itertools import islice
from history import AzureTableChatMessageHistory
from langchain.schema import HumanMessage, AIMessage

from pprint import pprint
import blob
from pinecone import Pinecone
from datetime import datetime, timedelta
import json
from transformers import pipeline
import csv
from dotenv import load_dotenv
import recommend_lawyer
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory
from langchain_core.vectorstores import VectorStoreRetriever
load_dotenv()

class CombinedMemory:
    def __init__(self, vectorstore: PineconeVectorStore):
        self.vectorstore = vectorstore
        self.buffer_memories = {}  
        self.vector_memories = {} 

    def get_memory(self, chat_id: str):
        if (chat_id not in self.buffer_memories):
            self.buffer_memories[chat_id] = ConversationBufferMemory(
                memory_key="chat_history",
                input_key="input",
                return_messages=True
            )
            self.vector_memories[chat_id] = VectorStoreRetrieverMemory(
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
                memory_key="relevant_history",
                input_key="input"
            )
        return self.buffer_memories[chat_id], self.vector_memories[chat_id]

    def save_context(self, chat_id, inputs, outputs):
        buffer_memory, vector_memory = self.get_memory(chat_id)
        # Ensure inputs has the required key
        if ("input" not in inputs and len(inputs) > 0):
            first_key = next(iter(inputs))
            inputs = {"input": inputs[first_key]}
        
        # Save to buffer memory
        buffer_memory.save_context(inputs, outputs)
        
        # Truncate outputs before saving to vector memory
        if (isinstance(outputs, dict)):
            truncated_outputs = {k: self._truncate_text(str(v)) for k, v in outputs.items()}
        else:
            truncated_outputs = self._truncate_text(str(outputs))
        
        try:
            vector_memory.save_context(inputs, truncated_outputs)
        except Exception as e:
            print(f"Warning: Failed to save to vector memory: {e}")

    def load_memory_variables(self, chat_id, inputs):
        buffer_memory, vector_memory = self.get_memory(chat_id)
        # Ensure inputs has the required key
        if (not inputs):
            inputs = {"input": ""}
        buffer_vars = buffer_memory.load_memory_variables(inputs)
        vector_vars = vector_memory.load_memory_variables(inputs)
        return {**buffer_vars, **vector_vars}
    
    def clear_memory(self, chat_id):
        if (chat_id in self.buffer_memories):
            del self.buffer_memories[chat_id]
        if (chat_id in self.vector_memories):
            del self.vector_memories[chat_id]

    def _truncate_text(self, text: str, max_length: int = 1000) -> str:
        """
        Truncate the text to the specified maximum length.
        
        Args:
            text (str): The text to be truncated.
            max_length (int): The maximum allowed length of the text.
        
        Returns:
            str: The truncated text.
        """
        return text if len(text) <= max_length else text[:max_length] + "..."


class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[Document]


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
        self.session_index_name = "session-storage"
        self._initialize_session_index()
        self.embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
        self.batch_size = 100  # For batch processing
        gc.enable()  # Ensure garbage collection is enabled

    def _initialize_vectorstore(self):
        try:
            embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
            self.vectorstore = PineconeVectorStore(index=self.index, embedding=embeddings)
            self.retriever = self.vectorstore.as_retriever()
            self.memory = CombinedMemory(self.vectorstore)
            print("Vectorstore initialized and memory created.")
            gc.collect()  # Force garbage collection after initialization
        finally:
            gc.collect()

    def _initialize_session_index(self):
        """Initialize or get the session storage index"""
        try:
            self.session_index = self.pc.Index(self.session_index_name)
            print("Successfully connected to existing session index")
        except Exception as e:
            print(f"Session index not found, attempting to create new one: {e}")
            try:
                # Create index with correct dimension
                self.pc.create_index(
                    name=self.session_index_name,
                    dimension=1024,  # Match embedding dimension
                    metric='cosine',
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "ap-southeast-1"
                        }
                    }
                )
                import time
                time.sleep(5)
                self.session_index = self.pc.Index(self.session_index_name)
                print(f"Created new session index: {self.session_index_name}")
            except Exception as create_error:
                print(f"Error creating session index: {create_error}")
                self.session_index = None
                
            if self.session_index is None:
                print("WARNING: Operating in memory-only mode, sessions will not persist between restarts")

    def get_recommended_lawyers(self, question: str) -> list:
        """Returns recommended lawyers based on question sentiment"""
        # 9. Immigration 
        sentiment = self.analyze_sentiment(question)
        print(f"Sentiment: {sentiment}")
        return recommend_lawyer.recommend(sentiment)

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

    Please return only the category name that best fits the text if none fits then return None: "{question}"
"""
        sentiment_result = self.llm.invoke(prompt)
        sentiment = sentiment_result.content.strip()
        print(f"Sentiment: {sentiment}")
        return sentiment

    def answer_question(self, question: str, chat_id: str) -> str:
        print("---ANSWERING QUESTION---")
        sentiment = self.analyze_sentiment(question)
        print(f"Sentiment: {sentiment}")

        # Retrieve relevant documents
        relevant_docs = self.retriever.get_relevant_documents(question)
        print(f"Number of relevant documents: {len(relevant_docs)}")
        
        # Perform web search
        web_search_results = self.web_search_tool.run(question)
        print(f"Web search results: {web_search_results}")

        # Load memory variables
        memory_variables = self.memory.load_memory_variables(chat_id, {"input": question})
        chat_history = memory_variables.get("chat_history", [])
        relevant_history = memory_variables.get("relevant_history", "")

        # Combine all information
        context = "\n".join([doc.page_content for doc in relevant_docs])
        web_context = "\n".join([result['content'] for result in web_search_results])

        # Generate answer
        prompt = f"""Based on the following information, provide a comprehensive answer:
        Question: {question}
        Context: {context}
        Web Context: {web_context}
        Chat History: {chat_history}
        Relevant History: {relevant_history}

        Provide the answer followed by the lawyer recommendations.
        """
        response = self.llm.invoke(prompt)
        print(f"Generated response: {response.content}")
        self.memory.save_context(chat_id, {"input": question}, {"output": response.content})
        return response.content

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
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an expert at routing a 
            user question to a vectorstore or web search. Use the vectorstore for questions on LLM  agents, 
            prompt engineering, and adversarial attacks. You do not need to be stringent with the keywords 
            in the question related to these topics. Otherwise, use web-search. Give a binary choice 'web_search' 
            or 'vectorstore' based on the question. Return the a JSON with a single key 'datasource' and 
            no premable or explaination. Question to route: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["question"],
        )
        self.question_router = (
            self.question_router_prompt | self.llm | JsonOutputParser()
        )

    def is_legal_query(self, question: str) -> bool:
        """Check if the query is law-related."""
        prompt = """Determine if the following question is related to law, legal matters, or legal proceedings. 
        Respond with only 'yes' or 'no'.
        
        Question: {question}
        """
        response = self.llm.invoke(prompt.format(question=question))
        return response.content.strip().lower() == 'yes'

    def route_question(self, state: Dict) -> str:
        print("---ROUTE QUESTION---")
        question = state["question"]
        chat_id = state.get("chat_id")  # Ensure chat_id is retrieved
        
        source = self.question_router.invoke({"question": question})
        if (source["datasource"] == "web_search"):
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "websearch"
        elif (source["datasource"] == "vectorstore"):
            print("---ROUTE QUESTION TO RAG---")
        source = self.question_router.invoke({"question": question})
        if source["datasource"] == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "websearch"
        else:
            print("---ROUTE QUESTION TO RAG---")
            return "vectorstore"

    def _batch_process_documents(self, documents: List[Document], batch_size: int = None) -> Generator:
        """Process documents in batches to reduce memory usage"""
        batch_size = batch_size or self.batch_size
        it = iter(documents)
        while batch := list(islice(it, batch_size)):
            yield batch
            gc.collect()  # Clean up after each batch

    def retrieve(self, state: Dict) -> Dict:
        try:
            print("---RETRIEVE---")
            question = state["question"]
            chat_id = state.get("chat_id")
            
            # Process documents in batches
            all_documents = []
            for doc_batch in self._batch_process_documents(self.retriever.invoke(question)):
                all_documents.extend(doc_batch)
                gc.collect()  # Clean up after each batch
            
            return {"documents": all_documents, "question": question, "chat_id": chat_id}
        finally:
            gc.collect()

    def generate(self, state: Dict) -> Dict:
        print("---GENERATE---")
        question = state["question"]
        chat_id = state.get("chat_id")
        documents = state["documents"]
        print(documents)
        metadata = [doc.metadata for doc in documents]
        print(f"Metadata: {metadata}")
        urls = blob.get_blob_urls([doc.metadata['file_name'] for doc in documents if 'file_name' in doc.metadata])
        print(f"URLs: {urls}")
        memory_vars = self.memory.load_memory_variables(chat_id, {"input": question})
        history_str = ""
        if ("chat_history" in memory_vars):
            history = memory_vars["chat_history"]
            history_str = "\n".join([f"Human: {h.content}" if h.type == "human" else f"Assistant: {h.content}" 
                                   for h in history[-3:]])  # Only keep last 3 exchanges
        context_list = [doc.page_content for doc in documents]
        truncated_context = self._truncate_context(context_list)
        
        # Generate response with truncated context
        generation = self.rag_chain.invoke({
            "context": truncated_context,
            "question": question,
            "chat_history": history_str
        })
        self.memory.save_context(chat_id, {"input": question}, {"output": generation})
        references = []
        try:
            pinecone_files = [doc.metadata['file_name'] for doc in documents[:len(truncated_context)]
                            if hasattr(doc, 'metadata') and 'file_name' in doc.metadata]
            if (pinecone_files):
                filtered_metadata = blob.get_blob_urls(pinecone_files)
                if (filtered_metadata):
                    references.extend([f"Document: {url}" for url in filtered_metadata])
        except Exception as e:
            print(f"Error processing Pinecone metadata: {e}")
        
        # Get web search references (limited to used context)
        web_references = [f"Web: {doc.metadata['source']}" for doc in documents[:len(truncated_context)]
                        if (hasattr(doc, 'metadata') and doc.metadata.get('is_web'))]
        if (web_references):
            references.extend(web_references)
        
        # Add references to final answer
        if (references):
            final_answer = f"{generation}\n\nReferences:\n" + "\n".join(references)
        else:
            final_answer = generation
            
        return {
            "documents": documents,
            "question": question,
            "generation": final_answer,
            "chat_id": chat_id
        }

    def _truncate_context(self, context_list, max_tokens=6000):
        """Memory-efficient context truncation"""
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained("gpt2")
            
            total_tokens = 0
            truncated_context = []
            
            # Process contexts in batches
            for ctx_batch in self._batch_process_documents(context_list, batch_size=10):
                for ctx in ctx_batch:
                    tokens = tokenizer.encode(ctx, truncation=True, max_length=512)
                    if total_tokens + len(tokens) > max_tokens:
                        return "\n".join(truncated_context)
                    truncated_context.append(ctx)
                    total_tokens += len(tokens)
                gc.collect()
            
            return "\n".join(truncated_context)
        finally:
            del tokenizer
            gc.collect()

    def grade_documents(self, state: Dict) -> Dict:
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]
        chat_id = state.get("chat_id")
        filtered_docs = []
        web_search = "No"
        for d in (documents):
            score = self.retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score["score"]
            if (grade.lower() == "yes"):
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
                web_search = "Yes"
                continue
        return {
            "documents": filtered_docs,
            "question": question,
            "web_search": web_search,
            "chat_id": chat_id
        }

    def web_search(self, state: Dict) -> Dict:
        try:
            print("---WEB SEARCH---")
            question = state["question"]
            chat_id = state.get("chat_id")  # Add retrieval of chat_id
            documents = state.get("documents", [])
            
            # Get chat history from memory
            memory_vars = self.memory.load_memory_variables(chat_id, {"input": question})  # Include chat_id
            chat_history = memory_vars.get("chat_history", [])
            
            # Create a contextualized search query with Pakistani law focus
            context_prompt = f"""
            Given the following chat history and current question, create a focused search query 
            Given the following chat history and current question, create a focused search query 
            specifically about Pakistani law and legal system. Always include "Pakistan law" or 
            "Pakistani legal system" in the query:
            
            Chat History:
            {chat_history}
            
            Current Question: {question}
            
            Create a search query that specifically focuses on Pakistani law context.
            Search Query:"""
            
            contextualized_query = self.llm.invoke(context_prompt).content.strip()
            if (not any(term in contextualized_query.lower() for term in ["pakistan", "pakistani"])):
                contextualized_query = f"Pakistani law {contextualized_query}"
            
            # Perform web search with contextualized query
            docs = self.web_search_tool.invoke({"query": contextualized_query})

            if (isinstance(docs, str) and docs.strip()):
                try:
                    docs = json.loads(docs)
                except json.JSONDecodeError:
                    print("Failed to decode JSON from docs")
                    docs = []

            # Filter and enhance documents for Pakistani law context
            processed_docs = []
            for doc_batch in self._batch_process_documents(docs, batch_size=5):
                for d in doc_batch:
                    context_verification_prompt = f"""
                    Verify if the following content is relevant to Pakistani law. If it is, enhance it with Pakistani legal context.
                    If it's not relevant to Pakistani law, return an empty string.
                    
                    Content: {d['content']}
                    """
                    
                    enhanced_content = self.llm.invoke(context_verification_prompt).content.strip()
                    
                    if (enhanced_content and enhanced_content != ""):
                        web_doc = Document(
                            page_content=f"""
                            Context: This information is about Pakistani law regarding {question}
                            
                            {enhanced_content}
                            """,
                            metadata={
                                "source": d.get("url", "No URL available"),
                                "title": d.get("title", "No title available"),
                                "is_web": True,
                                "context_query": contextualized_query,
                                "jurisdiction": "Pakistan"
                            }
                        )
                        processed_docs.append(web_doc)
                gc.collect()  # Clean up after each batch

            if (documents is not None):
                documents.extend(processed_docs)
            else:
                documents = processed_docs

            return {"documents": documents, "question": question, "chat_id": chat_id}
        finally:
            gc.collect()

    def decide_to_generate(self, state: Dict) -> str:
        print("---ASSESS GRADED DOCUMENTS---")
        web_search = state.get("web_search", "No")
        chat_id = state.get("chat_id")  # Ensure chat_id is retrieved
        
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
        chat_id = state.get("chat_id")
        
        try:
            truncated_docs = self._truncate_documents_for_model(documents)
            
            score = self.hallucination_grader.invoke(
                {"documents": truncated_docs, "generation": generation}
            )
            grade = score["score"]
            if (grade == "yes"):
                print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
                score = self.answer_grader.invoke(
                    {"question": question, "generation": generation}
                )
                grade = score["score"]
                if (grade == "yes"):
                    print("---DECISION: GENERATION ADDRESSES QUESTION---")
                    return "useful"
                else:
                    print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                    return "not useful"
            else:
                pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
                return "not supported"
        except Exception as e:
            print(f"Error in hallucination check: {str(e)}")
            return "useful"

    def build_workflow(self):
        workflow = StateGraph(state_schema=GraphState)
        workflow.add_node("websearch", self.web_search)
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("generate", self.generate)
        workflow.add_node("end", lambda x: {"question": x["question"], "generation": "I'm not able to answer this question as I only handle legal queries.", "documents": []})
        workflow.set_conditional_entry_point(
            self.route_question,
            {
                "websearch": "websearch",
                "vectorstore": "retrieve",
                "end": "end"  # Add end route for non-legal queries
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

    def run(self, question: str, chat_id: str):
        try:
            if chat_id:
                # Initialize chat history
                chat_history = AzureTableChatMessageHistory(
                    chat_id=chat_id,
                    connection_string=self.connection_string
                )
                
                # Add user question to history
                chat_history.add_message(HumanMessage(content=question))
            
            # Perform sentiment analysis on the question
            sentiment = self.analyze_sentiment(question)
            print(f"Sentiment: {sentiment}")
            
            # Recommend a lawyer based on the sentiment category
            recommendation = recommend_lawyer.recommend_lawyer(sentiment)
            print(recommendation)
            # breakpoint()
            # Continue with the existing workflow
            app = self.build_workflow()
            inputs = {"question": question}
            last_output = None
            for output in app.stream(inputs):
                for key, value in output.items():
                    pprint(f"Finished running: {key}:")
                    print("Output:")
                    pprint(value)
                    last_output = value
                gc.collect()  # Collect garbage after each iteration
            
            result = last_output["generation"]
            
            if chat_id:
                # Add AI response to history
                chat_history.add_message(AIMessage(content=result))
            
            gc.collect()
            return result
        
        finally:
            gc.collect()
            self.clear_memory_intensive_objects()

    def clear_session_memory(self, chat_id: str):
        self.memory.clear_memory(chat_id)

    def _truncate_documents_for_model(self, documents: List[Document], max_tokens: int = 4000) -> str:
        """Truncate documents to fit within model token limit"""
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        
        truncated_content = []
        total_tokens = 0
        
        for doc in documents:
            content = doc.page_content
            tokens = tokenizer.encode(content)
            if total_tokens + len(tokens) <= max_tokens:
                truncated_content.append(content)
                total_tokens += len(tokens)
            else:
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 0:
                    partial_content = tokenizer.decode(tokens[:remaining_tokens])
                    truncated_content.append(partial_content)
                break
        
        return "\n\n---\n\n".join(truncated_content)

    def _get_session_embedding(self, context: dict) -> List[float]:
        """Generate embedding for session data"""
        try:
            # Create a meaningful text representation of session activity
            session_items = []
            if context.get('context'):
                session_items.append(f"Context: {str(context['context'])}")
            if context.get('question_count'):
                session_items.append(f"Questions: {context['question_count']}")
            if context.get('last_accessed'):
                session_items.append(f"Last active: {context['last_accessed']}")
            
            session_text = " | ".join(session_items)
            if not session_text:
                session_text = "Empty session"
            
            # Get raw embedding
            raw_embedding = self.embeddings.embed_query(session_text)
            
            # Normalize the embedding vector
            import numpy as np
            norm = np.linalg.norm(raw_embedding)
            if norm == 0:
                # If normalization fails, create a random unit vector
                vec = np.random.randn(1024)  # Match dimension with index
                return (vec / np.linalg.norm(vec)).tolist()
            
            # Use numpy's memory-efficient operations
            embedding = np.array(raw_embedding, dtype=np.float32)  # Use float32 instead of float64
            norm = np.linalg.norm(embedding)
            if norm == 0:
                vec = np.random.randn(1024).astype(np.float32)
                return (vec / np.linalg.norm(vec)).tolist()
            
            normalized = (embedding / norm).tolist()
            return normalized
        finally:
            del embedding
            gc.collect()

    def store_session(self, chat_id: str, context: dict):
        """Store session data in vector store"""
        try:
            if self.session_index is None:
                print(f"Session {chat_id} stored in memory only")
                return
                
            # Prepare context data
            context_copy = context.copy()
            for key in ['created_at', 'last_accessed', 'expiry']:
                if isinstance(context_copy.get(key), datetime):
                    context_copy[key] = context_copy[key].isoformat()
            
            # Get normalized embedding vector
            vector = self._get_session_embedding(context_copy)
            
            context_str = json.dumps(context_copy)
            self.session_index.upsert(
                vectors=[{
                    'id': chat_id,
                    'values': vector,
                    'metadata': {
                        'session_data': context_str,
                        'last_accessed': str(datetime.now())
                    }
                }]
            )
            print(f"Session {chat_id} stored successfully")
        except Exception as e:
            print(f"Error storing session: {e}")

    def load_session(self, chat_id: str) -> dict:
        """Load session data from vector store"""
        try:
            # First try direct fetch
            result = self.session_index.fetch([chat_id])
            if result and result.get('vectors', {}).get(chat_id):
                return self._parse_session_data(result['vectors'][chat_id]['metadata']['session_data'])
                
            # Try query as fallback
            query_vector = self._get_session_embedding({'id': chat_id})
            query_result = self.session_index.query(
                vector=query_vector,
                filter={"id": chat_id},
                top_k=1,
                include_metadata=True
            )
            
            if query_result and query_result.matches:
                return self._parse_session_data(query_result.matches[0].metadata['session_data'])
                
            return None
        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    def _parse_session_data(self, session_data_str: str) -> dict:
        """Parse session data and convert datetime strings to datetime objects"""
        try:
            data = json.loads(session_data_str)
            for field in ['created_at', 'last_accessed', 'expiry']:
                if isinstance(data.get(field), str):
                    data[field] = datetime.fromisoformat(data[field])
            return data
        except Exception as e:
            print(f"Error parsing session data: {e}")
            return None

    def delete_session(self, chat_id: str):
        """Delete session data from vector store"""
        try:
            self.session_index.delete(ids=[chat_id])
            print(f"Session {chat_id} deleted successfully")
        except Exception as e:
            print(f"Error deleting session: {e}")

    def clear_memory_intensive_objects(self):
        """Clear memory-intensive objects when they're no longer needed"""
        if hasattr(self, '_temp_documents'):
            del self._temp_documents
        if hasattr(self, '_temp_embeddings'):
            del self._temp_embeddings
        gc.collect()

if __name__ == "__main__":
    agent = RAGAgent()    
    agent.run("Which types of proceedings are excluded from the application of this Act as per Section", chat_id="1230")

