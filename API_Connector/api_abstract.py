from abc import ABC, abstractmethod


class connectToAPI(ABC):
    def __init__(self, dummy, url):
        self.dummy = dummy
        self.url = url
        # load url etc here

    @abstractmethod
    def send_prompt(self, model: str, prompt: list[dict], top_p: float, temp: float):
        pass
