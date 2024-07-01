
from copy import deepcopy



class PromptCreator:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.prompt_history = [self.set_system_prompt()]


    def set_system_prompt(self):
        return self._create_prompt(content=self.system_prompt)
    def add_user_prompt(self, content):
        user_prompt = self._create_prompt(content=content,
                                          role='user')
        self.prompt_history.append()



    @staticmethod
    def _create_prompt(content: str,
                       role: str = 'system'):
        return {"role": role, "content": content}

