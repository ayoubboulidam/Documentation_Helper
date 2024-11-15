import os  # Provides functions to interact with the operating system

from dotenv import load_dotenv  # Loads environment variables from a .env file

load_dotenv()  # Load environment variables into the application

from langchain.text_splitter import RecursiveCharacterTextSplitter  # Imports a tool for splitting text into chunks
from langchain_community.document_loaders import ReadTheDocsLoader  # Imports a loader to read documentation from Read the Docs
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # Imports Google embeddings
from langchain_pinecone import PineconeVectorStore  # Imports the Pinecone vector store for storage and retrieval

# Specify the embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")  # Retrieves the Google API key from environment variables
)

def ingest_docs():
    # Initialize the document loader with the path to documentation
    loader = ReadTheDocsLoader(
        "C:\\Users\\pc\\Desktop\\Documentation_Helper\\langchain-docs\\api.python.langchain.com\\en\\latest",
        encoding="utf-8"  # Use UTF-8 encoding to avoid character decoding issues
    )

    # Load raw documents from the specified source
    raw_documents = loader.load()
    print(f"loaded {len(raw_documents)} documents")

    # Split the documents into smaller, manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    documents = text_splitter.split_documents(raw_documents)

    # Update the metadata in each document to use full URLs
    for doc in documents:
        new_url = doc.metadata["source"]
        new_url = new_url.replace("langchain-docs", "https:/")  # Update the URL to full path
        doc.metadata.update({"source": new_url})

    print(f"Going to add {len(documents)} to Pinecone")

    # Add the documents to Pinecone's vector store
    PineconeVectorStore.from_documents(
        documents, embeddings, index_name=os.environ["INDEX_NAME"]  # Specify the index name from environment variables
    )
    print("****Loading to vectorstore done ***")

# Execute the ingest_docs function if this script is run directly
if __name__ == "__main__":
    ingest_docs()
