import unittest
import os
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TestLangchainConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\nSetting up Langchain connection tests...")
        load_dotenv()
        cls.api_key = os.getenv('LANGCHAIN_API_KEY')
        print("Setup complete.")

    def test_api_key_exists(self):
        """Test that the Langchain API key exists and is not empty"""
        print("\nTesting Langchain API key existence...")
        self.assertIsNotNone(self.api_key, "Langchain API key is not set in .env file")
        self.assertNotEqual(self.api_key, "", "Langchain API key is empty")
        print(f"Langchain API key exists and is not empty")

    def test_embeddings_creation(self):
        """Test creating embeddings using Langchain"""
        print("\nTesting embeddings creation...")
        try:
            embeddings = OpenAIEmbeddings()
            test_text = "This is a test text for embeddings."
            result = embeddings.embed_query(test_text)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)
            self.assertTrue(len(result) > 0)
            print("Successfully created embeddings")
        except Exception as e:
            self.fail(f"Failed to create embeddings: {str(e)}")

    def test_text_splitter(self):
        """Test text splitting functionality"""
        print("\nTesting text splitter...")
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=100,
                chunk_overlap=20,
                length_function=len,
            )
            test_text = "This is a test text. " * 10  # Create a longer text
            chunks = text_splitter.split_text(test_text)
            self.assertIsNotNone(chunks)
            self.assertIsInstance(chunks, list)
            self.assertTrue(len(chunks) > 1)  # Should split into multiple chunks
            print("Successfully split text into chunks")
        except Exception as e:
            self.fail(f"Failed to split text: {str(e)}")

if __name__ == '__main__':
    unittest.main()
