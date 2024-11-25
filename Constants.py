from dataclasses import dataclass


@dataclass
class Constants:
    LLM_URL = "http://localhost:11434/v1/"
    TOKENIZER_MODEL = 'gpt-4o-mini'
    TOKENIZER_LOCAL_MODEL_PATH = r"E:\LLMs\LLM_Models\Mistral-7B-Instruct-v0.3\tokenizer.model"
    MAX_TOKEN_LENGTH = 4096
    AVG_TOKEN_CHARACKTER_COUNT = 3.25
    PARAGRAPH_SPLIT_OVERLAP = 150
    MODEL_NAME = 'llama3.2:latest'
    SYSTEM_PROMPT = """You are an expert in extracting persons name from any text.
    Analyse the provided texts carefully and check if there is any name, first name or last name, in it.
    Return ALL person names (first names, last names and titles, e.g. PhD) from the text. If a first or last name part 
    is not mentioned in the text, analyse if the mentioned part is a first or last name part and return ONLY the part
    mentioned directly in the text AND "-" for the other keys.
    
    Return all names as json in the following format: [{"First Name": "first_name", "Last Name": "last_name"]
    If there is no name in the whole text simply return "-" as values of the json keys.
    If there are multiple names within the text, return a list of jsons.
    
    It is imperative that all your answer ONLY contain the names in as json. Do NOT provide any other
    comment or explanations ONLY the names within the json
    """

    USER_BASE_PROMPT = """ Please return any persons name from the following text.
    It is imperative that your answer ONLY contain the names in as a json format, like this:
    {"First Name": "first_name", "Last Name": "last_name"}
    
    TEXT:
    """

    EXAMLES_USER = [
        "So if one asks is there anything faster than light. The answer is: No!, as shown by Albert Einstein",
        "Based on the works of Saint Augustine, Dr. Francianos has shown that the Theology is the search for answers that are bigger than us"]

    EXAMPLES_ASSISTANT = ['[{"First Name": "Albert", "Last Name": "Einstein"]',
                          '[{"First Name": "Augustine", "Last Name": "-"}],  [{"First Name": "-", "Last Name": "Francianos"]']
