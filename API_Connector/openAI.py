import os

import openai
import os
from API_Connector.api_abstract import connectToAPI

os.environ['OPENAI_API_KEY'] = 'xxx'


class ConnectOpenAI(connectToAPI):
    def __init__(self, dummy, url):
        super().__init__(dummy, url)
        openai.api_key = "EMPTY"
        openai.base_url = "http://localhost:8000/v1/"
        # try to use openaio client ???

    def send_prompt(self, model: str, prompt: list[dict], top_p: float = 1, temp: float = 1) -> str:
        print(prompt)
        response = openai.chat.completions.create(model=model,
                                                  messages=prompt,
                                                  stream=False,
                                                  top_p=top_p,
                                                  temperature=temp)

        return response.choices[0].message.content


if __name__ == "__main__":
    api_connection = ConnectOpenAI(dummy=False, url='http://localhost:8000/v1/')
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain asynchronous programming in the style of the pirate Blackbeard."}
    ]

    answer = api_connection.send_prompt(model='WestLake-7B-v2',
                                        prompt=messages)
    print(answer)
