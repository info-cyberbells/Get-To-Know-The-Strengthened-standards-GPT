import os
import asyncio
import pytest
from dotenv import load_dotenv
from openai import AsyncOpenAI
from backend.query_handler import QueryHandler
from backend.document_processor import DocumentProcessor
from backend.vector_store import InMemoryVectorStore

# Test queries for each workflow
WORKFLOW_1_QUERIES = [
    "What are the key requirements of Standard 1?",
    "How does Standard 1 address consumer dignity and choice?",
    "What are the main changes in the Strengthened Standards?"
]

WORKFLOW_2_QUERIES = [
    "How does our complaints policy align with Standard 1?",
    "Compare our policies with the Standards requirements.",
    "What improvements should we make to better meet the Standards?"
]

@pytest.mark.asyncio
async def test_chatbot_interaction():
    """Test real chatbot interactions with both workflows"""
    
    # Setup
    load_dotenv()
    document_processor = DocumentProcessor()
    vector_store = InMemoryVectorStore()
    query_handler = QueryHandler(vector_store, document_processor)
    client = AsyncOpenAI()
    
    # Create a thread
    thread = await client.beta.threads.create()
    thread_id = thread.id
    assistant_id = os.getenv('ASSISTANT_ID')
    
    try:
        # Test Workflow 1: Direct Standards Queries
        print("\n=== Testing Workflow 1: Direct Standards Queries ===")
        for query in WORKFLOW_1_QUERIES:
            print(f"\nQuery: {query}")
            response = await query_handler.process_query(
                query=query,
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            print(f"Response: {response['response']}\n")
            
        # Process test documents for Workflow 2
        test_files = [
            "data/BRV-ComplaintsHandlingPolicy.pdf",
            "data/EAC - Complaints Policy.pdf"
        ]
        
        for file_path in test_files:
            print(f"\nProcessing document: {file_path}")
            await query_handler.process_file(file_path, os.path.basename(file_path))
            
        # Test Workflow 2: Document-Aware Queries
        print("\n=== Testing Workflow 2: Document-Aware Queries ===")
        for query in WORKFLOW_2_QUERIES:
            print(f"\nQuery: {query}")
            response = await query_handler.process_query(
                query=query,
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            print(f"Response: {response['response']}\n")
            if response['relevant_chunks']:
                print("Relevant document sections:")
                for chunk in response['relevant_chunks'][:2]:  # Show first 2 chunks
                    print(f"- From {chunk['metadata']['file_path']}:")
                    print(f"  {chunk['chunk'][:200]}...")  # First 200 chars
            
    finally:
        # Cleanup
        if thread_id:
            await client.beta.threads.delete(thread_id)

if __name__ == "__main__":
    asyncio.run(test_chatbot_interaction()) 