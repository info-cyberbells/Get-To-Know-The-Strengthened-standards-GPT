# import asyncio
# import json
# import os
# from datetime import datetime
# import logging
# import signal
# from dotenv import load_dotenv

# from typing import Dict, Any
# from openai import AsyncOpenAI, OpenAI
# from openai.types.beta import Assistant, Thread
# from openai.types.beta.threads import Run, RequiredActionFunctionToolCall
# from openai.types.beta.assistant_stream_event import (
#     ThreadRunRequiresAction, ThreadMessageDelta, ThreadRunCompleted,
#     ThreadRunFailed, ThreadRunCancelling, ThreadRunCancelled, ThreadRunExpired, ThreadRunStepFailed,
#     ThreadRunStepCancelled)
# from logging.handlers import TimedRotatingFileHandler

# # Configure logging
# if not os.path.exists('logs'):
#     os.makedirs('logs')
# date_string = datetime.now().strftime("%Y-%m-%d")
# log_file = f'logs/assistant-chatbot-{date_string}.log'
# handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=5)
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s %(name)s %(threadName)s : %(message)s')
# handler.setFormatter(formatter)

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# logger.addHandler(handler)

# # Load environment variables
# load_dotenv()

# client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# sync_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# tool_instances: Dict[str, Any] = {}

# async def handle_function_call(tool_call: RequiredActionFunctionToolCall) -> tuple[str | None, str | None]:
#     if tool_call.type != "function":
#         return None, None
#     tool_id = tool_call.id
#     function = tool_call.function
#     function_name = function.name
#     function_args = json.loads(function.arguments)
#     try:
#         logger.info(f"calling function {function_name} with args: {function_args}")
#         # function_result = await tool_instances[function_name].arun(**function_args)
#         function_result = "true"
#         logger.info(f"got result from {function_name}: {function_result}")
#     except Exception as e:
#         logger.exception(f"Error handling function call: {e}")
#         function_result = None
#     return tool_id, function_result

# async def handle_function_calls(run_obj: Run) -> Dict[str, str]:
#     required_action = run_obj.required_action
#     if not required_action or required_action.type != "submit_tool_outputs":
#         return {}

#     tool_calls = required_action.submit_tool_outputs.tool_calls
#     results = await asyncio.gather(
#         *(handle_function_call(tool_call) for tool_call in tool_calls)
#     )
#     return {tool_id: result for tool_id, result in results if tool_id is not None and result is not None}

# async def submit_tool_outputs(thread_id: str, run_id: str, function_ids_to_result_map: Dict[str, str],
#                               stream=False):
#     tool_outputs = [{"tool_call_id": tool_id, "output": result} for tool_id, result in
#                     function_ids_to_result_map.items()]

#     logger.info(f"submitting tool outputs: {tool_outputs}")
#     run = await client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run_id,
#                                                              tool_outputs=tool_outputs,
#                                                              stream=stream)

#     return run

# async def kill_if_thread_is_running(thread_id: str):
#     runs = client.beta.threads.runs.list(
#         thread_id=thread_id
#     )

#     running_threads = []
#     async for run in runs:
#         if run.status in ["in_progress", "queued", "requires_action", "cancelling"]:
#             running_threads.append(run)

#     async def kill_run(run_to_kill: Run):
#         counter = 0
#         try:
#             while True:
#                 run_obj = await client.beta.threads.runs.retrieve(run_id=run_to_kill.id, thread_id=thread_id)
#                 run_status = run_obj.status
#                 if run_status == "cancelling":
#                     logger.info(f"run {run_to_kill.id} is being cancelled, waiting for it to get cancelled")
#                     await asyncio.sleep(2)
#                     continue

#                 if run_status in ["cancelled", "failed", "completed", "expired"]:
#                     logger.info(f"run {run_to_kill.id} is cancelled")
#                     break

#                 run_obj = await client.beta.threads.runs.cancel(
#                     thread_id=thread_id,
#                     run_id=run_to_kill.id
#                 )

#                 if run_obj.status in ["cancelled", "failed", "expired"]:
#                     logger.info(
#                         f"run {run_obj.id} for thread {thread_id} is killed. status is {run_obj.status}")
#                     break

#                 else:
#                     logger.info(
#                         f"run {run_obj.id} for thread {thread_id} is not yet killed. status is {run_obj.status}")
#                     counter += 1
#                     await asyncio.sleep(2)
#                     continue

#         except Exception:
#             logger.exception(f"error in killing thread: {thread_id}")
#             raise Exception(f"error in killing thread: {thread_id}")

#     if not running_threads:
#         logger.info(f"no running threads for thread : {thread_id}")
#         return

#     if running_threads:
#         logger.info(f"total {len(running_threads)} running threads")
#         tasks = []
#         for run_obj in running_threads:
#             task = asyncio.create_task(kill_run(run_obj))
#             await asyncio.sleep(0)
#             tasks.append(task)

#         done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED, timeout=120)
#         no_of_exceptions = 0

#         for done_task in done:
#             if done_task.exception() is None:
#                 task_result = done_task.result()
#                 if task_result:
#                     logger.info(f"status of run kill task: {done_task} is {task_result}")

#             else:
#                 if logger:
#                     logger.exception(f"error in run kill task: {done_task}, "
#                                      f"exception: {done_task.exception()}")

#                 no_of_exceptions += 1

#         for pending_task in pending:
#             logger.info(f"cancelling run kill task: {pending_task}")
#             pending_task.cancel()

#         if no_of_exceptions > 0 or pending:
#             raise Exception("failed to kill running threads")

# async def process_event(event: Any, thread: Thread, **kwargs):
#     """Process streaming events from the assistant"""
#     try:
#         # Handle message delta events
#         if isinstance(event, ThreadMessageDelta) and event.data.delta.content:
#             data = event.data.delta.content
#             for text in data:
#                 if hasattr(text, 'text') and hasattr(text.text, 'value'):
#                     token = text.text.value
#                     logger.debug(f"Received token: {token}")
#                     yield token

#         # Handle completion events
#         elif isinstance(event, ThreadRunCompleted):
#             logger.info("Chat completion finished successfully")
#             # Fetch the final message
#             messages = await client.beta.threads.messages.list(thread_id=thread.id)
#             latest_message = messages.data[0]  # Most recent message
#             if latest_message.role == "assistant":
#                 logger.info("=" * 50)
#                 logger.info("FINAL ASSISTANT RESPONSE")
#                 logger.info("=" * 50)
#                 for content in latest_message.content:
#                     if hasattr(content, 'text'):
#                         logger.info(content.text.value)
#                         yield content.text.value

#         # Handle function calls or actions
#         elif isinstance(event, ThreadRunRequiresAction):
#             logger.info("Processing function calls...")
#             run_obj = event.data
#             function_ids_to_result_map = await handle_function_calls(run_obj)
#             tool_output_events = await submit_tool_outputs(
#                 thread.id, 
#                 run_obj.id,
#                 function_ids_to_result_map,
#                 stream=True
#             )
#             async for tool_event in tool_output_events:
#                 async for token in process_event(tool_event, thread=thread, **kwargs):
#                     yield token

#     except Exception as e:
#         logger.error(f"Error processing event: {str(e)}", exc_info=True)
#         yield f"An error occurred while processing the event: {str(e)}"
#         raise

# async def process_event(event: Any, thread: Thread, **kwargs):
#     """Process streaming events from the assistant"""
#     try:
#         if isinstance(event, ThreadMessageDelta) and event.data.delta.content:
#             data = event.data.delta.content
#             for text in data:
#                 if hasattr(text, 'text') and hasattr(text.text, 'value'):
#                     yield text.text.value

#         elif isinstance(event, ThreadRunCompleted):
#             logger.info("Chat completion finished successfully")
#             # Don't fetch and send the message again here
#             return

#     except Exception as e:
#         logger.error(f"Error processing event: {str(e)}", exc_info=True)
#         yield f"An error occurred while processing the event: {str(e)}"

# async def chat_with_assistant(assistant: str, thread: Thread, user_query: str, **kwargs):
#     message = await client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_query)
#     logger.info(f"created message: {message}")

#     stream = await client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant,
#         stream=True
#     )

#     async for event in stream:
#         async for token in process_event(event, thread, **kwargs):
#             yield token

#     print("\nTool output completed")
#     print("*" * 100)

# from pathlib import Path

# async def chat_with_assistant_file(assistant: str, thread: Thread, user_query: str, file_path: str, **kwargs):
#     """Handle chat requests with file attachments"""
#     file_upload = None
#     full_response = []  # To collect response parts
    
#     try:
#         logger.info("Starting file-based chat process...")
        
#         # Upload file to OpenAI
#         with open(file_path, 'rb') as f:
#             file_upload = await client.files.create(
#                 file=f,
#                 purpose='assistants'
#             )
#         logger.info(f"File uploaded to OpenAI with ID: {file_upload.id}")

#         # Create messages
#         text_message = await client.beta.threads.messages.create(
#             thread_id=thread.id,
#             role="user",
#             content=user_query
#         )
#         logger.info(f"Created text message with ID: {text_message.id}")

#         file_message = await client.beta.threads.messages.create(
#             thread_id=thread.id,
#             role="user",
#             content="",  # Empty content for file message
#             attachments=[{"file_id": file_upload.id, "purpose": "embedding"}]
#         )
#         logger.info(f"Created file message with ID: {file_message.id}")

#         # Create run with the assistant
#         stream = await client.beta.threads.runs.create(
#             thread_id=thread.id,
#             assistant_id=assistant,
#             stream=True
#         )
#         logger.info("Created assistant run")

#         logger.info("=" * 50)
#         logger.info("STREAMING RESPONSE")
#         logger.info("=" * 50)

#         # Process the stream
#         async for event in stream:
#             logger.info(f"Received event: {event}")
#             async for token in process_event(event, thread, **kwargs):
#                 logger.info(f"Yielding token: {token}")
#                 full_response.append(token)
#                 yield token

#         # Log the complete response
#         if not full_response:
#             logger.warning("No tokens were received in the response stream.")
#             yield "I'm sorry, I couldn't generate a response. Please try again."

#         complete_response = "".join(full_response)
#         logger.info("=" * 50)
#         logger.info("COMPLETE RESPONSE:")
#         logger.info("=" * 50)
#         logger.info(complete_response)
#         logger.info("=" * 50)
        
#     except Exception as e:
#         logger.error(f"Error in chat_with_assistant_file: {str(e)}", exc_info=True)
#         if file_upload:
#             logger.error(f"File upload info: {file_upload.id}")
#         yield f"An error occurred: {str(e)}"
#         raise

#     finally:
#         # Clean up temporary file
#         try:
#             os.remove(file_path)
#             logger.info(f"Temporary file removed: {file_path}")
#         except Exception as cleanup_error:
#             logger.warning(f"Error during cleanup: {cleanup_error}")
#         logger.info("Chat session completed")


# async def create_thread() -> Thread:
#     thread = await client.beta.threads.create()
#     logger.info(f"created new thread: {thread.id}")
#     return thread

# def delete_thread(thread_id: str):
#     thread_deleted = sync_client.beta.threads.delete(thread_id=thread_id)
#     logger.info(f"deleted thread {thread_id}: {thread_deleted.deleted}")

# async def main():
#     thread = await create_thread()

#     def signal_handler(sig, frame):
#         print('Signal received, deleting thread and exiting...')
#         delete_thread(thread_id=thread.id)

#     signal.signal(signal.SIGINT, signal_handler)

#     while True:
#         try:
#             query = input("Enter your query. (TYPE 'exit' TO STOP AND EXIT): ")

#             if query.lower().strip() == "exit":
#                 break

#             async for token in chat_with_assistant(assistant=os.getenv('ASSISTANT_ID', ''), thread=thread, user_query=query):
#                 print(token, end='')

#         except Exception:
#             logger.exception("error in chat: ")

#     delete_thread(thread_id=thread.id)

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())



import asyncio
import json
import os
from datetime import datetime
import logging
import signal
from logger import logger

from typing import Dict
from openai import AsyncOpenAI, OpenAI
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import Run, RequiredActionFunctionToolCall
from openai.types.beta.assistant_stream_event import (
    ThreadRunRequiresAction, ThreadMessageDelta, ThreadRunCompleted,
    ThreadRunFailed, ThreadRunCancelling, ThreadRunCancelled, ThreadRunExpired, ThreadRunStepFailed,
    ThreadRunStepCancelled)
from logging.handlers import TimedRotatingFileHandler
# if not os.path.exists('logs'):
#     os.makedirs('logs')
# date_string = datetime.now().strftime("%Y-%m-%d")
# log_file = f'logs/jewelli-chatbot-{date_string}.log'
# handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=5)
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s %(name)s %(threadName)s : %(message)s')
# handler.setFormatter(formatter)

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# logger.addHandler(handler)


client = AsyncOpenAI(api_key="openai-api-key")
sync_client = OpenAI(api_key="openai-api-key")

# OpenAIAssistant is class that I had written which acts as a factory 
# to create an assistant. It has wrapper methods for various functionalities.
# for brevity I am omitting the implementation details of this class.
# you can write your own class that creates/retrieves an assistant.
# assistant_creator = OpenAIAssistant(client=client)

tool_instances = {}

async def handle_function_call(tool_call: RequiredActionFunctionToolCall) -> (str, str):
    if tool_call.type != "function":
        return None, None
    tool_id = tool_call.id
    function = tool_call.function
    function_name = function.name
    function_args = json.loads(function.arguments)
    try:
        logger.info(f"calling function {function_name} with args: {function_args}")
        # function_result = await tool_instances[function_name].arun(**function_args)
        function_result = "true"
        logger.info(f"got result from {function_name}: {function_result}")
    except Exception as e:
        logger.exception(f"Error handling function call: {e}")
        function_result = None
    return tool_id, function_result

async def handle_function_calls(run_obj: Run) -> Dict[str, str]:
    required_action = run_obj.required_action
    if required_action.type != "submit_tool_outputs":
        return {}

    tool_calls = required_action.submit_tool_outputs.tool_calls
    results = await asyncio.gather(
        *(handle_function_call(tool_call) for tool_call in tool_calls)
    )
    return {tool_id: result for tool_id, result in results if tool_id is not None}

async def submit_tool_outputs(thread_id: str, run_id: str, function_ids_to_result_map: Dict[str, str],
                              stream=False):
    tool_outputs = [{"tool_call_id": tool_id, "output": result if result is not None else ""} for tool_id, result in
                    function_ids_to_result_map.items()]

    logger.info(f"submitting tool outputs: {tool_outputs}")
    run = await client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run_id,
                                                             tool_outputs=tool_outputs,
                                                             stream=stream)

    return run


async def kill_if_thread_is_running(thread_id: str):
    runs = client.beta.threads.runs.list(
        thread_id=thread_id
    )

    running_threads = []
    async for run in runs:
        if run.status in ["in_progress", "queued", "requires_action", "cancelling"]:
            running_threads.append(run)

    async def kill_run(run_to_kill: Run):
        counter = 0
        try:
            while True:
                run_obj = await client.beta.threads.runs.retrieve(run_id=run_to_kill.id, thread_id=thread_id)
                run_status = run_obj.status
                if run_status == "cancelling":
                    logger.info(f"run {run_to_kill.id} is being cancelled, waiting for it to get cancelled")
                    await asyncio.sleep(2)
                    continue

                if run_status in ["cancelled", "failed", "completed", "expired"]:
                    logger.info(f"run {run_to_kill.id} is cancelled")
                    break

                run_obj = await client.beta.threads.runs.cancel(
                    thread_id=thread_id,
                    run_id=run_to_kill.id
                )

                if run_obj.status in ["cancelled", "failed", "expired"]:
                    logger.info(
                        f"run {run_obj.id} for thread {thread_id} is killed. status is {run_obj.status}")
                    break

                else:
                    logger.info(
                        f"run {run_obj.id} for thread {thread_id} is not yet killed. status is {run_obj.status}")
                    counter += 1
                    await asyncio.sleep(2)
                    continue

        except Exception:
            logger.exception(f"error in killing thread: {thread_id}")
            raise Exception(f"error in killing thread: {thread_id}")

    if not running_threads:
        logger.info(f"no running threads for thread : {thread_id}")
        return

    if running_threads:
        logger.info(f"total {len(running_threads)} running threads")
        tasks = []
        for run_obj in running_threads:
            task = asyncio.create_task(kill_run(run_obj))
            await asyncio.sleep(0)
            tasks.append(task)

        done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED, timeout=120)
        no_of_exceptions = 0

        for done_task in done:
            if done_task.exception() is None:
                task_result = done_task.result()
                if task_result:
                    logger.info(f"status of run kill task: {done_task} is {task_result}")

            else:
                if logger:
                    logger.exception(f"error in run kill task: {done_task}, "
                                     f"exception: {done_task.exception()}")

                no_of_exceptions += 1

        for pending_task in pending:
            logger.info(f"cancelling run kill task: {pending_task}")
            pending_task.cancel()

        if no_of_exceptions > 0 or pending:
            raise Exception("failed to kill running threads")

async def process_event(event, thread: Thread, **kwargs):
    if isinstance(event, ThreadMessageDelta):
        data = event.data.delta.content
        for text in data:
            yield text.text.value
            # print(text.text.value, end='', flush=True)

    elif isinstance(event, ThreadRunRequiresAction):
        run_obj = event.data
        function_ids_to_result_map = await handle_function_calls(run_obj)
        tool_output_events = await submit_tool_outputs(thread.id, run_obj.id, function_ids_to_result_map, stream=True)
        async for tool_event in tool_output_events:
            async for token in process_event(tool_event, thread=thread, **kwargs):
                yield token

    elif any(isinstance(event, cls) for cls in [ThreadRunFailed, ThreadRunCancelling, ThreadRunCancelled,
                                                ThreadRunExpired, ThreadRunStepFailed, ThreadRunStepCancelled]):
        raise Exception("Run failed")

    elif isinstance(event, ThreadRunCompleted):
        print("\nRun completed")

    # Handle other event types like ThreadRunQueued, ThreadRunStepInProgress, ThreadRunInProgress
    else:
        print("\nRun in progress")

async def chat_with_assistant(assistant: str, thread: Thread, user_query: str, **kwargs):
    # await kill_if_thread_is_running(thread_id=thread.id)
    message = await client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_query)
    logger.info(f"created message: {message}")

    stream = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant,
        stream=True
    )

    async for event in stream:
        async for token in process_event(event, thread, **kwargs):
            yield token

    print("\nTool output completed")

    print("*" * 100)

async def chat_with_assistant_file(assistant: str, thread: Thread, user_query: str, file_path: str, **kwargs):
    file_upload = await client.files.create(
        file=open(file_path, 'rb'),
        purpose='assistants',
    )
    logger.info(f"file uploaded: {file_upload}")

    message = await client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=user_query,
        attachments=[{'tools': [{"type": "file_search"}], 'file_id': file_upload.id}],
    )
    logger.info(f"created message: {message}")

    stream = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant,
        stream=True
    )

    async for event in stream:
        async for token in process_event(event, thread, **kwargs):
            yield token

    print("\nTool output completed")

    print("*" * 100)

async def create_thread() -> Thread:
    thread = await client.beta.threads.create()
    logger.info(f"created new thread: {thread.id}")
    return thread


def delete_thread(thread_id):
    thread_deleted = sync_client.beta.threads.delete(thread_id=thread_id)
    logger.info(f"deleted thread {thread_id}: {thread_deleted.deleted}")


async def main():
    # assistant = await create_assistant()
    thread = await create_thread()

    def signal_handler(sig, frame):
        print('Signal received, deleting thread and exiting...')
        delete_thread(thread_id=thread.id)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            query = input("Enter your query. (TYPE 'exit' TO STOP AND EXIT): ")

            if query.lower().strip() == "exit":
                break

            async for token in chat_with_assistant(assistant="assistant-id", thread=thread, user_query=query):
                print(token, end='')

        except Exception:
            logger.exception("error in chat: ")

    delete_thread(thread_id=thread.id)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

