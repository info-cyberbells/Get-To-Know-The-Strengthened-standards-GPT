import unittest
import os
import sys
import logging
import time
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestOpenAIConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("\nSetting up OpenAI connection tests...")
        try:
            # Load environment variables
            load_dotenv()
            cls.api_key = os.getenv('OPENAI_API_KEY')
            if not cls.api_key:
                raise ValueError("API key not found in environment variables")
            
            # Use the correct assistant ID directly
            cls.assistant_id = "asst_pYliV8MV2faRfHiWg3Z3Bfa1"
            cls.client = OpenAI(api_key=cls.api_key)
            cls.async_client = AsyncOpenAI(api_key=cls.api_key)
            logger.info("Setup complete.")
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            raise

    def test_assistant_id_exists(self):
        """Test that the Assistant ID exists and is not empty"""
        logger.info("\nTesting Assistant ID existence...")
        try:
            self.assertIsNotNone(self.assistant_id, "Assistant ID is not set")
            self.assertNotEqual(self.assistant_id, "", "Assistant ID is empty")
            logger.info(f"Assistant ID exists and is not empty: {self.assistant_id}")
        except Exception as e:
            logger.error(f"Assistant ID test failed: {str(e)}")
            raise

    def test_list_assistants(self):
        """Test that we can list assistants"""
        logger.info("\nTesting listing all assistants...")
        try:
            assistants = self.client.beta.assistants.list()
            self.assertIsNotNone(assistants, "Failed to list assistants")
            logger.info("Available assistants:")
            for assistant in assistants.data:
                logger.info(f"- ID: {assistant.id}")
                logger.info(f"  Name: {assistant.name}")
                logger.info(f"  Created at: {assistant.created_at}")
                logger.info(f"  Model: {assistant.model}")
                if hasattr(assistant, 'instructions'):
                    logger.info(f"  Instructions: {assistant.instructions}")
        except Exception as e:
            logger.error(f"List assistants test failed: {str(e)}")
            raise

    def test_assistant_exists(self):
        """Test that the Assistant ID is valid and can be retrieved"""
        logger.info("\nTesting Assistant retrieval...")
        try:
            assistant = self.client.beta.assistants.retrieve(self.assistant_id)
            self.assertIsNotNone(assistant, "Failed to retrieve assistant")
            self.assertEqual(assistant.id, self.assistant_id, "Retrieved assistant ID doesn't match")
            logger.info(f"Successfully retrieved assistant:")
            logger.info(f"- ID: {assistant.id}")
            logger.info(f"- Name: {assistant.name}")
            logger.info(f"- Created at: {assistant.created_at}")
            if hasattr(assistant, 'instructions'):
                logger.info(f"- Instructions: {assistant.instructions}")
        except Exception as e:
            logger.error(f"Assistant retrieval test failed: {str(e)}")
            raise

    def test_thread_creation(self):
        """Test creating a thread"""
        logger.info("\nTesting thread creation...")
        try:
            # Create a thread
            thread = self.client.beta.threads.create()
            self.assertIsNotNone(thread, "Failed to create thread")
            logger.info(f"Created thread: {thread.id}")

            # Clean up
            deletion = self.client.beta.threads.delete(thread.id)
            self.assertTrue(deletion.deleted, "Failed to delete thread")
            logger.info("Successfully deleted thread")
        except Exception as e:
            logger.error(f"Thread creation test failed: {str(e)}")
            raise

    def test_message_creation(self):
        """Test creating a message in a thread"""
        logger.info("\nTesting message creation...")
        try:
            # Create a thread
            thread = self.client.beta.threads.create()
            self.assertIsNotNone(thread, "Failed to create thread")
            logger.info(f"Created thread: {thread.id}")

            # Create a message
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="What are the Aged Care Quality Standards?"
            )
            self.assertIsNotNone(message, "Failed to create message")
            logger.info(f"Created message: {message.id}")

            # Clean up
            deletion = self.client.beta.threads.delete(thread.id)
            self.assertTrue(deletion.deleted, "Failed to delete thread")
            logger.info("Successfully deleted thread")
        except Exception as e:
            logger.error(f"Message creation test failed: {str(e)}")
            raise

    def test_complete_interaction(self):
        """Test a complete interaction with the assistant"""
        logger.info("\nTesting complete interaction with assistant...")
        try:
            # Create a thread
            thread = self.client.beta.threads.create()
            self.assertIsNotNone(thread, "Failed to create thread")
            logger.info(f"Created thread: {thread.id}")

            # Create a message
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="What are the Aged Care Quality Standards?"
            )
            self.assertIsNotNone(message, "Failed to create message")
            logger.info(f"Created message: {message.id}")

            # Create a run
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            self.assertIsNotNone(run, "Failed to create run")
            logger.info(f"Created run: {run.id}")

            # Wait for run to complete
            while run.status in ['queued', 'in_progress']:
                logger.info(f"Run status: {run.status}")
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

            logger.info(f"Final run status: {run.status}")
            
            if run.status == 'completed':
                # Get the assistant's response
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                for msg in messages.data:
                    if msg.role == "assistant":
                        logger.info("\nAssistant's response:")
                        for content in msg.content:
                            if hasattr(content, 'text'):
                                logger.info(content.text.value)

            # Clean up
            deletion = self.client.beta.threads.delete(thread.id)
            self.assertTrue(deletion.deleted, "Failed to delete thread")
            logger.info("Successfully deleted thread")
        except Exception as e:
            logger.error(f"Complete interaction test failed: {str(e)}")
            raise

if __name__ == '__main__':
    try:
        unittest.main(verbosity=2)
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        sys.exit(1)
