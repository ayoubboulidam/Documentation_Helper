import os
from dotenv import load_dotenv
from typing import Any, Dict, List

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()

def run_llm(query: str, chat_history: List[Dict[str, Any]] = []) -> Dict[str, Any]:
    """
    Runs the LLM chain with memory and returns the result.
    Args:
        query (str): User query.
        chat_history (List[Dict[str, Any]]): The ongoing chat history.
    Returns:
        Dict[str, Any]: Formatted response including the result and sources.
    """
    # Initialize embeddings and vector store
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    docsearch = PineconeVectorStore(
        index_name=os.getenv("INDEX_NAME"),
        embedding=embeddings
    )

    # Configure the chat model
    chat = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        temperature=0
    )

    # Load prompts
    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    # Create chains
    stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)
    history_aware_retriever = create_history_aware_retriever(
        llm=chat,
        retriever=docsearch.as_retriever(),
        prompt=rephrase_prompt
    )
    qa_chain = create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=stuff_documents_chain
    )

    # Execute the chain
    result = qa_chain.invoke(input={"input": query, "chat_history": chat_history})

    # Format and return the result
    return {
        "query": result["input"],
        "result": result["answer"],
        "source_documents": result["context"]
    }
