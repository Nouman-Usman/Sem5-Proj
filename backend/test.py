import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
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
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory
from langchain_core.vectorstores import VectorStoreRetriever
load_dotenv()


class CombinedMemory:
    def __init__(self, vectorstore: PineconeVectorStore):
        self.buffer_memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="input",
            return_messages=True
        )
        self.vector_memory = VectorStoreRetrieverMemory(
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory_key="relevant_history",
            input_key="input"
        )

    def save_context(self, inputs, outputs):
        # Ensure inputs has the required key
        if "input" not in inputs and len(inputs) > 0:
            # Use the first available key as input if "input" is not present
            first_key = next(iter(inputs))
            inputs = {"input": inputs[first_key]}
        self.buffer_memory.save_context(inputs, outputs)
        self.vector_memory.save_context(inputs, outputs)

    def load_memory_variables(self, inputs):
        # Ensure inputs has the required key
        if not inputs:
            inputs = {"input": ""}
        buffer_vars = self.buffer_memory.load_memory_variables(inputs)
        vector_vars = self.vector_memory.load_memory_variables(inputs)
        return {**buffer_vars, **vector_vars}


class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[Document]


class RAGAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("PINECONE_API")
        self.legal_index_name = "apna-waqeel"
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
        self._initialize_vectorstore()  # This will now properly initialize memory
        self._initialize_prompts()

    def _initialize_vectorstore(self):
        embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
        self.vectorstore = PineconeVectorStore(index=self.index, embedding=embeddings)
        self.retriever = self.vectorstore.as_retriever()
        # Initialize memory after vectorstore is created
        self.memory = CombinedMemory(self.vectorstore)
        print("Vectorstore initialized and memory created.")

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
        print(f"Sentiment: {sentiment}")
        return sentiment

    def answer_question(self, question: str) -> str:
        print("---ANSWERING QUESTION---")
        sentiment = self.analyze_sentiment(question)
        print(f"Sentiment: {sentiment}")
        lawyer_recommendation = self._recommend_lawyer(sentiment)
        print(f"Lawyer Recommendation: {lawyer_recommendation}")

        # Retrieve relevant documents
        relevant_docs = self.retriever.get_relevant_documents(question)
        print(f"Number of relevant documents: {len(relevant_docs)}")

        # Perform web search
        web_search_results = self.web_search_tool.run(question)
        print(f"Web search results: {web_search_results}")

        # Load memory variables
        memory_variables = self.memory.load_memory_variables({"input": question})
        chat_history = memory_variables.get("chat_history", [])
        relevant_history = memory_variables.get("relevant_history", "")

        # Combine all information
        context = "\n".join([doc.page_content for doc in relevant_docs])
        web_context = "\n".join([result['content'] for result in web_search_results])

        # Generate answer
        prompt = self.qa_prompt.format(
            question=question,
            context=context,
            web_context=web_context,
            lawyer_recommendation=lawyer_recommendation,
            chat_history=chat_history,
            relevant_history=relevant_history
        )
        response = self.llm.invoke(prompt)
        print(f"Generated response: {response.content}")

        # Save context
        self.memory.save_context({"input": question}, {"output": response.content})

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

    def retrieve(self, state: Dict) -> Dict:
        print("---RETRIEVE---")
        question = state["question"]
        documents = self.retriever.invoke(question)
        return {"documents": documents, "question": question}

    def generate(self, state: Dict) -> Dict:
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]
        
        # Debug print for documents and metadata
        print("Documents received:", len(documents))
        for doc in documents:
            print("Document metadata:", doc.metadata if hasattr(doc, 'metadata') else "No metadata")
        
        # Get chat history from memory with proper input
        memory_vars = self.memory.load_memory_variables({"input": question})
        history_str = ""
        if "chat_history" in memory_vars:
            history = memory_vars["chat_history"]
            history_str = "\n".join([f"Human: {h.content}" if h.type == "human" else f"Assistant: {h.content}" 
                                   for h in history])
        
        # Rest of your existing generate prompt code...
        # ...existing code...
        
        generation = self.rag_chain.invoke({
            "context": [doc.page_content for doc in documents], 
            "question": question,
            "chat_history": history_str
        })
        
        # Save the interaction to memory
        self.memory.save_context(
            {"input": question},
            {"output": generation}
        )
        
        # Extract metadata and create references
        try:
            metadata_files = []
            for doc in documents:
                if hasattr(doc, 'metadata') and 'file_name' in doc.metadata:
                    metadata_files.append(doc.metadata['file_name'])
            
            if metadata_files:
                print("Found metadata files:", metadata_files)
                filtered_metadata = blob.get_blob_urls(metadata_files)
                if filtered_metadata:
                    final_answer = f"{generation}\nReferences:\n" + "\n".join(filtered_metadata)
                else:
                    final_answer = generation
            else:
                print("No metadata files found in documents")
                final_answer = generation
                
        except Exception as e:
            print(f"Error processing metadata: {e}")
            final_answer = generation
            
        print("Final answer with references:", final_answer)
        return {
            "documents": documents,
            "question": question,
            "generation": final_answer,
        }

    def grade_documents(self, state: Dict) -> Dict:
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]
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
            # "metadata": filtered_metadata,
            "question": question,
            "web_search": web_search,
        }

    def web_search(self, state: Dict) -> Dict:
        print("---WEB SEARCH---")
        question = state["question"]
        documents = state.get("documents", [])
        # metadata = state.get("metadata", [])
        docs = self.web_search_tool.invoke({"query": question})

        if isinstance(docs, str) and docs.strip():
            try:
                docs = json.loads(docs)
            except json.JSONDecodeError:
                print("Failed to decode JSON from docs")
                docs = []

        web_results = "\n".join([d["content"] for d in docs])
        web_results = Document(page_content=web_results)

        if documents is not None:
            documents.append(web_results)
            # metadata.append({})
        else:
            documents = [web_results]
            # metadata = [{}]

        return {"documents": documents, "question": question}

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

    def run(self, question: str):
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
                # print("Output:")
                # pprint(value)
                last_output = value
        pprint(last_output["generation"])    
        # return last_output["generation"]


if __name__ == "__main__":
    agent = RAGAgent()
agent.run("Which types of proceedings are excluded from the application of this Act as per Section 3?")
print("Now In Context")
agent.run("Explain In detail")  # This will now understand the context of the previous question
    # while True:
    #     agent.run(input("What is your legal query: "))
