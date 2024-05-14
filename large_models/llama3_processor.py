from langchain_community.llms import Ollama

class Llama3Processor:
    def __init__(self):
        self.ollama = Ollama(model="llama3")

    def process(self, text):
        return self.ollama.invoke(text)