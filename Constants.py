from dataclasses import dataclass


@dataclass
class Constants:
    LLM_URL = "http://localhost:11434/v1/"
    TOKENIZER_MODEL = 'gpt-4o-mini'
    TOKENIZER_LOCAL_MODEL_PATH = r"E:\LLMs\LLM_Models\Mistral-7B-Instruct-v0.3\tokenizer.model"
    CONTEXT_LENGTH = 2048
    # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
    TEMPERATURE = 0.0
    # An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
    # We generally recommend altering this or temperature but not both.
    TOP_P = 1.0

    TEXT_SPLIT_MAX_TOKEN_LENGTH = 768
    AVG_TOKEN_CHARACKTER_COUNT = 3.25
    PARAGRAPH_SPLIT_OVERLAP = 150
    MODEL_NAME = 'magistral:24b'#'llama3.2:latest' #'phi3:14b-medium-128k-instruct-q8_0'  # 'llama3.2:latest'  # 'mistral:7b'

    EXTRACT_COLUMN_KEYS = ["First_Name", "Last_Name"]
    SYSTEM_PROMPT = """You are an expert in extracting person full names, i.e. first name and last name from texts.
    All names have to be returned via a function tool call and json format like this:
    final_result({"names":[{"First_Name":"...","Last_Name":"..."}]})
    
    Analyse the provided texts carefully and check if there are any quotation or references any persons first name or last name, in it.
    If a first or last name part  is not mentioned in the text, analyse if the mentioned part is a first or last name
    part and return ONLY the part mentioned directly in the text and "-" for the other keys.
    If there are no person names, output exactly this and nothing else (no explanation, no extra whitespace):
    final_result({"names":[]})

    Do NOT extract organizations, countries, places, parties, or other non-person entities.    
    Do answer in a free-form text; go straight to the structured call, 
    
    In short: Extract all **person** full names only and return them in the following tool calling json format.
    Examples:
    Input: "I spoke with Alice Johnson and the UNICEF team in Geneva."
    Output: final_result({"names":[{"First_Name":"Alice","Last_Name":"Johnson"}]})
    
    Input: "The conference was hosted by Spain and attended by delegates."
    Output: final_result({"names":[]})
    
    Input: "Augustinus schrieb eine Autobiographie in Afrika und Isaak Newton sein Büch über die Schwerkraft in Cambridge, England"
    Output: final_result({"names":[{"First_Name":"Augustinus","Last_Name":"-"},{"First_Name":"Isaak","Last_Name":"Newton"}]})
    
    Input: "Met Dr. Bob Lee and CEO Clara Smith from OpenAI."
    Output: final_result({"names":[{"First_Name":"Bob","Last_Name":"Lee"},{"First_Name":"Clara","Last_Name":"Smith"}]})"""

    USER_BASE_PROMPT = """ Reminder: Respond only by calling final_result(...) with JSON; do not give free-form prose first.
    Please extract persons names from the following text: \n """



    FOOTNOTE_RE_PATTERNS = [r'vgl\.\sname+',
                            r'Vgl\.\sname+'
                            r'in:\sname+',
                            r'\d+\tname+',
                            r'\d+\sname+',
                            ]
