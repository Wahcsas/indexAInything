from dataclasses import dataclass


@dataclass
class Constants:
    TOKENIZER_MODEL = r"E:\LLMs\LLM_Models\Mistral-7B-Instruct-v0.3\tokenizer.model"
    MAX_TOKEN_LENGTH = 1024
    AVG_TOKEN_CHARACKTER_COUNT = 3.25
    PARAGRAPH_SPLIT_OVERLAP = 150
    MODEL_NAME = 'Mistral-7B-Instruct-v0.3'
