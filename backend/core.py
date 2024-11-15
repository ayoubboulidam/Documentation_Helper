import os  # Used for accessing environment variables

from dotenv import load_dotenv  # Loads environment variables from a .env file
from langchain.chains.retrieval import create_retrieval_chain  # Creates a retrieval-based chain for answering questions

load_dotenv()  # Load environment variables from the .env file

from langchain import hub  # Provides access to pre-built LangChain components
from langchain.chains.combine_documents import \
    create_stuff_documents_chain  # Combines multiple documents into one chain
from langchain_pinecone import PineconeVectorStore  # Manages the Pinecone vector database for document retrieval

from langchain_google_genai import GoogleGenerativeAIEmbeddings, \
    ChatGoogleGenerativeAI  # Google embeddings and chat model


# Function to query the LLM with a given input
def run_llm(query: str):
    # Initialize the embedding model for vector search
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GOOGLE_API_KEY")  # Retrieve API key from environment variables
    )

    # Connect to the Pinecone vector store
    docsearch = PineconeVectorStore(
        index_name=os.environ["INDEX_NAME"],  # Retrieve the index name from environment variables
        embedding=embeddings  # Use the embeddings for document vectorization
    )

    # Set up the Google chat model for response generation
    chat = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        temperature=0  # Lower temperature for more deterministic responses
    )

    # Load a pre-built retrieval-qa-chat prompt from LangChain's hub
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    # Combine documents into a single chain using the chat model and prompt
    stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

    # Create the final retrieval-based chain
    qa = create_retrieval_chain(
        retriever=docsearch.as_retriever(),  # Use the Pinecone retriever for fetching relevant documents
        combine_docs_chain=stuff_documents_chain  # Combine documents with the chat chain
    )

    # Invoke the chain with the input query and return the result
    result = qa.invoke(input={"input": query})

    # Format the result into a dictionary
    new_result = {
        "query": result["input"],  # The input query
        "result": result["answer"],  # The generated answer
        "source_documents": result["context"],  # The context documents used
    }

    return new_result


# Run the function and print the result when executed directly
if __name__ == "__main__":
    res = run_llm(query="What is a LangChain Chain?")  # Query about LangChain
    print(res["result"])  # Print the answer
