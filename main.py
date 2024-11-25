import gradio as gr

from Constants import Constants
from utils import str_utils, prompt_utils
from API_Connector import openAI


def split_pdf_text(pdf_file: str):
    pdf_text = str_utils.get_pdf_text(pdf_file)
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
    for nr, prompt in enumerate(prompt_list):
        prompt_creator.add_user_prompt(Constants.USER_BASE_PROMPT + prompt)
        prompts = prompt_creator.get_prompt_history()
        print(f'Prompting for part {nr}/{total_parts} using {prompt_creator.count_tokens_in_prompt_history()} tokens')
        ai_response = openAI_connector.send_prompt(model=Constants.MODEL_NAME,
                                                   prompt=prompts,
                                                   top_p=1,
                                                   temp=1)
        names_list.append(ai_response)
        prompt_creator.delete_prompt_history()
        print(ai_response)
    return names_list


def set_up_examples(prompt_creator:prompt_utils.PromptCreator):
    for user_prompt, assistant_answer in zip(Constants.EXAMLES_USER, Constants.EXAMPLES_ASSISTANT):
        prompt_creator.add_user_prompt(user_prompt)
        prompt_creator.add_assistant_message(assistant_answer)



def index_for_names(pdf_file):
    split_text = split_pdf_text(pdf_file=pdf_file)
    print('Test_len: ',len(split_text), '\n EXT: ', split_text)
    names: list = prompt_llm_for_persons(split_text)
    return names


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
