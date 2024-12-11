

# import os
# import uuid
# from datetime import datetime
# from dotenv import load_dotenv
# from typing import Optional, Dict, Any, cast

# from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
# from fastapi.responses import StreamingResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from openai import OpenAI, AsyncOpenAI
# from openai.types.beta import Thread

# from logger import logger
# from utils import chat_with_assistant, chat_with_assistant_file
# from document_processor import DocumentProcessor
# from vector_store import InMemoryVectorStore
# from query_handler import QueryHandler
# from custom_types import FileProcessingResponse

# # Load environment variables
# load_dotenv()

# app = FastAPI()
# client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# # Get assistant ID from environment
# temp_assistant_id: Optional[str] = os.getenv('ASSISTANT_ID')
# if not temp_assistant_id:
#     raise ValueError("ASSISTANT_ID environment variable is not set")

# UPLOAD_DIR = "uploads"
# if not os.path.exists(UPLOAD_DIR):
#     os.makedirs(UPLOAD_DIR)

# # Store in a non-optional variable after the check
# assistant_id: str = temp_assistant_id

# # Initialize components
# document_processor = DocumentProcessor()
# vector_store = InMemoryVectorStore()
# query_handler = QueryHandler(vector_store, document_processor)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with specific origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["*"]
# )

# @app.get('/api/v1/assistant/health')
# async def health_check() -> JSONResponse:
#     """Health check endpoint to verify the server is running"""
#     return JSONResponse(content={'status': 'healthy', 'message': 'Server is running'})

# @app.get('/api/v1/assistant/threads')
# async def create_thread() -> Dict[str, Any]:
#     """Create a new conversation thread"""
#     try:
#         if not client.api_key:
#             logger.error("OpenAI API key is not set")
#             raise HTTPException(
#                 status_code=500,
#                 detail="OpenAI API key is not configured"
#             )
            
#         thread = await client.beta.threads.create()
        
#         # Convert Thread object to a serializable dictionary
#         thread_dict = {
#             "id": thread.id,
#             "created_at": thread.created_at,
#             "metadata": thread.metadata if hasattr(thread, 'metadata') else None,
#             "object": thread.object if hasattr(thread, 'object') else "thread"
#         }
        
#         logger.info(f"Thread created successfully: {thread.id}")
#         return {"data": thread_dict}
        
#     except Exception as e:
#         logger.error(f"Error creating thread: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to create thread: {str(e)}"
#         )

# @app.post('/api/v1/assistant/chat')
# async def assistant(request: Request) -> StreamingResponse:
#     """Handle chat requests without file attachments"""
#     try:
#         data = await request.json()
#         thread_id = data.get('thread_id')
#         user_query = data.get('user_query')
        
#         if not thread_id or not user_query:
#             raise HTTPException(status_code=400, detail="Missing thread_id or user_query")

#         # Process query using the query handler
#         response = await query_handler.process_query(
#             query=user_query,
#             thread_id=thread_id,
#             assistant_id=assistant_id
#         )
        
#         # Get thread for streaming response
#         thread = await client.beta.threads.retrieve(thread_id)
        
#         return StreamingResponse(
#             chat_with_assistant(
#                 assistant=assistant_id,
#                 thread=thread,
#                 user_query=response['enhanced_query']
#             ),
#             media_type='text/event-stream'
#         )
#     except Exception as e:
#         logger.error(f"Error in chat endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post('/api/v1/assistant/chat-file')
# async def chat_file(
#    thread_id: str = Form(...),
#    user_query: str = Form(...),
#    file: Optional[UploadFile] = File(None)
# ) -> StreamingResponse:
#    """Handle chat requests with file attachments"""
#    save_path = None
#    try:
#        # Log request details
#        logger.info("=" * 50)
#        logger.info("NEW CHAT REQUEST WITH FILE")
#        logger.info("=" * 50)
#        logger.info(f"User Query: {user_query}")
#        if file:
#            logger.info(f"Attached File: {file.filename}")
#        logger.info("-" * 50)

#        # Retrieve thread
#        thread = await client.beta.threads.retrieve(thread_id)
#        logger.info(f"Thread Retrieved: {thread}")

#        if file and file.filename:
#            logger.info(f"Processing file: {file.filename}")
           
#            # Generate unique file ID and save path
#            file_id = str(uuid.uuid4())
#            file_extension = os.path.splitext(file.filename)[1].lower()
#            save_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")
           
#            # Read and save file content
#            content = await file.read()
#            if not content:
#                logger.error("Empty file content received")
#                raise HTTPException(status_code=400, detail="Empty file uploaded")
               
#            content_size = len(content)
#            logger.info(f"File Size: {content_size} bytes")
           
#            # Save file
#            with open(save_path, "wb") as f:
#                f.write(content)
#            logger.info(f"File saved successfully at: {save_path}")
           
#            # Process file and add to vector store
#            process_result = await query_handler.process_file(save_path, file_id)
#            logger.info(f"File processing result: {process_result}")

#            async def response_generator():
#                try:
#                    logger.info("Starting response generation...")
#                    async for token in chat_with_assistant_file(
#                        assistant=assistant_id,
#                        thread=thread,
#                        user_query=f"{user_query}\n\nContext from uploaded file: {file.filename}",
#                        file_path=save_path
#                    ):
#                        yield token
#                    logger.info("Response generation completed")
#                except Exception as e:
#                    logger.error(f"Error during response generation: {str(e)}", exc_info=True)
#                    raise
#                finally:
#                    # Only remove file after response is complete
#                    if os.path.exists(save_path):
#                        try:
#                            os.remove(save_path)
#                            logger.info(f"Temporary file removed: {save_path}")
#                        except Exception as e:
#                            logger.error(f"Error removing temporary file: {str(e)}")

#            return StreamingResponse(
#                response_generator(),
#                media_type='text/event-stream'
#            )
       
#        # Handle request without file
#        logger.info("Processing query without file")
#        return StreamingResponse(
#            chat_with_assistant(
#                assistant=assistant_id,
#                thread=thread,
#                user_query=user_query
#            ),
#            media_type='text/event-stream'
#        )
   
#    except Exception as e:
#        # Log the full error with traceback
#        logger.error(f"Error in chat-file endpoint: {str(e)}", exc_info=True)
       
#        # Clean up file if error occurred before streaming
#        if save_path and os.path.exists(save_path):
#            try:
#                os.remove(save_path)
#                logger.info(f"Temporary file removed due to error: {save_path}")
#            except Exception as cleanup_error:
#                logger.error(f"Error removing temporary file: {str(cleanup_error)}")
       
#        # Raise HTTP exception
#        raise HTTPException(
#            status_code=500,
#            detail=f"Error processing request: {str(e)}"
#        )

# @app.get('/api/v1/vector-store/stats')
# async def get_vector_store_stats() -> JSONResponse:
#     """Get statistics about the vector store"""
#     try:
#         stats = vector_store.get_stats()
#         return JSONResponse(content=stats)
#     except Exception as e:
#         logger.error(f"Error getting vector store stats: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)



from logger import logger
import shutil
import os
from datetime import datetime

from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
import json
import tempfile
from utils import chat_with_assistant, chat_with_assistant_file

app = FastAPI()
client = OpenAI(api_key="openai-api-key")

assistant_id = 'assistant-id'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins or specify a list
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get('/test')
async def test():
    print("hello....... ")
    return JSONResponse(content={'message': 'Hello World!', 'status_code': 200})

@app.get('/api/v1/assistant/health')
async def health_check() -> JSONResponse:
    """Health check endpoint to verify the server is running"""
    return JSONResponse(content={'status': 'healthy', 'message': 'Server is running'})


@app.get('/api/v1/assistant/threads')
async def create_thread():
    thread = client.beta.threads.create()
    return {"data": thread}


@app.post('/api/v1/assistant/chat')
async def assistant(request: Request):
    print("assistant called")
    data = await request.json()
    print(data)
    thread_id = data.get('thread_id')
    user_query = data.get('user_query')
    thread = client.beta.threads.retrieve(thread_id)
    return StreamingResponse(chat_with_assistant(assistant="assistant-id", thread=thread, user_query=user_query))
    

@app.post('/api/v1/assistant/chat-file')
async def chat_file(
    thread_id: str = Form(...), 
    user_query: str = Form(...), 
    file: UploadFile = File(None)
):
    thread = client.beta.threads.retrieve(thread_id)
    logger.info(f"Thread Retrieved: {thread}")
    if file:
        logger.info(f"code is running with file")
        with open(f"{file.filename}", "wb") as f:
            f.write(file.file.read())
        return StreamingResponse(chat_with_assistant_file(assistant="assistant-id", thread=thread, user_query=user_query, file_path=file.filename))
    logger.info(f"code is running without file")
    return StreamingResponse(chat_with_assistant(assistant="assistant-id", thread=thread, user_query=user_query))

# old id: asst_4DJlWbqXooIm6hzJYBW5TSpX
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,  port=5002)   
    # enter your server host id for exm: host="0.0.0.0" or your server ip

