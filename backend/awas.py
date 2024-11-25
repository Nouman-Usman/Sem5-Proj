from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnableConfig
from langchain_core.documents import Document
from main import RAGAgent
import time
import json
import numpy as np

agent = RAGAgent()
llm = ChatGroq(
    temperature=0,
    model="llama3-groq-70b-8192-tool-use-preview",
    max_tokens=2000
)

# Get dataset
dataset = agent.retrieve_dataset()
print(f"Retrieved {len(dataset)} documents")

if not dataset:
    raise ValueError("No documents were retrieved from the dataset")

def extract_number(text: str) -> float:
    """Extract the first number from text, handling various formats."""
    try:
        # Find first number in the text
        number = ''.join(c for c in text if c.isdigit() or c == '.')
        if number:
            return float(number)
        return 5.0  # Default score if no number found
    except:
        return 5.0  # Default score if conversion fails

def evaluate_rag(llm, documents, batch_size=3):
    """Simple RAG evaluation using only ChatGroq"""
    
    scores = {
        "relevance": [],
        "coherence": []
    }
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}/{len(documents)//batch_size + 1}")
        
        for doc in batch:
            try:
                # Generate a question from the document
                question_prompt = f"Generate a single question that can be answered from this text: {doc.page_content[:300]}"
                question = llm.invoke(question_prompt).content.strip()
                
                # Generate an answer
                answer_prompt = f"Answer this question based on the given context:\nContext: {doc.page_content[:500]}\nQuestion: {question}"
                answer = llm.invoke(answer_prompt).content.strip()
                
                # Evaluate relevance with stricter prompt
                relevance_prompt = f"""On a scale of 1-10, rate ONLY with a number how relevant the answer is to the question and context:
                Context: {doc.page_content[:500]}
                Question: {question}
                Answer: {answer}
                Output only a number between 1 and 10, nothing else.
                """
                relevance_score = extract_number(llm.invoke(relevance_prompt).content.strip())
                scores["relevance"].append(relevance_score / 10.0)
                
                # Evaluate coherence with stricter prompt
                coherence_prompt = f"""On a scale of 1-10, rate ONLY with a number how well-structured and coherent this answer is:
                Answer: {answer}
                Output only a number between 1 and 10, nothing else.
                """
                coherence_score = extract_number(llm.invoke(coherence_prompt).content.strip())
                scores["coherence"].append(coherence_score / 10.0)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing document: {e}")
                continue
        
        # Print batch results
        batch_results = {
            "relevance": np.mean(scores["relevance"][-batch_size:]),
            "coherence": np.mean(scores["coherence"][-batch_size:])
        }
        print(f"Batch results: {batch_results}")
        time.sleep(3)
    
    # Calculate final scores
    final_scores = {
        metric: np.mean(scores[metric])
        for metric in scores.keys()
    }
    
    return final_scores

try:
    results = evaluate_rag(llm, dataset)
    print("\nFinal Evaluation Results:")
    print(json.dumps(results, indent=2))
    
except Exception as e:
    print(f"Error during evaluation: {e}")
    raise