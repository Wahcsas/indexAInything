import pathlib

import pymupdf
import re
from Constants import Constants


def read_pdf_pages(pdf_path: str | pathlib.Path) -> dict[int:str]:
    """
    Reads a PDF file and extracts text from each page.

    :param pdf_path: The path to the PDF file.
    :type pdf_path: str
    :return: A dictionary where keys are page numbers (starting from 1) and values are the extracted text.
    :rtype: dict
    """
    # Open the PDF file
    doc = pymupdf.open(pdf_path)
    pdf_text = {}

    # Extract text from each page
    for page in doc:
        text = page.get_text()
        page_number = page.number + 1  # Page numbers are zero-indexed in PyMuPDF
        pdf_text[page_number] = text

    doc.close()
    return pdf_text


def find_name_pages(names: list, pdf_pages: dict, exclude_pages: list, footnote_patterns: list[str]) -> dict[
                                                                                                        str:list[int]]:
    name_pages = {name: [] for name in names}

    for name in names:
        parts = name.split('_')
        last_name = parts[0] if len(parts[0]) > 0 else ''
        first_name = parts[1] if len(parts) > 1 and len(parts[1]) > 0 else ''

        # Pattern to match full name, last name, and possessive forms, but not as part of footnotes
        name_pattern = rf'\b{last_name}(?:,?\s+{first_name})?\b|\b{first_name}\s+{last_name}\b'
        name_regex = re.compile(name_pattern, re.IGNORECASE)

        footnotes_reg_with_name = [n.replace('name', last_name) for n in footnote_patterns]
        # Prepare regex for footnotes
        footnote_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in footnotes_reg_with_name]

        for page_number, text in pdf_pages.items():
            if page_number in exclude_pages:
                continue  # Skip excluded pages

            # First check the entire text for the name
            if name_regex.search(text):
                # Check specifically for footnotes
                if any(footnote_regex.search(text) for footnote_regex in footnote_regexes):
                    # If found in footnotes, check if also found outside of the footnotes, by trying to find the
                    # shortest text for each individual split via footnote_regex, we find the text WITHOUT the footnotes
                    text_without_footnotes = min(footnote_regex.split(text)[0] for footnote_regex in footnote_regexes)
                    if name_regex.search(text_without_footnotes):
                        name_pages[name].append(page_number)
                else:
                    name_pages[name].append(page_number)
            # If not found in the main text, don't add the page number even if found in the footnote
    # make pages unique
    name_pages = {name: set(pages) for name, pages in name_pages.items() if len(pages) > 0}
    return name_pages


def run_name_index(pdf_path: str, names_list: list, exclude_pages: list) -> dict[str:list[int]]:
    # Extract names and read PDF
    pdf_pages = read_pdf_pages(pdf_path)

    # Use the function to find the pages for each name
    name_to_pages = find_name_pages(names=names_list, pdf_pages=pdf_pages,
                                    exclude_pages=exclude_pages, footnote_patterns=Constants.FOOTNOTE_RE_PATTERNS)

    return name_to_pages
