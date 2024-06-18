from api_abstract import connectToAPI


class DummyAPI(connectToAPI):

    def send_prompt(self, model: str, prompt: list[dict], top_p: float, temp: float):
        return print(prompt[-1]['content'] + 'to' + model + 'from url' + str(self.url))
