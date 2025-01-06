from utils.token_counter import TokenCounter


class PromptCreator:
    """
    A class for creating and managing conversational prompts, including user, assistant, and system prompts.

    :param system_prompt: The initial system prompt content that serves as the foundation of the conversation.
    :type system_prompt: str
    """

    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self.prompt_history = [self.set_system_prompt()]
        self.token_counter = TokenCounter(count_typ='local')

    def get_prompt_history(self) -> list:
        """
        Retrieve the full prompt history, which includes the system prompt and all user/assistant messages.
        :return: A list of dictionaries representing the conversation history.
        :rtype: list
        """
        return self.prompt_history

    def set_system_prompt(self, system_prompt: str = None) -> dict:
        """
        Set and return the formatted system prompt. If a new system prompt is provided,
        it updates the stored system prompt and sets it as new default value

        :return: A dictionary representing the system prompt.
        :rtype: dict
        """
        if not system_prompt:
            system_prompt = self.system_prompt
        else:
            self.system_prompt = system_prompt
        return self._create_prompt(content=system_prompt)

    def add_user_prompt(self, content) -> None:
        """
        Add a user prompt to the prompt history.

        :param content: The content of the user's message.
        :type content: str
        """
        user_prompt = self._create_prompt(content=content,
                                          role='user')
        self.prompt_history.append(user_prompt)

    def add_assistant_message(self, content) -> None:
        """
        Add an assistant response to the prompt history.

        :param content: The content of the assistant's message.
        :type content: str
        """
        assistant_prompt = self._create_prompt(content=content,
                                               role='assistant')
        self.prompt_history.append(assistant_prompt)

    def delete_prompt_history(self, delete_system_prompt=False):
        """
        Delete the entire prompt history default behaviour except for the system prompt.
        if delete_system_prompt is set to true the system prompt is also deleted

        :return: None
        """
        if delete_system_prompt:
            self.prompt_history = []
        else:
            self.prompt_history = [self.set_system_prompt()]

    def delete_last_prompt_history_element(self):
        self.prompt_history.pop(-1)

    @staticmethod
    def _create_prompt(content: str,
                       role: str = 'system') -> dict:
        return {"role": role, "content": content}

    def count_tokens_in_prompt_history(self):
        return sum([self.token_counter.count_tokens(p['content']) for p in self.prompt_history])


if __name__ == "__main__":
    p = PromptCreator(system_prompt='Your are a helpful AI! Thus help.')
    p.add_user_prompt('How many bridges must a man cross before you can call him a man!')
    p.add_assistant_message("I don't know the answer. But I think it is blowing in the wind")
    print(p.get_prompt_history())
