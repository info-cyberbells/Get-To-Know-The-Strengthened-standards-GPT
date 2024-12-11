# from logger import logger
# import shutil
# import os
# from datetime import datetime

# from fastapi import FastAPI, Request, File, UploadFile, Form
# from fastapi.responses import StreamingResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from openai import OpenAI
# from typing_extensions import override
# from openai import AssistantEventHandler
# import json
# import tempfile
# from utils import chat_with_assistant, chat_with_assistant_file

# app = FastAPI()
# client = OpenAI(api_key="ENter-API-KEY")

# assistant_id = 'your-assistant-id'

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get('/test')
# async def test():
#     print("hello....... ")
#     return JSONResponse(content={'message': 'Hello World!', 'status_code': 200})

# @app.get('/api/v1/assistant/threads')
# async def create_thread():
#     thread = client.beta.threads.create()
#     return {"data": thread}


# @app.post('/api/v1/assistant/chat')
# async def assistant(request: Request):
#     print("assistant called")
#     data = await request.json()
#     print(data)
#     thread_id = data.get('thread_id')
#     user_query = data.get('user_query')
#     thread = client.beta.threads.retrieve(thread_id)
#     return StreamingResponse(chat_with_assistant(assistant="your-assis-id", thread=thread, user_query=user_query))
    

# @app.post('/api/v1/assistant/chat-file')
# async def chat_file(
#     thread_id: str = Form(...), 
#     user_query: str = Form(...), 
#     file: UploadFile = File(None)
# ):
#     thread = client.beta.threads.retrieve(thread_id)
#     logger.info(f"Thread Retrieved: {thread}")
#     if file:
#         logger.info(f"code is running with file")
#         with open(f"{file.filename}", "wb") as f:
#             f.write(file.file.read())
#         return StreamingResponse(chat_with_assistant_file(assistant="your-assis-id", thread=thread, user_query=user_query, file_path=file.filename))
#     logger.info(f"code is running without file")
#     return StreamingResponse(chat_with_assistant(assistant="your-assis-id", thread=thread, user_query=user_query))


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="5.161.122.193", port=5002)



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
client = OpenAI(api_key="ENTER-YOUR-API-KEY")

assistant_id = 'ENTER-YOUR-ASSISTANT-ID'

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
    return StreamingResponse(chat_with_assistant(assistant="ENTER-YOUR-ASSISTANT-ID", thread=thread, user_query=user_query))
    

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
        return StreamingResponse(chat_with_assistant_file(assistant="ENTER-YOUR-ASSISTANT-ID", thread=thread, user_query=user_query, file_path=file.filename))
    logger.info(f"code is running without file")
    return StreamingResponse(chat_with_assistant(assistant="ENTER-YOUR-ASSISTANT-ID", thread=thread, user_query=user_query))

# old id: asst_4DJlWbqXooIm6hzJYBW5TSpX
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="5.161.122.193", port=5002)

