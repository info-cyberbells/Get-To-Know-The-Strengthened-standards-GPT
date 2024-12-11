import os
from typing import List
import PyPDF2
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import numpy as np
from datetime import datetime
from logger import logger
from custom_types import ProcessedDocument, DocumentMetadata

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.embeddings = OpenAIEmbeddings()
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = []
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                
                # Join all text with proper spacing
                full_text = ' '.join(text)
                
                # Handle empty PDF
                if not full_text.strip():
                    raise ValueError(f"No text content found in PDF {file_path}")
                    
                return full_text
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise

    def extract_text(self, file_path: str) -> str:
        """Extract text from a document based on its file extension."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        try:
            # Convert text string to a format that the text splitter can handle
            if not isinstance(text, str):
                text = str(text)
                
            # Handle empty or invalid text
            if not text.strip():
                logger.warning("Received empty text for chunking")
                return []

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Successfully split text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise

    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks."""
        try:
            embeddings = self.embeddings.embed_documents(chunks)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def process_document(self, file_path: str) -> ProcessedDocument:
        """Process a document: extract text, chunk it, and generate embeddings."""
        try:
            # Extract text from document
            text = self.extract_text(file_path)
            logger.info(f"Extracted text from {file_path}")
            
            # Ensure text is a string
            if not isinstance(text, str):
                text = str(text)
            
            # Handle empty text
            if not text.strip():
                raise ValueError(f"No text content extracted from {file_path}")
                
            # Chunk the text
            chunks = self.chunk_text(text)
            if not chunks:
                raise ValueError(f"No chunks generated from {file_path}")
                
            # Generate embeddings
            chunk_embeddings = self.generate_embeddings(chunks)
            
            metadata: DocumentMetadata = {
                'file_path': file_path,
                'processed_at': datetime.now().isoformat(),
                'chunk_count': len(chunks)
            }
            
            logger.info(f"Successfully processed document {file_path} into {len(chunks)} chunks")
            return {
                'chunks': chunks,
                'embeddings': chunk_embeddings,
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    def compute_similarity(self, query_embedding: List[float], document_embeddings: List[List[float]]) -> List[float]:
        """Compute cosine similarity between query and document embeddings."""
        try:
            # Convert to numpy arrays for efficient computation
            query_array = np.array(query_embedding)
            doc_array = np.array(document_embeddings)
            
            # Compute cosine similarity
            similarities = np.dot(doc_array, query_array) / (
                np.linalg.norm(doc_array, axis=1) * np.linalg.norm(query_array)
            )
            
            return similarities.tolist()
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise
