from utils.token_counter import TokenCounter

class PromptCreator:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.prompt_history = [self.set_system_prompt()]
        self.token_counter = TokenCounter(count_typ='local')

    def get_prompt_history(self):
        return self.prompt_history

    def set_system_prompt(self):
        return self._create_prompt(content=self.system_prompt)

    def add_user_prompt(self, content):
        user_prompt = self._create_prompt(content=content,
                                          role='user')
        self.prompt_history.append(user_prompt)

    def add_assistant_message(self, content):
        assistant_prompt = self._create_prompt(content=content,
                                          role='assistant')
        self.prompt_history.append(assistant_prompt)

    def delete_prompt_history(self):
        self.prompt_history = [self.set_system_prompt()]

    def delete_last_prompt_history_element(self):
        self.prompt_history.pop(-1)

    @staticmethod
    def _create_prompt(content: str,
                       role: str = 'system'):
        return {"role": role, "content": content}

    def count_tokens_in_prompt_history(self):
        return sum([self.token_counter.count_tokens(p['content']) for p in self.prompt_history])



if __name__ == "__main__":
    p = PromptCreator('Your are a helpful AI! Thus help.')
    p.add_user_prompt('How many bridges must a man cross before you can call him a man!')
    p.add_assistant_message("I don't know the answer. But I think it is blowing in the wind")
    print(p.get_prompt_history())
