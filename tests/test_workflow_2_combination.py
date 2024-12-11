import os
import sys
import logging
import pytest
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from backend.document_processor import DocumentProcessor
from backend.vector_store import InMemoryVectorStore
from backend.query_handler import QueryHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for each test module."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def base_components():
    """Set up base components that don't require async operations."""
    logger.info("\nSetting up base components...")
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key not found in environment variables")
        
        # Use the correct assistant ID
        assistant_id = "asst_pYliV8MV2faRfHiWg3Z3Bfa1"
        
        # Initialize components
        document_processor = DocumentProcessor()
        vector_store = InMemoryVectorStore()
        query_handler = QueryHandler(vector_store, document_processor)
        
        # Set up test file paths
        test_file_path = os.path.join("data", "BRV-ComplaintsHandlingPolicy.pdf")
        test_file_path_2 = os.path.join("data", "EAC - Complaints Policy.pdf")
        
        if not os.path.exists(test_file_path) or not os.path.exists(test_file_path_2):
            raise ValueError(f"Test files not found")
            
        logger.info("Base setup complete.")
        
        return {
            'api_key': api_key,
            'assistant_id': assistant_id,
            'document_processor': document_processor,
            'vector_store': vector_store,
            'query_handler': query_handler,
            'test_file_path': test_file_path,
            'test_file_path_2': test_file_path_2
        }
        
    except Exception as e:
        logger.error(f"Base setup failed: {str(e)}")
        raise

@pytest.fixture(scope="function")
async def setup_components(base_components):
    """Set up components including async client for each test."""
    client = AsyncOpenAI(api_key=base_components['api_key'])
    components = {**base_components, 'client': client}
    return components

@pytest.mark.asyncio
async def test_natural_context_integration(setup_components):
    """Test natural integration of document context with Standards knowledge"""
    logger.info("\nTesting natural context integration...")
    thread_id = None
    try:
        # Get components
        components = await setup_components
        client = components['client']
        query_handler = components['query_handler']
        test_file_path = components['test_file_path']
        assistant_id = components['assistant_id']

        # Process document
        logger.info("Processing test document...")
        file_response = await query_handler.process_file(test_file_path, "test_policy")
        assert file_response['status'] == 'success'
        logger.info("Document processed successfully")

        # Create thread
        thread = await client.beta.threads.create()
        thread_id = thread.id
        logger.info(f"Created thread: {thread_id}")

        # Test query requiring natural integration
        test_query = """Looking at our complaints handling policy, how well does it align with 
        Standard 1's emphasis on dignity and choice? What specific improvements would you recommend?"""
        
        logger.info(f"\nProcessing query: {test_query}")
        response = await query_handler.process_query(
            query=test_query,
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Verify response structure
        assert response is not None, "No response received"
        assert 'response' in response, "Missing response field"
        assert 'relevant_chunks' in response, "Missing relevant_chunks field"
        assert 'enhanced_query' in response, "Missing enhanced_query field"
        assert len(response['relevant_chunks']) > 0, "No relevant chunks found"

        # Verify natural integration in response
        response_text = response['response'].lower()
        
        # Check for policy analysis
        assert any(term in response_text for term in [
            'your policy', 'your procedure', 'your process'
        ]), "Response doesn't reference organization's specific policy"
        
        # Check for Standards knowledge
        assert any(term in response_text for term in [
            'standard 1', 'dignity', 'choice', 'rights'
        ]), "Response doesn't reference Standards requirements"
        
        # Check for integration quality
        assert any(term in response_text for term in [
            'align', 'alignment', 'consistent with', 'meets'
        ]), "Response doesn't analyze alignment"
        
        # Check for practical recommendations
        assert any(term in response_text for term in [
            'recommend', 'suggest', 'improve', 'enhance'
        ]), "Response doesn't provide practical recommendations"

        logger.info("Successfully verified natural context integration")

    except Exception as e:
        logger.error(f"Natural context integration test failed: {str(e)}")
        raise
    finally:
        if thread_id:
            try:
                await client.beta.threads.delete(thread_id)
                logger.info("Cleaned up test thread")
            except Exception as e:
                logger.error(f"Failed to delete thread: {str(e)}")

@pytest.mark.asyncio
async def test_complex_policy_analysis(setup_components):
    """Test handling of complex policy analysis scenarios"""
    logger.info("\nTesting complex policy analysis...")
    thread_id = None
    try:
        # Get components
        components = await setup_components
        client = components['client']
        query_handler = components['query_handler']
        test_file_path = components['test_file_path']
        test_file_path_2 = components['test_file_path_2']
        assistant_id = components['assistant_id']

        # Process both documents
        logger.info("Processing test documents...")
        await query_handler.process_file(test_file_path, "policy1")
        await query_handler.process_file(test_file_path_2, "policy2")
        logger.info("Documents processed successfully")

        # Create thread
        thread = await client.beta.threads.create()
        thread_id = thread.id

        # Test complex analysis query
        test_query = """Compare our complaints handling policies with the new Standards' 
        requirements. What are the strengths and gaps in our current approach? How can we 
        better support diverse communities while maintaining compliance?"""
        
        logger.info(f"\nProcessing complex query: {test_query}")
        response = await query_handler.process_query(
            query=test_query,
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Verify comprehensive analysis
        assert response is not None, "No response received"
        assert len(response['relevant_chunks']) >= 2, "Not enough context found"
        
        response_text = response['response'].lower()
        
        # Check for comparative analysis
        assert any(term in response_text for term in [
            'strength', 'gap', 'difference', 'comparison'
        ]), "Response doesn't provide comparative analysis"
        
        # Check for diversity considerations
        assert any(term in response_text for term in [
            'diverse', 'cultural', 'community', 'inclusive'
        ]), "Response doesn't address diversity"
        
        # Check for compliance aspects
        assert any(term in response_text for term in [
            'compliance', 'requirement', 'standard', 'align'
        ]), "Response doesn't address compliance"
        
        # Check for actionable recommendations
        assert any(term in response_text for term in [
            'recommend', 'implement', 'improve', 'develop'
        ]), "Response doesn't provide actionable recommendations"

        logger.info("Successfully verified complex policy analysis")

    except Exception as e:
        logger.error(f"Complex policy analysis test failed: {str(e)}")
        raise
    finally:
        if thread_id:
            try:
                await client.beta.threads.delete(thread_id)
                logger.info("Cleaned up test thread")
            except Exception as e:
                logger.error(f"Failed to delete thread: {str(e)}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
