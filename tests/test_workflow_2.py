import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
import pytest
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from PyPDF2.errors import EmptyFileError
from backend.document_processor import DocumentProcessor
from backend.vector_store import InMemoryVectorStore
from backend.query_handler import QueryHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@pytest.fixture(scope="module")
async def setup_components(base_components):
    """Set up components including async client for each test."""
    client = AsyncOpenAI(api_key=base_components['api_key'])
    components = {**base_components, 'client': client}
    yield components
    await client.close()

@pytest.mark.asyncio(loop_scope="module")
async def test_workflow_2_document_processing(setup_components):
    """Test document processing capabilities"""
    components = setup_components
    logger.info("\nTesting document processing capabilities...")
    try:
        document_processor = components['document_processor']
        test_file_path = components['test_file_path']
        
        # Test document processing
        processed_doc = document_processor.process_document(test_file_path)
        
        # Validate document processing results
        assert processed_doc is not None, "Document processing failed"
        assert 'chunks' in processed_doc, "Chunks not generated"
        assert 'embeddings' in processed_doc, "Embeddings not generated"
        assert 'metadata' in processed_doc, "Metadata not generated"
        
        # Validate chunk properties
        assert len(processed_doc['chunks']) > 0, "No chunks generated"
        assert len(processed_doc['chunks']) == len(processed_doc['embeddings']), "Chunks and embeddings count mismatch"
        
        # Validate chunk content
        for chunk in processed_doc['chunks']:
            assert len(chunk) > 0, "Empty chunk detected"
            assert isinstance(chunk, str), "Chunk is not string type"
            
        logger.info(f"Successfully processed document into {len(processed_doc['chunks'])} chunks")
        
    except Exception as e:
        logger.error(f"Document processing test failed: {str(e)}")
        raise

@pytest.mark.asyncio(loop_scope="module")
async def test_workflow_2_context_integration(setup_components):
    """Test the integration of document context with Assistant knowledge"""
    logger.info("\nTesting context integration...")
    thread_id = None
    try:
        client = setup_components['client']
        query_handler = setup_components['query_handler']
        test_file_path = setup_components['test_file_path']
        assistant_id = setup_components['assistant_id']

        # Step 1: Process and store the document
        logger.info("Processing test document...")
        file_response = await query_handler.process_file(test_file_path, "test_policy")
        assert file_response['status'] == 'success', "Failed to process document"
        logger.info("Document processed successfully")

        # Step 2: Create conversation thread
        thread = await client.beta.threads.create()
        thread_id = thread.id
        assert thread_id is not None, "Failed to create thread"
        logger.info(f"Created thread: {thread_id}")

        # Step 3: Test query that requires context integration
        test_query = """How does our complaints handling process align with Standard 1's 
        requirements for consumer dignity and choice? What improvements are needed?"""
        
        logger.info(f"Processing query: {test_query}")
        response = await query_handler.process_query(
            query=test_query,
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Verify response structure and content
        assert response is not None, "No response received"
        assert 'response' in response, "Response missing response field"
        assert 'relevant_chunks' in response, "Response missing relevant_chunks field"
        assert 'enhanced_query' in response, "Response missing enhanced_query field"

        # Verify enhanced query format
        enhanced_query = response['enhanced_query']
        assert "User's Question:" in enhanced_query, "Enhanced query missing original question"
        assert "relevant information from the user's organizational documents" in enhanced_query, \
            "Enhanced query missing context introduction"

        # Verify response content integration
        response_text = response['response'].lower()
        assert "standard 1" in response_text, "Response doesn't reference Standard 1"
        assert "dignity" in response_text, "Response doesn't address dignity"
        assert "choice" in response_text, "Response doesn't address choice"
        assert len(response['relevant_chunks']) > 0, "No relevant chunks found"

        # Verify response combines both sources
        assert any(
            term in response_text 
            for term in ['policy', 'procedure', 'process']
        ), "Response doesn't reference organization's documents"
        assert any(
            term in response_text 
            for term in ['standard', 'requirement', 'align']
        ), "Response doesn't reference Standards requirements"

        logger.info("Successfully tested context integration")

    except Exception as e:
        logger.error(f"Context integration test failed: {str(e)}")
        raise
    finally:
        if thread_id:
            try:
                await client.beta.threads.delete(thread_id)
                logger.info("Cleaned up test thread")
            except Exception as e:
                logger.error(f"Failed to delete thread: {str(e)}")

@pytest.mark.asyncio(loop_scope="module")
async def test_workflow_2_multiple_documents(setup_components):
    """Test handling multiple documents in context"""
    logger.info("\nTesting multiple document handling...")
    thread_id = None
    try:
        client = setup_components['client']
        query_handler = setup_components['query_handler']
        test_file_path = setup_components['test_file_path']
        test_file_path_2 = setup_components['test_file_path_2']
        assistant_id = setup_components['assistant_id']

        # Clear any existing documents
        query_handler.vector_store = InMemoryVectorStore()

        # Step 1: Process multiple documents
        logger.info("Processing multiple documents...")
        logger.info(f"Processing file 1: {test_file_path}")
        await query_handler.process_file(test_file_path, "policy1")
        
        logger.info(f"Processing file 2: {test_file_path_2}")
        await query_handler.process_file(test_file_path_2, "policy2")
        
        # Verify documents in vector store
        store_stats = query_handler.vector_store.get_stats()
        logger.info(f"Vector store stats: {store_stats}")

        # Step 2: Create thread
        thread = await client.beta.threads.create()
        thread_id = thread.id

        # Step 3: Test query with increased top_k
        test_query = "Compare our complaints handling policies and suggest improvements based on the Standards."
        
        logger.info(f"Processing query: {test_query}")
        response = await query_handler.process_query(
            query=test_query,
            thread_id=thread_id,
            assistant_id=assistant_id,
            top_k=10  # Increased from 6 to 10
        )

        # Debug response chunks
        logger.info("Retrieved chunks from documents:")
        for chunk in response['relevant_chunks']:
            logger.info(f"Chunk from: {chunk['metadata']['file_path']}")

        # Verify response handles multiple documents
        assert response is not None, "No response received"
        assert len(response['relevant_chunks']) >= 2, "Not enough relevant chunks found"
        
        # Verify response integrates multiple sources
        response_text = response['response'].lower()
        
        # Check for comparative analysis
        assert any(term in response_text for term in [
            'compare', 'comparison', 'both policies', 'differences'
        ]), "Response doesn't compare policies"
        
        # Check for policy references
        file_paths = [chunk['metadata']['file_path'] for chunk in response['relevant_chunks']]
        unique_files = set(file_paths)
        assert len(unique_files) >= 2, "Response doesn't reference both policies"
        
        # Check for standards integration
        assert "standard" in response_text, "Response doesn't reference Standards"
        assert "improvement" in response_text, "Response doesn't suggest improvements"

        logger.info("Successfully tested multiple document handling")

    except Exception as e:
        logger.error(f"Multiple document test failed: {str(e)}")
        raise
    finally:
        if thread_id:
            try:
                await client.beta.threads.delete(thread_id)
                logger.info("Cleaned up test thread")
            except Exception as e:
                logger.error(f"Failed to delete thread: {str(e)}")

@pytest.mark.asyncio(loop_scope="module")
async def test_invalid_document_scenarios(setup_components):
    """Test various invalid document scenarios"""
    logger.info("\nTesting invalid document scenarios...")
    temp_files = []
    try:
        document_processor = setup_components['document_processor']
        
        # Test case 1: Invalid file type
        invalid_file = "temp_invalid.txt"
        with open(invalid_file, 'w') as f:
            f.write("Invalid content")
        temp_files.append(invalid_file)
        
        with pytest.raises(ValueError):
            document_processor.process_document(invalid_file)
        logger.info("Successfully caught invalid file type error")
        
        # Test case 2: Empty file
        empty_file = "temp_empty.pdf"
        with open(empty_file, 'w') as f:
            pass
        temp_files.append(empty_file)
        
        with pytest.raises((ValueError, EmptyFileError)):
            document_processor.process_document(empty_file)
        logger.info("Successfully caught empty file error")
        
        # Test case 3: Non-existent file
        with pytest.raises(FileNotFoundError):
            document_processor.process_document("nonexistent.pdf")
        logger.info("Successfully caught non-existent file error")

    except Exception as e:
        logger.error(f"Invalid document scenarios test failed: {str(e)}")
        raise
    finally:
        # Clean up temporary files
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
        logger.info("Cleaned up temporary files")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
