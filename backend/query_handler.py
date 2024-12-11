from typing import List, Dict, Optional, AsyncGenerator, Any, cast
import asyncio
from openai import AsyncOpenAI
from openai.types.beta.threads import Run, Message
from openai.pagination import AsyncCursorPage
from document_processor import DocumentProcessor
from vector_store import InMemoryVectorStore
from custom_types import (
    ProcessedDocument,
    DocumentMetadata,
    QueryResponse,
    FileProcessingResponse,
    SearchResult,
    RelevantChunk
)
from logger import logger

class AssistantError(Exception):
    """Custom exception for Assistant API related errors"""
    pass

class QueryHandler:
    def __init__(self, vector_store: InMemoryVectorStore, document_processor: DocumentProcessor):
        self.vector_store = vector_store
        self.document_processor = document_processor
        self.openai_client = AsyncOpenAI()

    async def process_query(self, 
                          query: str, 
                          thread_id: str,
                          assistant_id: str,
                          top_k: int = 3,
                          similarity_threshold: float = 0.7) -> QueryResponse:
        """Process query by first getting relevant user document context, then querying Assistant"""
        try:
            logger.info("Starting query processing...")
            
            # Stage 1: Get relevant info from user documents
            logger.info("Searching user-uploaded documents...")
            user_doc_context = await self._get_user_document_context(
                query=query,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            logger.info(f"Found {len(user_doc_context)} relevant chunks from user documents")
            
            # Stage 2: Create enhanced query incorporating user document context
            logger.info("Creating enhanced query...")
            enhanced_query = self._create_enhanced_query(
                original_query=query,
                user_context=user_doc_context
            )
            
            # Stage 3: Get comprehensive response from Assistant
            logger.info("Getting response from Assistant API...")
            assistant_response = await self._get_assistant_response(
                query=enhanced_query,
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            logger.info("Received Assistant API response")
            
            return cast(QueryResponse, {
                'response': assistant_response,
                'relevant_chunks': user_doc_context,
                'enhanced_query': enhanced_query
            })
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def _create_enhanced_query(self, original_query: str, user_context: List[RelevantChunk]) -> str:
        """Create an enhanced query that incorporates user document context"""
        try:
            if not user_context:
                return original_query
            
            # Format the context from user documents
            context = self._format_context(user_context)
            
            # Group documents by source
            sources = {}
            for chunk in user_context:
                file_path = chunk['metadata'].get('file_path', 'unknown')
                if file_path not in sources:
                    sources[file_path] = []
                sources[file_path].append(chunk['chunk'])

            # Create a more structured prompt based on query type
            if any(term in original_query.lower() for term in ['compare', 'difference', 'similarities']):
                # Comparison query
                enhanced_query = f"""I need you to help analyze and compare different organizational policies 
                while considering the Strengthened Aged Care Quality Standards.

                User's Question: {original_query}

                I have {len(sources)} different policy documents to compare:

                {self._format_sources_summary(sources)}

                Please provide a detailed response that:
                1. Explicitly compares and contrasts the approaches in these policies
                2. Identifies specific strengths and potential gaps in each policy
                3. Analyzes how well each aligns with the Standards
                4. Recommends improvements based on both the Standards and best practices
                5. Highlights any unique features or innovative approaches in each policy

                Make your response clear and structured, with explicit comparisons between the policies."""

            else:
                # Standard query
                enhanced_query = f"""I need you to help answer a question about the Strengthened Aged Care Quality Standards, 
                while incorporating specific information from the user's organization.

                User's Question: {original_query}

                Here is relevant information from the user's organizational documents:
                {context}

                Please provide a response that:
                1. Explains how the Standards apply to their specific situation
                2. References relevant parts of their organizational documents
                3. Identifies any specific alignments or potential gaps
                4. Provides practical suggestions for implementation

                Make your response conversational and natural, weaving together information from both sources."""

            return enhanced_query
            
        except Exception as e:
            logger.error(f"Error creating enhanced query: {str(e)}")
            raise

    def _format_sources_summary(self, sources: Dict[str, List[str]]) -> str:
        """Format a summary of different document sources"""
        summary_parts = []
        for file_path, chunks in sources.items():
            source_name = file_path.split('\\')[-1]  # Get just the filename
            summary = f"Document: {source_name}\nKey points:\n"
            for i, chunk in enumerate(chunks, 1):
                summary += f"{i}. {chunk.strip()}\n"
            summary_parts.append(summary)
        return "\n\n".join(summary_parts)

    async def _get_user_document_context(self, 
                                       query: str,
                                       top_k: int = 3,
                                       similarity_threshold: float = 0.7) -> List[RelevantChunk]:
        """Search user-uploaded documents for relevant information"""
        try:
            # Generate embedding for the query
            query_embedding = self.document_processor.embeddings.embed_query(query)
            logger.info("Generated query embedding")
            
            # Search for relevant documents
            similar_chunks = self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                score_threshold=similarity_threshold
            )
            logger.info(f"Found {len(similar_chunks)} similar chunks")
            
            # Convert SearchResult to RelevantChunk
            relevant_chunks = [cast(RelevantChunk, {
                'chunk': chunk['chunk'],
                'score': chunk['score'],
                'metadata': dict(chunk['metadata']),
                'file_id': chunk['file_id']
            }) for chunk in similar_chunks]
            
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error getting user document context: {str(e)}")
            raise

    def _format_context(self, chunks: List[RelevantChunk]) -> str:
        """Format document chunks into a context string."""
        try:
            if not chunks:
                return ""
            
            context_parts = []
            for chunk in chunks:
                source_info = f"From {chunk['metadata'].get('file_path', 'unknown source')}"
                context_parts.append(f"{source_info}:\n{chunk['chunk']}\n")
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error formatting context: {str(e)}")
            raise

    async def _get_assistant_response(self, 
                                    query: str, 
                                    thread_id: str,
                                    assistant_id: str) -> str:
        """Get response from OpenAI Assistant."""
        try:
            logger.info("Creating message in thread...")
            # Create message in thread
            message_response = await self.openai_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=query
            )
            logger.info("Message created successfully")
            
            logger.info("Starting assistant run...")
            # Create run
            run_response = await self.openai_client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            
            # Wait for run to complete
            run = run_response
            max_retries = 60  # Maximum number of retries (60 * 2 seconds = 2 minutes)
            retries = 0
            
            while run.status in ['queued', 'in_progress'] and retries < max_retries:
                logger.info(f"Run status: {run.status} (attempt {retries + 1}/{max_retries})")
                await asyncio.sleep(2)  # Wait 2 seconds between checks
                run_status = await self.openai_client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                run = run_status
                retries += 1
            
            if run.status == 'completed':
                logger.info("Run completed successfully")
                # Get messages after completion
                messages_response = await self.openai_client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                
                # Get the assistant's response
                for msg in messages_response.data:
                    if msg.role == "assistant":
                        for content in msg.content:
                            if hasattr(content, 'text'):
                                logger.info("Retrieved assistant's response")
                                return content.text.value
            
            error_msg = f"Assistant run failed with status: {run.status}"
            if retries >= max_retries:
                error_msg = "Assistant run timed out after 2 minutes"
            logger.error(error_msg)
            raise AssistantError(error_msg)
            
        except Exception as e:
            logger.error(f"Error getting assistant response: {str(e)}")
            raise

    async def process_file(self, file_path: str, file_id: str) -> FileProcessingResponse:
        """Process a new file and add it to the vector store."""
        try:
            # Process the document
            doc_result = self.document_processor.process_document(file_path)
            
            # Add to vector store
            self.vector_store.add_document(
                file_id=file_id,
                chunks=doc_result['chunks'],
                embeddings=doc_result['embeddings'],
                metadata=doc_result['metadata']
            )
            
            return cast(FileProcessingResponse, {
                'status': 'success',
                'message': f'File processed and added to vector store',
                'metadata': dict(doc_result['metadata'])
            })
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise
