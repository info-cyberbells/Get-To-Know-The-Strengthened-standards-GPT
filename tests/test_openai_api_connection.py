import unittest
import os
from dotenv import load_dotenv
from openai import OpenAI

class TestOpenAIConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\nSetting up OpenAI connection tests...")
        # Load environment variables
        load_dotenv()
        cls.api_key = os.getenv('OPENAI_API_KEY')
        cls.assistant_id = os.getenv('ASSISTANT_ID')
        cls.client = OpenAI(api_key=cls.api_key)
        print("Setup complete.")

    def test_api_key_exists(self):
        """Test that the API key exists and is not empty"""
        print("\nTesting API key existence...")
        self.assertIsNotNone(self.api_key, "API key is not set in .env file")
        self.assertNotEqual(self.api_key, "", "API key is empty")
        print(f"API key exists and is not empty: {self.api_key[:8]}...")

    def test_api_connection(self):
        """Test that we can connect to OpenAI API"""
        print("\nTesting OpenAI API connection...")
        try:
            # Try to list models as a simple API test
            models = self.client.models.list()
            self.assertIsNotNone(models, "Failed to get models list")
            print("Successfully connected to OpenAI API")
        except Exception as e:
            self.fail(f"Failed to connect to OpenAI API: {str(e)}")

if __name__ == '__main__':
    unittest.main()
