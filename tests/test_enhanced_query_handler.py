import os
import sys
import logging
import time
import pytest
import asyncio
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
from backend.document_processor import DocumentProcessor
from backend.vector_store import InMemoryVectorStore
from backend.query_handler import QueryHandler, AssistantError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def setup_components():
    """Set up test components."""
    logger.info("\nSetting up test components...")
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key not found in environment variables")
        
        # Use the correct assistant ID
        assistant_id = "asst_pYliV8MV2faRfHiWg3Z3Bfa1"
        client = OpenAI(api_key=api_key)
        
        # Initialize components
        document_processor = DocumentProcessor()
        vector_store = InMemoryVectorStore()
        query_handler = QueryHandler(vector_store, document_processor)
        
        # Set up test file paths
        test_file_path = os.path.join("data", "BRV-ComplaintsHandlingPolicy.pdf")
        test_file_path_2 = os.path.join("data", "EAC - Complaints Policy.pdf")
        
        if not os.path.exists(test_file_path) or not os.path.exists(test_file_path_2):
            raise ValueError(f"Test files not found")
            
        logger.info("Setup complete.")
        
        components = {
            'api_key': api_key,
            'assistant_id': assistant_id,
            'client': client,
            'document_processor': document_processor,
            'vector_store': vector_store,
            'query_handler': query_handler,
            'test_file_path': test_file_path,
            'test_file_path_2': test_file_path_2
        }
        
        return components
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_integrated_query_processing(setup_components):
    """Test the integrated query processing workflow"""
    logger.info("\nTesting integrated query processing...")
    thread_id = None
    try:
        # Get components
        client = setup_components['client']
        query_handler = setup_components['query_handler']
        test_file_path = setup_components['test_file_path']
        assistant_id = setup_components['assistant_id']

        # Create a thread
        thread = await client.beta.threads.create()
        thread_id = thread.id
        assert thread_id is not None, "Failed to create thread"

        # Process test file
        file_id = "test_policy"
        await query_handler.process_file(test_file_path, file_id)

        # Test query that should combine policy and user document info
        test_query = """How can I improve my complaints handling process to better align with Standard 1 
        of the Aged Care Quality Standards, particularly regarding consumer dignity and choice?"""

        response = await query_handler.process_query(
            query=test_query,
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Verify response structure
        assert response is not None, "No response received"
        assert 'response' in response, "Response missing response field"
        assert 'relevant_chunks' in response, "Response missing relevant_chunks field"
        assert 'enhanced_query' in response, "Response missing enhanced_query field"

        # Verify response content
        assert len(response['relevant_chunks']) > 0, "No relevant chunks found"
        assert "Standard 1" in response['response'], "Response doesn't reference Standard 1"
        assert "dignity" in response['response'].lower(), "Response doesn't address dignity"
        assert "choice" in response['response'].lower(), "Response doesn't address choice"

        # Verify enhanced query format
        enhanced_query = response['enhanced_query']
        assert "User's Question:" in enhanced_query, "Enhanced query missing original question"
        assert "relevant information from the user's organizational documents" in enhanced_query, \
            "Enhanced query missing context introduction"

        logger.info("Successfully tested integrated query processing")

    except Exception as e:
        logger.error(f"Integrated query test failed: {str(e)}")
        raise
    finally:
        if thread_id:
            await client.beta.threads.delete(thread_id)

@pytest.mark.asyncio
async def test_error_handling(setup_components):
    """Test error handling in each stage"""
    logger.info("\nTesting error handling...")
    thread_id = None
    try:
        query_handler = setup_components['query_handler']
        client = setup_components['client']
        assistant_id = setup_components['assistant_id']

        # Create a thread
        thread = await client.beta.threads.create()
        thread_id = thread.id

        # Test invalid file processing
        with pytest.raises(Exception):
            await query_handler.process_file("nonexistent.pdf", "invalid_file")
        logger.info("Successfully caught invalid file error")

        # Test invalid thread ID
        with pytest.raises(Exception):
            await query_handler.process_query(
                query="test query",
                thread_id="invalid_thread_id",
                assistant_id=assistant_id
            )
        logger.info("Successfully caught invalid thread ID error")

        # Test invalid assistant ID
        with pytest.raises(Exception):
            await query_handler.process_query(
                query="test query",
                thread_id=thread_id,
                assistant_id="invalid_assistant_id"
            )
        logger.info("Successfully caught invalid assistant ID error")

    except Exception as e:
        logger.error(f"Error handling test failed: {str(e)}")
        raise
    finally:
        if thread_id:
            await client.beta.threads.delete(thread_id)

@pytest.mark.asyncio
async def test_context_integration(setup_components):
    """Test the integration of user document context with Assistant knowledge"""
    logger.info("\nTesting context integration...")
    thread_id = None
    try:
        # Get components
        client = setup_components['client']
        query_handler = setup_components['query_handler']
        test_file_path = setup_components['test_file_path']
        test_file_path_2 = setup_components['test_file_path_2']
        assistant_id = setup_components['assistant_id']

        # Create a thread
        thread = await client.beta.threads.create()
        thread_id = thread.id

        # Process multiple test files
        await query_handler.process_file(test_file_path, "policy1")
        await query_handler.process_file(test_file_path_2, "policy2")

        # Test query that should integrate information from both documents with Standards
        test_query = "Compare our complaints handling processes with the requirements of the Strengthened Standards."

        response = await query_handler.process_query(
            query=test_query,
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Verify context integration
        assert response is not None, "No response received"
        assert len(response['relevant_chunks']) >= 2, "Not enough relevant chunks found"
        
        # Verify response integrates both document context and Standards knowledge
        response_text = response['response'].lower()
        assert "standards" in response_text, "Response doesn't reference Standards"
        assert "policy" in response_text, "Response doesn't reference organizational policies"
        assert "align" in response_text or "compliance" in response_text, \
            "Response doesn't discuss alignment between policies and Standards"

        logger.info("Successfully tested context integration")

    except Exception as e:
        logger.error(f"Context integration test failed: {str(e)}")
        raise
    finally:
        if thread_id:
            await client.beta.threads.delete(thread_id)

@pytest.mark.asyncio
async def test_logging_functionality(setup_components, caplog):
    """Test logging functionality"""
    logger.info("\nTesting logging functionality...")
    thread_id = None
    try:
        # Get components
        client = setup_components['client']
        query_handler = setup_components['query_handler']
        test_file_path = setup_components['test_file_path']
        assistant_id = setup_components['assistant_id']

        # Create a thread
        thread = await client.beta.threads.create()
        thread_id = thread.id

        # Process test file and capture logs
        with caplog.at_level(logging.INFO):
            await query_handler.process_file(test_file_path, "test_policy")
            await query_handler.process_query(
                query="How do our complaints processes align with the Standards?",
                thread_id=thread_id,
                assistant_id=assistant_id
            )

        # Verify logging content
        log_text = caplog.text.lower()
        assert "starting query processing" in log_text, "Missing query processing log"
        assert "searching user-uploaded documents" in log_text, "Missing document search log"
        assert "creating enhanced query" in log_text, "Missing enhanced query log"
        assert "getting response from assistant api" in log_text, "Missing Assistant API log"

        logger.info("Successfully tested logging functionality")

    except Exception as e:
        logger.error(f"Logging functionality test failed: {str(e)}")
        raise
    finally:
        if thread_id:
            await client.beta.threads.delete(thread_id)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
