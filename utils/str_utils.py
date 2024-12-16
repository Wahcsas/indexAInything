import math

import pymupdf

from Constants import Constants
from utils.token_counter import TokenCounter





#[json.loads(x) for x in a]


def get_pdf_text(pdf_file: str):
    doc = pymupdf.open(pdf_file)
    text_pages: list = [page.get_text() for page in doc]
    pure_text: str = ' '.join(text_pages)
    return pure_text


def split_with_overlap(elemet_to_split: str | list, num_parts: int, overlap: int) -> list:
    """
    Splits a given string or list into a specified number of parts with an overlap between consecutive parts.

    This function divides the input element into `num_parts` where each part is of approximately equal size,
    but allowing the specified number of overlapping elements (`overlap`) between consecutive parts.

    :param elemet_to_split: (str | list): The input element to split. It can be either a string or a list.
    :param num_parts: (int): The number of parts to divide the input into.
    :param overlap: (int): The number of elements that should overlap between consecutive parts.

    :return: list:  A list of parts, where each part is a substring (if the input is a string)
    or sublist (if the input is a list) from the original input, considering the specified overlap.
    """
    length = len(elemet_to_split)
    part_size = (length + (num_parts - 1) * overlap) // num_parts
    result = []
    for part in range(num_parts):
        start = max(0, part * (part_size - overlap))
        end = min(length, start + part_size)
        result.append(elemet_to_split[start:end])
    return result


def clean_text(text:str, clean_side='both'):
    """
    Cleans the input text by removing spaces from the specified side(s).

    :param text:  The input string to be cleaned.
    :param clean_side: The side from which to remove spaces. Can be 'start', 'end', or 'both'.
                       - 'start': Removes spaces from the start of the text.
                       - 'end': Removes spaces from the end of the text.
                       - 'both': Removes spaces from both the start and end of the text.
                       Default is 'both'.
    :return: The cleaned text with spaces removed from the specified side(s)
    """
    start = text.find(' ')
    end = text.rfind(' ')
    if clean_side == 'start':
        return text[start:].strip()
    elif clean_side == 'end':
        return text[:end].strip()
    elif clean_side == 'both':
        return text[start:end].strip()


class TextTokenSplitter:
    def __init__(self):
        self.text = None

    def split_text_by_token_paragraphs(self, text: str) -> list:
        """
        Splits a given text into chunks where each chunk is a paragraph or a part of a paragraph based on the maximum
        token length constraint. If a single paragraph exceeds the maximum token length, it will be further split with overlap.

        Args:
            text (str): The input text to be split into chunks.

        Returns:
            list: A list of text chunks that conform to the token length requirements.
        """
        self.text = text
        paragraphs = self._split_into_paragraphs()
        tokens_per_paragraph = self._count_tokens_in_paragraphs(paragraphs)
        paragraphs_fitted: list = []

        current_chunk: str = ""
        for tokens, paragraph in zip(tokens_per_paragraph, paragraphs):
            if tokens == 0:
                continue
            if len(current_chunk) + tokens + 2 < Constants.MAX_TOKEN_LENGTH:  # +2 for potential new lines
                current_chunk = self._join_paragraph(current_chunk, paragraph)
            else:
                paragraphs_fitted.extend(self._process_large_paragraph(current_chunk, paragraph, tokens))
                current_chunk: str = ""  # Reset after processing

        if current_chunk:
            paragraphs_fitted.append(current_chunk)

        return paragraphs_fitted

    def _split_into_paragraphs(self) -> list:
        split_texts = self.text.split('\n')
        split_texts = [split.strip() for split in split_texts if len(split) > 0]
        return split_texts

    @staticmethod
    def _count_tokens_in_paragraphs(paragraphs: list) -> list:
        token_counter = TokenCounter()
        return [token_counter.count_tokens(para) for para in paragraphs]

    @staticmethod
    def _join_paragraph(current_chunk: str, paragraph: str) -> str:
        return current_chunk + "\n" + paragraph if current_chunk else paragraph

    def _process_large_paragraph(self, current_chunk: str, paragraph: str, tokens: int) -> list:
        chunks = []
        if current_chunk:
            chunks.append(current_chunk)
        if tokens > Constants.MAX_TOKEN_LENGTH:
            chunks.extend(self._split_and_clean_paragraph(paragraph, tokens))
        else:
            chunks.append(paragraph)
        return chunks

    def _split_and_clean_paragraph(self, paragraph, tokens):
        required_splits = math.ceil(tokens / Constants.MAX_TOKEN_LENGTH)
        chunks = split_with_overlap(elemet_to_split=paragraph, num_parts=required_splits,
                                    overlap=Constants.PARAGRAPH_SPLIT_OVERLAP)
        cleaned_chunks = self._clean_text_chunks(chunks)
        return cleaned_chunks

    @staticmethod
    def _clean_text_chunks(chunks):
        cleaned_chunks: list = []
        clean_first_chunk = clean_text(chunks[0], 'end')  # remove only letters from start of first chunk
        cleaned_chunks.append(clean_first_chunk)
        for chunk in chunks[1:-1]:
            cleaned_chunks.append(clean_text(chunk, 'both'))
        clean_last_chunk = clean_text(chunks[-1], 'start')  # remove only letters from end of last chunk
        cleaned_chunks.append(clean_last_chunk)
        return cleaned_chunks


if __name__ == "__main__":
    # Example usage:
    Constants.MAX_TOKEN_LENGTH = 50
    Constants.PARAGRAPH_SPLIT_OVERLAP = 10
    test_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin eget vehicula risus. Pellentesque 
    habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum tortor quam, 
    feugiat vitae, ultricies eget, tempor sit amet, ante. Donec eu libero sit amet quam egestas semper. Aenean 
    ultricies mi vitae est. Mauris placerat eleifend leo. Quisque sit amet est et sapien ullamcorper pharetra. 
    Vestibulum erat wisi, condimentum sed, commodo vitae, ornare sit amet, wisi.
        
    Aenean fermentum, elit eget tincidunt condimentum, eros ipsum rutrum orci, sagittis tempus lacus enim ac dui. 
    Donec non enim in turpis pulvinar facilisis. Ut felis. Praesent dapibus, neque id cursus faucibus, tortor neque 
    egestas augue, eu vulputate magna eros eu erat. Aliquam erat volutpat. Nam dui mi, tincidunt quis, 
    accumsan porttitor, facilisis luctus, metus."""

    text_parts = TextTokenSplitter().split_text_by_token_paragraphs(test_text)
    token_counter = TokenCounter(count_typ='openAI')
    total_text_tokens = token_counter.count_tokens(test_text)
    print('OPEN AI TOTAL TEXT TOKENS: ', total_text_tokens)
    for i, chunk in enumerate(text_parts):
        print('TOKENS: ', token_counter.count_tokens(chunk))
        print(f"Chunk {i + 1}:\n{chunk}\n")

    print('---------------------------------')

    token_counter = TokenCounter(count_typ='estimate')
    total_text_tokens = token_counter.count_tokens(test_text)
    print('ESTIMATED TOTAL TEXT TOKENS: ', total_text_tokens)
    for i, chunk in enumerate(text_parts):
        print('TOKENS: ', token_counter.count_tokens(chunk))
        print(f"Chunk {i + 1}:\n{chunk}\n")



