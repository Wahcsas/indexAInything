import gradio as gr
import pandas as pd
from Constants import Constants
from indexer.index_from_list import run_name_index
from utils import str_utils
from utils.pydantic_agent_system import NameExtractionAgent
from utils.other_utils import clean_pandas_df


def split_pdf_text(pdf_file: str):
    pdf_text = str_utils.get_total_pdf_text(pdf_file)
    split_to_tokens = str_utils.TextTokenSplitter()
    split_text: list = split_to_tokens.split_text_by_token_paragraphs(pdf_text)
    return split_text


def prompt_llm_for_persons(prompt_list):
    agent = NameExtractionAgent()
    dict_list: list = []
    for prompt in prompt_list:
        current_dict = agent.process_chunk(prompt)
        if current_dict:
            dict_list.append(current_dict)

    if not dict_list:
        return pd.DataFrame(columns=Constants.EXTRACT_COLUMN_KEYS)

    df_list = [pd.DataFrame(d) for d in dict_list]
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df = clean_pandas_df(combined_df)
    return combined_df



def index_for_names(pdf_file) -> pd.DataFrame:
    split_text = split_pdf_text(pdf_file=pdf_file)
    print('Test_len: ', len(split_text), '\n EXT: ', split_text)
    names_df: pd.DataFrame = prompt_llm_for_persons(split_text)
    names_df['id'] = names_df[Constants.EXTRACT_COLUMN_KEYS[0]] + '_' + names_df[Constants.EXTRACT_COLUMN_KEYS[1]]
    # DROP TOTAL DUPLICATES
    names_df = names_df.drop_duplicates(subset=['id'])
    names_df = names_df.set_index('id')
    name_to_pages = run_name_index(names_list=list(names_df.index), pdf_path=pdf_file, exclude_pages=[], pages_offset=19)
    names_df['pages'] = names_df.index.map(name_to_pages)
    # drop NAN. None, null values and EMPTY list, i.e. not found
    names_df = names_df.dropna(subset=['pages'])
    names_df = names_df[~names_df['pages'].str.len().eq(0)]
    return names_df


def main():
    with gr.Blocks() as demo:
        with gr.Row():
            infile = gr.File(label='Document')
            output_table = gr.DataFrame()
        with gr.Column():
            start_btn = gr.Button('Start', variant='primary')
            start_btn.click(fn=index_for_names,
                            inputs=infile,
                            outputs=output_table
                            )

    demo.launch()


if __name__ == "__main__":
    main()