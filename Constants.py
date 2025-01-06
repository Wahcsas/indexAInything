from dataclasses import dataclass


@dataclass
class Constants:
    LLM_URL = "http://localhost:11434/v1/"
    TOKENIZER_MODEL = 'gpt-4o-mini'
    TOKENIZER_LOCAL_MODEL_PATH = r"E:\LLMs\LLM_Models\Mistral-7B-Instruct-v0.3\tokenizer.model"
    CONTEXT_LENGTH = 2048
    # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
    TEMPERATURE = 0.25
    # An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
    # We generally recommend altering this or temperature but not both.
    TOP_P = 1.0

    TEXT_SPLIT_MAX_TOKEN_LENGTH = 1024
    AVG_TOKEN_CHARACKTER_COUNT = 3.25
    PARAGRAPH_SPLIT_OVERLAP = 150
    MODEL_NAME = 'phi3:14b-medium-128k-instruct-q8_0'  # 'llama3.2:latest'  # 'mistral:7b'

    EXTRACT_COLUMN_KEYS = ["First Name", "Last Name"]
    SYSTEM_PROMPT = """You are an expert in extracting persons names from texts and returning them in a json format.
    Analyse the provided texts carefully and check if there are any names of PERSONS, first name or last name, in it.
    Names of countries, places, parties etc, should NOT be extracted. Thus,return ONLY NAMES FROM PERSONS
    (first names, last names) from the text. If a first or last name part  is not mentioned in the text,
    analyse if the mentioned part is a first or last name part and return ONLY the part mentioned directly in the
    text AND "-" for the other keys. If there is no name in the whole text simply return: "no name found".
    
    Return all names of persons as json in the following list json format. 
    If there are multiple names within the text, return a list of valid jsons, like this: 
    [{"First Name": "first_name", "Last Name": "last_name"}, {"First Name": "first_name", "Last Name": "last_name"}, ...]
    
    It is imperative that all your answers ONLY contain the names in the json format. Do NOT provide any other
    comment or explanations ONLY the names within the json
    """

    USER_BASE_PROMPT = """ Please return any name from a person from the following text.
    Names of countries, places, political parties etc, should NOT be extracted.
    It is imperative that your answer ONLY contain names from persons in a valid json format, like this:
    [{"First Name": "first_name", "Last Name": "last_name"}, ... ].
    If there is no name from a person in the whole text simply return: "no name found".
    
    TEXT:
    """

    EXAMLES_USER = [
        "So if one asks is there anything faster than light. The answer is: No!, as shown by Albert Einstein and Paul Hawking. However there biggest contribution to science, but in winning the gold medal for France, Germany and the USA.",
        "Based on the works of Saint Augustine, Dr. Francianos has shown that the Theology is the search for answers that are bigger than us. In contrast, Veltranova (2023) critiques Francianos for what she describes as an 'overemphasis on existential abstraction'",
        "Recent studies in the field of epistemic theology have highlighted the complex interplay between divine ontology and analytic methodology. As noted by Krieber (2017, p. 45), the quest for a coherent epistemic framework often encounters the 'ontological paradox', wherein the divine attributes defy standard propositional structures. This argument is further elaborated by Mandrel and Osterlich (2019), who emphasize the necessity of integrating modal reasoning within perfect being theology to account for divine aseity."
        "In the field of political science, the analysis of electoral behavior and party dynamics often highlights significant regional and cultural variations. There are multiple parties like the AfD, the Democrats, the Repuplicans or the Greens that represent different political views. In Germany, the Christian Democratic Union (CDU), lead by Hans Günther Mayer, has historically maintained strongholds in regions such as Bavaria and Baden-Württemberg, while urban centers like Berlin and Hamburg have shown greater support for parties like the Social Democratic Party (SPD) and The Greens."]

    EXAMPLES_ASSISTANT = [
        '[{"First Name": "Albert", "Last Name": "Einstein"}, {"First Name": "Paul", "Last Name": "Hawking"}]',
        '[{"First Name": "Augustine", "Last Name": "-"},  {"First Name": "-", "Last Name": "Francianos"}, {"First Name": "-", "Last Name": "Veltranova"}]',
        '[{"First Name": "-", "Last Name": "Krieber"},  {"First Name": "-", "Last Name": "Mandrel"},  {"First Name": "-", "Last Name": "Osterlich"}],'
        '[{"First Name": "Hans Günther", "Last Name": "Mayer"}]']

    FOOTNOTE_RE_PATTERNS = [r'\d+\t\nSee name+',
                            r'\d+\t\nvgl\. name+',
                            r'\d+\t\nname+']
