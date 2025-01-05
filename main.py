import gradio as gr
import pandas as pd
from Constants import Constants
from indexer.index_from_list import run_name_index
from utils import str_utils, prompt_utils
from API_Connector import openAI
from utils.json_utils import JsonStrToDict
from utils.other_utils import clean_pandas_df


def split_pdf_text(pdf_file: str):
    pdf_text = str_utils.get_total_pdf_text(pdf_file)
    split_to_tokens = str_utils.TextTokenSplitter()
    split_text: list = split_to_tokens.split_text_by_token_paragraphs(pdf_text)
    return split_text


def prompt_llm_for_persons(prompt_list):
    openAI_connector = openAI.ConnectOpenAI(dummy=False, url=Constants.LLM_URL)
    prompt_creator = prompt_utils.PromptCreator(Constants.SYSTEM_PROMPT)
    set_up_examples(prompt_creator)
    print(prompt_creator.get_prompt_history())
    names_list: list = []
    total_parts = len(prompt_list)

    dict_list: list = []
    json_parser = JsonStrToDict()
    for nr, prompt in enumerate(prompt_list):
        prompt_creator.add_user_prompt(Constants.USER_BASE_PROMPT + prompt)
        prompts = prompt_creator.get_prompt_history()
        print(f'Prompting for part {nr}/{total_parts} using {prompt_creator.count_tokens_in_prompt_history()} tokens')
        ai_response = openAI_connector.send_prompt(model=Constants.MODEL_NAME,
                                                   prompt=prompts,
                                                   top_p=1,
                                                   temp=1)
        print('AI RESPONSE is: ', ai_response)
        current_dict = json_parser.json_to_dict(ai_response)
        print(f'CURRENT dict is \n {current_dict}')

        if len(current_dict) > 0:
            print(f'Appending from {nr} with len: {len(current_dict)}')
            dict_list.append(current_dict)
        names_list.append(ai_response)
        prompt_creator.delete_prompt_history()

        #  add logic to search for and correct json then extract actual pdf page
    df_list = [pd.DataFrame(d) for d in dict_list]
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df = clean_pandas_df(combined_df)
    return combined_df


def set_up_examples(prompt_creator: prompt_utils.PromptCreator):
    for user_prompt, assistant_answer in zip(Constants.EXAMLES_USER, Constants.EXAMPLES_ASSISTANT):
        prompt_creator.add_user_prompt(user_prompt)
        prompt_creator.add_assistant_message(assistant_answer)


def index_for_names(pdf_file):
    split_text = split_pdf_text(pdf_file=pdf_file)
    print('Test_len: ', len(split_text), '\n EXT: ', split_text)
    names_df: pd.DataFrame = prompt_llm_for_persons(split_text)
    names_df['id'] = names_df[Constants.EXTRACT_COLUMN_KEYS[0]] + '_' + names_df[Constants.EXTRACT_COLUMN_KEYS[1]]
    names_df = names_df.set_index('id')
    name_to_pages = run_name_index(names_list=list(names_df.index), pdf_path=pdf_file, exclude_pages=[])
    return name_to_pages


def main():
    with gr.Blocks() as demo:
        with gr.Row():
            infile = gr.File(label='Document')
            output_text = gr.Textbox(value='')
        with gr.Column():
            start_btn = gr.Button('Start', variant='primary')
            start_btn.click(fn=index_for_names,
                            inputs=infile,
                            outputs=output_text
                            )

    demo.launch()


if __name__ == "__main__":
    main()



test_string_no_brackets = '{"First Name": "David", "Last Name": "Miller"}'
test_string= "[{'First Name': 'M. Steven', 'Last Name': 'Fish'}]"
json_parser = JsonStrToDict()
dict_list = []
for nr, text in enumerate([test_string_no_brackets, test_string]):
    current_dict = json_parser.json_to_dict(text)
    if len(current_dict) > 0:
            print(f'Appending from {nr} with len: {len(current_dict)}')
            dict_list.append(current_dict)
df_list = [pd.DataFrame(d) for d in dict_list]
combined_df = pd.concat(df_list, ignore_index=True)