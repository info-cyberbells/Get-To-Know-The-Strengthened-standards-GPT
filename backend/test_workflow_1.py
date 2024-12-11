# import os
# import logging
# import pytest
# from pathlib import Path
# import asyncio
# import sys
# from dotenv import load_dotenv
# from openai import AsyncOpenAI
# from query_handler import QueryHandler
# from document_processor import DocumentProcessor
# from vector_store import InMemoryVectorStore

# # Configure logging
# sys.path.insert(0, str(Path(__file__).parent.parent))
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @pytest.fixture(scope="module")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

# @pytest.fixture(scope="module")
# async def setup():
#     """Set up test components."""
#     logger.info("\nSetting up test components...")
#     try:
#         load_dotenv()
        
#         # Initialize components
#         document_processor = DocumentProcessor()
#         vector_store = InMemoryVectorStore()
#         query_handler = QueryHandler(vector_store, document_processor)
#         client = AsyncOpenAI()
        
#         # Create thread
#         thread = await client.beta.threads.create()
        
#         return {
#             'query_handler': query_handler,
#             'client': client,
#             'thread_id': thread.id,
#             'assistant_id': os.getenv('ASSISTANT_ID')
#         }
#     except Exception as e:
#         logger.error(f"Setup failed: {str(e)}")
#         raise

# @pytest.mark.asyncio
# async def test_standards_query(setup):
#     """Test basic Standards query without document context"""
#     logger.info("\nTesting Standards query...")
#     try:
#         components = setup
        
#         # Test direct Standards query
#         query = "What are the key requirements of Standard 1 regarding consumer dignity and choice?"
        
#         response = await components['query_handler'].process_query(
#             query=query,
#             thread_id=components['thread_id'],
#             assistant_id=components['assistant_id']
#         )
        
#         # Verify response
#         assert response is not None, "No response received"
#         assert 'response' in response, "Missing response field"
#         assert 'Standard 1' in response['response'], "Response doesn't reference Standard 1"
        
#         # Verify Standards knowledge
#         response_text = response['response'].lower()
#         assert 'dignity' in response_text, "Response doesn't address dignity"
#         assert 'choice' in response_text, "Response doesn't address choice"
        
#         logger.info("Successfully tested Standards query")
        
#     except Exception as e:
#         logger.error(f"Standards query test failed: {str(e)}")
#         raise

# @pytest.mark.asyncio
# async def test_standards_interpretation(setup):
#     """Test interpretation of Standards requirements"""
#     logger.info("\nTesting Standards interpretation...")
#     try:
#         components = setup
        
#         query = """How does Standard 1 relate to diverse communities and cultural safety? 
#         What specific practices are recommended?"""
        
#         response = await components['query_handler'].process_query(
#             query=query,
#             thread_id=components['thread_id'],
#             assistant_id=components['assistant_id']
#         )
        
#         # Verify response
#         assert response is not None, "No response received"
#         response_text = response['response'].lower()
        
#         # Check for key concepts
#         assert any(term in response_text for term in [
#             'cultural', 'diverse', 'safety', 'inclusive'
#         ]), "Response doesn't address cultural safety"
        
#         # Check for practical guidance
#         assert any(term in response_text for term in [
#             'practice', 'implement', 'approach', 'strategy'
#         ]), "Response doesn't provide practical guidance"
        
#         logger.info("Successfully tested Standards interpretation")
        
#     except Exception as e:
#         logger.error(f"Standards interpretation test failed: {str(e)}")
#         raise

# if __name__ == '__main__':
#     pytest.main([__file__, '-v'])


import os
import logging
import pytest
from pathlib import Path
import asyncio
import sys
from dotenv import load_dotenv
from openai import AsyncOpenAI
from query_handler import QueryHandler
from document_processor import DocumentProcessor
from vector_store import InMemoryVectorStore

# Configure logging
sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Remove the custom event_loop fixture and let pytest-asyncio handle it
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="module")
async def test_components():
    """Set up test components."""
    logger.info("\nSetting up test components...")
    load_dotenv()
    
    # Initialize components
    document_processor = DocumentProcessor()
    vector_store = InMemoryVectorStore()
    query_handler = QueryHandler(vector_store, document_processor)
    client = AsyncOpenAI()
    
    # Create thread
    thread = await client.beta.threads.create()
    
    # Create a components dictionary
    components = {
        'query_handler': query_handler,
        'client': client,
        'thread_id': thread.id,
        'assistant_id': os.getenv('ASSISTANT_ID')
    }
    
    yield components
    # Cleanup if needed
    await client.close()

# Use scope parameter in the mark instead of a custom event_loop fixture
@pytest.mark.asyncio(scope="module")
async def test_standards_query(test_components):
    """Test basic Standards query without document context"""
    logger.info("\nTesting Standards query...")
    try:
        # Test direct Standards query
        query = "What are the key requirements of Standard 1 regarding consumer dignity and choice?"
        
        response = await test_components['query_handler'].process_query(
            query=query,
            thread_id=test_components['thread_id'],
            assistant_id=test_components['assistant_id']
        )
        
        # Verify response
        assert response is not None, "No response received"
        assert 'response' in response, "Missing response field"
        assert 'Standard 1' in response['response'], "Response doesn't reference Standard 1"
        
        # Verify Standards knowledge
        response_text = response['response'].lower()
        assert 'dignity' in response_text, "Response doesn't address dignity"
        assert 'choice' in response_text, "Response doesn't address choice"
        
        logger.info("Successfully tested Standards query")
        
    except Exception as e:
        logger.error(f"Standards query test failed: {str(e)}")
        raise

@pytest.mark.asyncio(scope="module")
async def test_standards_interpretation(test_components):
    """Test interpretation of Standards requirements"""
    logger.info("\nTesting Standards interpretation...")
    try:
        query = """How does Standard 1 relate to diverse communities and cultural safety? 
        What specific practices are recommended?"""
        
        response = await test_components['query_handler'].process_query(
            query=query,
            thread_id=test_components['thread_id'],
            assistant_id=test_components['assistant_id']
        )
        
        # Verify response
        assert response is not None, "No response received"
        response_text = response['response'].lower()
        
        # Check for key concepts
        assert any(term in response_text for term in [
            'cultural', 'diverse', 'safety', 'inclusive'
        ]), "Response doesn't address cultural safety"
        
        # Check for practical guidance
        assert any(term in response_text for term in [
            'practice', 'implement', 'approach', 'strategy'
        ]), "Response doesn't provide practical guidance"
        
        logger.info("Successfully tested Standards interpretation")
        
    except Exception as e:
        logger.error(f"Standards interpretation test failed: {str(e)}")
        raise

if __name__ == '__main__':
    pytest.main([__file__, '-v'])