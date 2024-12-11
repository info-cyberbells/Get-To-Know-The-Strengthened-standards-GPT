import os
import asyncio
import pytest
from dotenv import load_dotenv
from openai import AsyncOpenAI
from backend.query_handler import QueryHandler
from backend.document_processor import DocumentProcessor
from backend.vector_store import InMemoryVectorStore

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def setup():
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    document_processor = DocumentProcessor()
    vector_store = InMemoryVectorStore()
    query_handler = QueryHandler(vector_store, document_processor)
    client = AsyncOpenAI()
    
    # Create a thread
    thread = await client.beta.threads.create()
    
    return {
        'query_handler': query_handler,
        'client': client,
        'thread_id': thread.id,
        'assistant_id': os.getenv('ASSISTANT_ID')
    }

@pytest.mark.asyncio
async def test_workflow_1(setup):
    """Test basic Standards query without document context"""
    components = setup
    
    # Test query about Standards
    query = "What are the key requirements of Standard 1 regarding consumer dignity and choice?"
    
    response = await components['query_handler'].process_query(
        query=query,
        thread_id=components['thread_id'],
        assistant_id=components['assistant_id']
    )
    
    assert response is not None
    assert 'response' in response
    assert 'Standard 1' in response['response']
    print("\nWorkflow 1 Response:", response['response'])

@pytest.mark.asyncio
async def test_workflow_2(setup):
    """Test document-aware query with context"""
    components = setup
    
    # Process a test document
    test_file = "data/BRV-ComplaintsHandlingPolicy.pdf"
    await components['query_handler'].process_file(test_file, "test_policy")
    
    # Test query that requires document context
    query = "How does our complaints handling policy align with Standard 1?"
    
    response = await components['query_handler'].process_query(
        query=query,
        thread_id=components['thread_id'],
        assistant_id=components['assistant_id']
    )
    
    assert response is not None
    assert 'response' in response
    assert 'relevant_chunks' in response
    print("\nWorkflow 2 Response:", response['response'])

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 