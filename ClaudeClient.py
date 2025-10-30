from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

class Client:
    def __init__(self):
        self.api = os.getenv("CLAUDE_API")
        self.client = Anthropic(api_key=self.api)