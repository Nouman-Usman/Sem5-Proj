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
from langchain.memory import ConversationBufferWindowMemory
import datetime
import pyodbc
# from langchain_core.pydantic_v1 import BaseModel, Field
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
        gc.collect()
        self.max_context_length = 4096
        self.memory = ConversationBufferWindowMemory(k=5)
        self.chats_loaded = False

    def analyze_sentiment(self, question: str) -> str:
        """Analyze sentiment with proper input validation and prompt handling"""
        print("---SENTIMENT ANALYSIS---")
        prompt_template = """You are a legal assistant analyzing the sentiment of text.
            Analyze the following text and categorize it into exactly one of these categories:
            Civil, Criminal, Corporate, Constitutional, Tax, Family, Intellectual Property, 
            Labor and Employment, Immigration, Commercial, Environmental, Banking and Finance,
            Cyber Law, Alternate Dispute Resolution (ADR)

            Text: {text}

            Return only the category name without any additional text."""

            # Format prompt with actual text
        prompt = prompt_template.format(text=question)

            # Make LLM call with proper string input
        sentiment_result = self.llm.invoke(prompt)
        return sentiment_result.content
            # Extract and clean response
        # response = sentiment_result.content.strip()
        # print(f"Sentiment analysis response: {response}")
        #     # Handle tool call format if present
        # if "<tool_call>" in response:
        #         try:
        #             parsed = self._safe_parse_json(response)
        #             if parsed and "arguments" in parsed:
        #                 if "category" in parsed["arguments"]:
        #                     response = parsed["arguments"]["category"]
        #         except Exception:
        #             pass

        #     # Validate against known categories
        # valid_categories = {
        #         "Civil", "Criminal", "Corporate", "Constitutional", "Tax",
        #         "Family", "Intellectual Property", "Labor and Employment",
        #         "Immigration", "Commercial", "Environmental", "Banking and Finance",
        #         "Cyber Law", "Alternate Dispute Resolution"
        #     }

        # response = response.strip()
        # if response in valid_categories:
        #         return response

        #     # Default to most relevant category if not exact match
        # return self._find_closest_category(response, valid_categories)

        # except Exception as e:
        #     logging.error(f"Sentiment analysis error: {e}")
        #     return "Civil"  # Default category on error

    def _find_closest_category(self, text: str, categories: set) -> str:
        """Find closest matching legal category"""
        text = text.lower()
        
        # Direct matches for common variations
        category_variations = {
            "civil law": "Civil",
            "criminal law": "Criminal",
            "corporate law": "Corporate",
            "family law": "Family",
            "tax law": "Tax",
            "ip law": "Intellectual Property",
            "employment law": "Labor and Employment",
            "labor law": "Labor and Employment",
            "immigration law": "Immigration",
            "business law": "Commercial",
            "environmental law": "Environmental",
            "banking law": "Banking and Finance",
            "cyber law": "Cyber Law",
            "cybersecurity": "Cyber Law",
            "adr": "Alternate Dispute Resolution",
            "mediation": "Alternate Dispute Resolution",
            "arbitration": "Alternate Dispute Resolution"
        }

        # Check for exact matches in variations
        if text in category_variations:
            return category_variations[text]

        # Find best partial match
        max_score = 0
        best_match = "Civil"  # Default category
        
        for category in categories:
            # Calculate word overlap score
            category_words = set(category.lower().split())
            text_words = set(text.split())
            common_words = category_words & text_words
            
            # Weight longer matches more heavily
            score = len(common_words) / max(len(category_words), len(text_words))
            
            if score > max_score:
                max_score = score
                best_match = category

        return best_match

    def _initialize_vectorstore(self):
        embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
        self.vectorstore = PineconeVectorStore(index=self.index, embedding=embeddings)
        # self.vectorstore.add_documents(doc_splits)
        self.retriever = self.vectorstore.as_retriever()
        print("Vectorstore initialized and documents added.")

    def _initialize_prompts(self):
        self.retrieval_grader_prompt = PromptTemplate(
            template="""You are a legal document relevance validator.
Determine if a document contains information relevant to a given question.

You must respond with ONLY a JSON object in this exact format (no other text):
{{"score": "yes"}} or {{"score": "no"}}

RELEVANCE CRITERIA:
1. The document contains information that directly or indirectly answers the question
2. The document discusses related legal concepts or procedures
3. The document references relevant laws, sections, or precedents

Document: {document}
Question: {question}""",
            input_variables=["question", "document"],
        )
        self.retrieval_grader = (
            self.retrieval_grader_prompt 
            | self.llm
            | JsonOutputParser()
        )
        
        self.generate_prompt = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a legal assistant for question-answering tasks in the context of Pakistani law. Structure your responses in Markdown format to aid in legal research. Bold the key terms like section or laws and use bullet points for lists. Provide a detailed response to the user's question.

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
            template="""You are evaluating if an answer is supported by given documents.
Return ONLY a JSON response in this exact format:
{{"score": "yes"}} - if the answer is supported
{{"score": "no"}} - if the answer is not supported

Documents: {documents}
Answer to evaluate: {generation}""",
            input_variables=["generation", "documents"],
        )
        self.hallucination_grader = (
            self.hallucination_grader_prompt | self.llm | JsonOutputParser()
        )

        self.answer_grader_prompt = PromptTemplate(
            template="""You are evaluating if an answer is useful for a question.
Return ONLY a JSON response in this exact format:
{{"score": "yes"}} - if the answer is useful
{{"score": "no"}} - if the answer is not useful

Question: {question}
Answer to evaluate: {generation}""",
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
        try:
            generation = self.rag_chain.invoke({
                "context": context,
                "question": question,
                "chat_history": chat_context
            })

            # Check if generation is an error message
            if any(phrase in generation.lower() for phrase in [
                "i apologize", "i'm sorry", "i do not have the capability",
                "cannot assist", "cannot help", "not able to"
            ]):
                # Try web search as fallback
                print("---DETECTED ERROR MESSAGE, TRYING WEB SEARCH---")
                web_results = self.web_search(state)
                if web_results["documents"]:
                    state["documents"] = web_results["documents"]
                    return self.generate(state)  # Retry with web results

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
        except Exception as e:
            logging.error(f"Generation error: {e}")
            return {
                "documents": documents,
                "question": question,
                "generation": "I apologize, but I encountered an error. Please try rephrasing your question.",
                "source": []
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

    def _safe_parse_json(self, text: str) -> dict:
        """Enhanced JSON parsing with better error handling"""
        try:
            # If input is already a dict, return it with proper score format
            if isinstance(text, dict):
                if "score" in text:
                    return {"score": str(text["score"]).lower()}
                return text

            # Handle tool call format
            if "<tool_call>" in text:
                # Extract JSON between first { and last }
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = text[start:end]
                    try:
                        data = json.loads(json_str)
                        # Handle tool call specific structure
                        if "arguments" in data:
                            args = data["arguments"]
                            # Look for different types of relevance indicators
                            if "score" in args:
                                return {"score": str(args["score"]).lower()}
                            if "document" in args and "userQuestion" in args:
                                # Assume relevance if properly formatted
                                return {"score": "yes"}
                        return {"score": "yes"}  # Default to yes if well-formed
                    except json.JSONDecodeError:
                        pass

            # Try parsing as regular JSON
            if text.startswith("{") and text.endswith("}"):
                data = json.loads(text)
                if "score" in data:
                    return {"score": str(data["score"]).lower()}

            # Handle plain text responses
            text_lower = text.lower().strip()
            if any(word in text_lower for word in ["yes", "relevant", "true"]):
                return {"score": "yes"}
            
            return {"score": "no"}

        except Exception as e:
            logging.error(f"JSON parsing error: {e}")
            return {"score": "no"}

    def _process_grader_response(self, response: Any) -> Dict[str, str]:
        """Helper to process and normalize grader responses"""
        if isinstance(response, dict) and "score" in response:
            return response
            
        if isinstance(response, str):
            # Handle tool call format
            if "<tool_call>" in response:
                try:
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(response[start:end])
                        if "arguments" in data:
                            return {"score": "yes"}  # Default to yes for tool calls
                except:
                    pass
            # Try direct JSON parsing
            try:
                if response.startswith("{") and response.endswith("}"):
                    data = json.loads(response)
                    if "score" in data:
                        return data
            except:
                pass
                
        return {"score": "no"}  # Default fallback

    def _handle_tool_call_response(self, response: str) -> Dict[str, str]:
        """Extract relevance score from tool call format"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                
                # Common tool call patterns
                if "arguments" in data:
                    args = data["arguments"]
                    if any(key in args for key in ["score", "isRelevant", "relevant"]):
                        return {"score": "yes"}
                    if "document" in args and "question" in args:
                        return {"score": "yes"}
                
                # Check for direct score in response
                if "score" in data:
                    return {"score": str(data["score"]).lower()}
                    
            return {"score": "no"}
        except:
            return {"score": "no"}

    def grade_documents(self, state: Dict) -> Dict:
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        print("State: ", state)
        breakpoint()
        question = state["question"]
        documents = state["documents"]
        filtered_docs = []
        web_search = "No"
        source = state["source"]
        
        # Check each document's relevance
        for d in documents:
            prompt_value = self.retrieval_grader_prompt.format(
                question=question,
                document=d.page_content
            )
            llm_response = self.llm.invoke(prompt_value)
            print(" Llm response: ", llm_response.content)
            try:
                parsed_json = json.loads(llm_response.content)
                if parsed_json.get("score") == "yes":
                    filtered_docs.append(d)
                else:
                    print("Document not relevant")
                    web_search = "Yes"  # Set to Yes if any document is not relevant
            except json.JSONDecodeError:
                web_search = "Yes"  # Set to Yes on parsing error
                continue

        # Return all state fields including web_search
        return {
            **state,  # Preserve all existing state
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
        print(f"Web search: {web_search}")
        breakpoint()
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
        attempts = state.get("attempts", 0)

        if attempts >= 2:
            return "useful"

        try:
            # Check hallucination
            prompt_value = self.hallucination_grader_prompt.format(
                documents=documents,
                generation=generation
            )
            llm_response = self.llm.invoke(prompt_value)
            try:
                parsed_json = json.loads(llm_response.content)
                if parsed_json.get("score") == "yes":
                    # Check usefulness
                    prompt_value = self.answer_grader_prompt.format(
                        question=question,
                        generation=generation
                    )
                    llm_response = self.llm.invoke(prompt_value)
                    parsed_json = json.loads(llm_response.content)
                    return "useful" if parsed_json.get("score") == "yes" else "not useful"
                return "not supported"
            except json.JSONDecodeError:
                return "not supported" if attempts < 2 else "useful"

        except Exception as e:
            logging.error(f"Generation grading error: {e}")
            return "not supported" if attempts < 2 else "useful"

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
            sentiment = self.analyze_sentiment(question=question)

            app = self.build_workflow()
            inputs = {
                "question": question,
                "documents": [],
                "source": [],
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

    def save_context(self, user_input: str, assistant_output: str):
        self.memory.save_context({"input": user_input}, {"output": assistant_output})

    def is_valid_uuid(self, uuid_str: str) -> bool:
        try:
            uuid.UUID(uuid_str)
            return True
        except (ValueError, AttributeError, TypeError):
            return False

if __name__ == "__main__":
    rag = RAGAgent()
    query = "What is the procedure for filing a lawsuit in Pakistan?"
    question = "Rape Cases in Pakistan"
    result = rag.run(question, [])
    print(result)
