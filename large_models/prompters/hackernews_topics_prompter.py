from langchain_core.prompts import ChatPromptTemplate
from .prompter import Prompter

class HackerNewsTopicsPrompter(Prompter):

    _available_topics = None

    def __init__(self, available_topics):
        self._available_topics = available_topics

    def generate_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", f"You are an AI assistant which supports a user in choosing the most interesting topic for him. Here's a list of topics he can access (comma separated): {self._available_topics}"),
            ("user", "{input}")
        ])