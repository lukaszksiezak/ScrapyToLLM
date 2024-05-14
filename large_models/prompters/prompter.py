from abc import ABC, abstractmethod

class Prompter(ABC):
    """
    Base class for prompters. Prompters are responsible for generating decorated prompts
    """
    _system_description = None

    def __init__(self, system_description):
        pass
    
    @abstractmethod
    def generate_prompt(self, text):
        """
        Generate a decorated prompt
        """
        raise NotImplementedError()