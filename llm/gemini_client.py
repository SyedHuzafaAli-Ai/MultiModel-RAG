from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)

# Prompt Template
prompt = PromptTemplate(
    input_variables=["context", "question", "conversation"],
    template="""
You are a helpful AI assistant.

Use the conversation history and provided context to answer the user's question.

If the answer is not in the context, say:
"I don't know based on the provided documents."

Conversation History:
{conversation}

Context:
{context}

Question:
{question}
"""
)

# Create Chain
chain = prompt | llm


# Generate Response Function
def generate_response(query, chunks, conversation=""):

    # Build formatted context
    context = ""

    for chunk in chunks:
        context += f"""
Source: {chunk['source']}
Page: {chunk['page']}

Content:
{chunk['text']}

"""

    # Invoke LLM
    response = chain.invoke({
        "context": context,
        "question": query,
        "conversation": conversation
    })

    return response.content