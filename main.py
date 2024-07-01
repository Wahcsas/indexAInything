import gradio as gr

from utils import str_utils
from API_Connector import openAI


def split_pdf_text(pdf_file: str):
    pdf_text = str_utils.get_pdf_text(pdf_file)
    split_to_tokens = str_utils.TextTokenSplitter()
    split_text: list = split_to_tokens.split_text_by_token_paragraphs(pdf_text)
    return split_text


def prompt_list_to_llm(base_prompt, prompt_list):
    openAI_connector = openAI.ConnectOpenAI()
    # for prompt in prompt_list:


def main():
    with gr.Blocks() as demo:
        with gr.Row():
            infile = gr.File(label='Document')
            output_text = gr.Textbox(value='')
        with gr.Column():
            start_btn = gr.Button('Start', variant='primary')
            start_btn.click(fn=split_pdf_text,
                            inputs=infile,
                            outputs=output_text
                            )

    demo.launch()


if __name__ == "__main__":
    main()
