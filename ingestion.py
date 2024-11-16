import os  # Provides functions to interact with the operating system
from dotenv import load_dotenv  # Loads environment variables from a .env file

# Load environment variables into the application
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings  # Imports Google embeddings
from langchain_pinecone import PineconeVectorStore  # Imports the Pinecone vector store for storage and retrieval
from langchain_community.document_loaders import FireCrawlLoader  # Import FireCrawlLoader

# Specify the embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")  # Retrieves the Google API key from environment variables
)

def ingest_docs2() -> None:
    # Docker documentation URLs to be crawled
    docker_documents_base_urls = [
        "https://www.docker.com/blog/november-2024-updated-plans-announcement/",
        "https://docs.docker.com/get-started/get-docker/",
        "https://docs.docker.com/guides/",
        "https://docs.docker.com/manuals/",
        "https://docs.docker.com/reference/",
        "https://docs.docker.com/get-started/",
        "https://docker.qualtrics.com/jfe/form/SV_3IDfGscnmh99ex8",
        "https://docs.docker.com/tags/admin/",
        "https://docs.docker.com/tags/ai/",
        "https://docs.docker.com/tags/app-dev/",
        "https://docs.docker.com/tags/best-practices/",
        "https://docs.docker.com/tags/cloud-services/",
        "https://docs.docker.com/tags/data-science/",
        "https://docs.docker.com/tags/databases/",
        "https://docs.docker.com/tags/deploy/",
        "https://docs.docker.com/tags/devops/",
        "https://docs.docker.com/tags/distributed-systems/",
        "https://docs.docker.com/tags/faq/",
        "https://docs.docker.com/tags/networking/",
        "https://docs.docker.com/tags/product-demo/",
        "https://docs.docker.com/tags/release-notes/",
        "https://docs.docker.com/tags/secrets/",
        "https://docs.docker.com/tags/troubleshooting/",
        "https://forums.docker.com/",
        "https://dockr.ly/comm-slack",
        "https://www.docker.com/community/captains/",
        "https://cookiepedia.co.uk/giving-consent-to-cookies",
        "https://www.onetrust.com/products/cookie-consent/",
    ]

    # No need to split the URL list manually, FireCrawl handles the job efficiently.
    # FireCrawl is capable of parsing and processing URLs as needed, so we can skip manual splitting or additional URL handling.

    for url in docker_documents_base_urls:
        print(f"FireCrawl: {url}")

        # Initialize the FireCrawlLoader with valid parameters:
        # Removed 'crawlerOptions' and 'wait_until_done' as they were causing errors.
        loader = FireCrawlLoader(
            url=url,
            mode="crawl",  # Specifies the mode as crawl to fetch the page content.
            params={
                "pageOptions": {"onlyMainContent": True},  # Ensures that only the main content is crawled

            },
        )

        # Load the documents from the crawled pages
        docs = loader.load()

        # Log how many documents were retrieved
        print(f"Going to add {len(docs)} to Pinecone")

        # Store the documents in Pinecone vector store, using embeddings for indexing
        PineconeVectorStore.from_documents(
            docs, embeddings, index_name=os.environ["INDEX_DOCKER"]
        )

        # Confirm the loading process to Pinecone is complete
        print("****Loading to vectorstore done ***")


if __name__ == "__main__":
    ingest_docs2()
