from langchain_core.prompts import ChatPromptTemplate
from .prompter import Prompter

class HackerNewsPrompter(Prompter):

    _system_description = None

    def __init__(self, system_description):
        self._system_description = system_description

    def generate_prompt(self, text):
        return ChatPromptTemplate.from_messages([
            ("system", self._system_description),
            ("user", "{input}")
        ])