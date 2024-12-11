from typing import List, Dict, TypedDict, Any, Union

class DocumentMetadata(TypedDict):
    file_path: str
    processed_at: str
    chunk_count: int

class ProcessedDocument(TypedDict):
    chunks: List[str]
    embeddings: List[List[float]]
    metadata: DocumentMetadata

class VectorStoreDocument(TypedDict):
    chunks: List[str]
    embeddings: List[List[float]]
    metadata: DocumentMetadata

class SearchResult(TypedDict):
    chunk: str
    score: float
    metadata: DocumentMetadata
    file_id: str

class RelevantChunk(TypedDict):
    chunk: str
    score: float
    metadata: Dict[str, Any]
    file_id: str

class QueryResponse(TypedDict):
    response: str
    relevant_chunks: List[RelevantChunk]
    enhanced_query: str

class FileProcessingResponse(TypedDict):
    status: str
    message: str
    metadata: Dict[str, Any]
