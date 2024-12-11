from typing import List, Dict, Optional, cast
import numpy as np
from logger import logger
from custom_types import (
    DocumentMetadata,
    VectorStoreDocument,
    SearchResult
)

class InMemoryVectorStore:
    def __init__(self):
        self.documents: Dict[str, VectorStoreDocument] = {}  # file_id -> document data
        self.preloaded_documents: Dict[str, VectorStoreDocument] = {}  # preloaded document data

    def add_document(self, 
                    file_id: str, 
                    chunks: List[str], 
                    embeddings: List[List[float]], 
                    metadata: DocumentMetadata,
                    is_preloaded: bool = False) -> None:
        """Add a document to the vector store."""
        try:
            document_data = cast(VectorStoreDocument, {
                'chunks': chunks,
                'embeddings': embeddings,
                'metadata': metadata
            })
            
            if is_preloaded:
                self.preloaded_documents[file_id] = document_data
            else:
                self.documents[file_id] = document_data
                
            logger.info(f"Added document {file_id} to vector store (preloaded: {is_preloaded})")
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            raise

    def get_document(self, file_id: str, include_preloaded: bool = True) -> Optional[VectorStoreDocument]:
        """Retrieve a document from the vector store."""
        try:
            # Check user-uploaded documents
            if file_id in self.documents:
                return self.documents[file_id]
            
            # Check preloaded documents if requested
            if include_preloaded and file_id in self.preloaded_documents:
                return self.preloaded_documents[file_id]
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving document from vector store: {str(e)}")
            raise

    def remove_document(self, file_id: str) -> bool:
        """Remove a document from the vector store."""
        try:
            if file_id in self.documents:
                del self.documents[file_id]
                logger.info(f"Removed document {file_id} from vector store")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing document from vector store: {str(e)}")
            raise

    def search_similar(self, 
                      query_embedding: List[float], 
                      top_k: int = 5,
                      score_threshold: float = 0.7,
                      include_preloaded: bool = True) -> List[SearchResult]:
        """Search for similar chunks across all documents."""
        try:
            all_results: List[SearchResult] = []
            
            # Function to process documents and find similar chunks
            def process_documents(documents: Dict[str, VectorStoreDocument]) -> List[SearchResult]:
                results: List[SearchResult] = []
                for file_id, doc_data in documents.items():
                    embeddings = np.array(doc_data['embeddings'])
                    chunks = doc_data['chunks']
                    metadata = doc_data['metadata']
                    
                    # Compute similarities
                    similarities = np.dot(embeddings, query_embedding) / (
                        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
                    )
                    
                    # Get indices of top similar chunks above threshold
                    similar_indices = np.where(similarities >= score_threshold)[0]
                    similar_scores = similarities[similar_indices]
                    
                    # Sort by similarity score
                    sorted_indices = np.argsort(similar_scores)[::-1]
                    
                    for idx in sorted_indices:
                        chunk_idx = similar_indices[idx]
                        results.append(cast(SearchResult, {
                            'chunk': chunks[chunk_idx],
                            'score': float(similar_scores[idx]),
                            'metadata': metadata,
                            'file_id': file_id
                        }))
                return results
            
            # Process user-uploaded documents
            all_results.extend(process_documents(self.documents))
            
            # Process preloaded documents if requested
            if include_preloaded:
                all_results.extend(process_documents(self.preloaded_documents))
            
            # Sort all results by score and return top_k
            all_results.sort(key=lambda x: x['score'], reverse=True)
            return all_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the vector store."""
        try:
            return {
                'user_documents_count': len(self.documents),
                'preloaded_documents_count': len(self.preloaded_documents),
                'total_user_chunks': sum(len(doc['chunks']) for doc in self.documents.values()),
                'total_preloaded_chunks': sum(len(doc['chunks']) for doc in self.preloaded_documents.values())
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            raise
