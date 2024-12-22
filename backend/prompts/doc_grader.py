from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.output_parsers import CommaSeparatedListOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv
import os
import json
load_dotenv()

class RelevanceScore(BaseModel):
    score: Literal["yes", "no"] = Field(description="Relevance score of the document")

retrieval_grader_prompt = PromptTemplate(
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
    input_variables=["question", "document"]
)

llm = ChatGroq(temperature=0, model="llama3-groq-70b-8192-tool-use-preview")

# print(llm.invoke("Hello, world!"))
# print("Hello, world!")
def grade_document(question: str, document: str) -> RelevanceScore:
    response = retrieval_grader_prompt | llm | CommaSeparatedListOutputParser()
    # return None
    # return response.invoke(question=question, document=document)
    try:
        prompt_value = retrieval_grader_prompt.format(
            question=question,
            document=document
        )

        llm_response = llm.invoke(prompt_value)
        print(llm_response.content)
        breakpoint()
        parsed_json = json.loads(llm_response.content)

        return RelevanceScore(**parsed_json)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return RelevanceScore(score="no")
    except Exception as e:
        print(f"Error processing response: {e}")
        return RelevanceScore(score="no")

# Test the function
test_result = grade_document(
    "What is the legal drinking age in the US?", 
    "The legal drinking age in the US is 21 years old."
)
print(test_result)
