from dataclasses import dataclass


@dataclass
class Constants:
    TOKENIZER_MODEL = r"E:\LLMs\LLM_Models\Mistral-7B-Instruct-v0.3\tokenizer.model"
    TOKENIZER_MODEL_TYPE = 'local'
    MAX_TOKEN_LENGTH = 3000
    AVG_TOKEN_CHARACKTER_COUNT = 3.25
    PARAGRAPH_SPLIT_OVERLAP = 150
    MODEL_NAME = 'Mistral-7B-Instruct-v0.3'
    SYSTEM_PROMPT = """You are an expert in extracting persons name from any text.
    Analyse the provided texts carefully and check if there is any name, first name or last name, in it.
    Return ALL person names (first names and last names) from the text. If a first or last name part is not mentioned
    in the text, analyse if the mentioned part is a first or last name and return ONLY the mentioned part and
    "UNKNOWN_Number" for the other part.
     
     Return all the names as comma separated list in a format, like this:
    first_name_1 last_name_1, first_name_2 last_name_2, UNKNOWN_3 last_name_3, etc.
    
    If there is no name in the whole text simply return "___".
    
    It is imperative that all your answer ONLY contain the names in a comma separated list. Do NOT provide any other
    comment or explanations ONLY the comma separated name list. 
    """

    USER_BASE_PROMPT = """ Please return any persons name from the following text.
    It is imperative that your answer ONLY contain the names in a comma separated list, in a format, like this:
    first_name_1 last_name_1, first_name_2 last_name_2, UNKNOWN_3 last_name_3, etc.
    
    TEXT:
    """