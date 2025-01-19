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


def filter_positive_matches(text, positive_pattern, negative_patterns,
                            context_window_before=10, context_window_after=10, ignore_case=True) -> list:
    """
    Finds matches of the positive pattern in text and filters out those that match any of the negative patterns.

    :param text: The text to search within.
    :param positive_pattern: Regex pattern for the positive matches.
    :param negative_patterns: List of regex patterns to exclude.
    :param context_window_before: Number of characters before the match to check for negative patterns.
    :param context_window_after: Number of characters after the match to check for negative patterns.
    :param ignore_case: Whether to perform case-insensitive matching.
    :return: List of filtered matches (strings).
    """
    # Compile regex patterns with or without ignore case flag
    flags = re.IGNORECASE if ignore_case else 0
    positive_pattern_compiled = re.compile(positive_pattern, flags)
    negative_patterns_compiled = [re.compile(neg, flags) for neg in negative_patterns]

    # Step 1: Find all occurrences of the positive pattern
    matches = positive_pattern_compiled.finditer(text)

    filtered_matches = []

    for match in matches:
        start, end = match.span()

        # Step 2: Check if any negative pattern matches the specified context window around the match
        is_negative = False
        for neg in negative_patterns_compiled:
            context_to_check = text[max(0, start - context_window_before):end + context_window_after]
            if neg.search(context_to_check):
                is_negative = True
                break

        # Step 3: If no negative pattern is found, keep the match
        if not is_negative:
            filtered_matches.append(match.group())

    return filtered_matches


def remove_split_char(input_text: str, split_char: str, return_part: int = 0) -> str:
    input_text = input_text.split(split_char)
    return input_text[return_part].strip()


def find_name_pages(names: list, pdf_text: dict[int:str],
                    exclude_pages: list, footnote_patterns: str,
                    remove_part_split_char: str | None = None):
    name_pages = {name: [] for name in names}

    for name in names:
        parts = name.split('_')
        if len(parts) > 1:  # FIRT AND LAST NAME
            last_name: str = parts[0]
            first_name: str = parts[1]
            if remove_part_split_char:
                last_name = remove_split_char(input_text=last_name,
                                              split_char='(')
            # Pattern to match full name, last name, and possessive forms, but not as part of footnotes
            name_pattern = rf"\b{first_name}[ ,]{last_name}(?:s|es|\b)|\b{last_name}(?:s|es|\b)[ ,]{first_name}"
        else:  # ONLY ONE NAME PART
            last_name: str = parts[0]
            if remove_part_split_char:
                last_name = remove_split_char(input_text=last_name,
                                              split_char='(')
                name_pattern = rf"\b{last_name}(?:s|es|\b)"

        # Prepare regex for footnotes
        negative_regex_last_name = [n.replace('name', last_name) for n in footnote_patterns]
        negative_regex_all_names = [n.replace('name', f"{first_name} {last_name}") for n in footnote_patterns]
        negative_regex = negative_regex_last_name + negative_regex_all_names
        for page_number, text in pdf_text.items():
            if page_number in exclude_pages:
                continue  # Skip excluded pages
            # replace nonbreak space with normal space for better more unified search results
            text = text.replace(' ', ' ')
            found_matches = filter_positive_matches(text=text,
                                                    negative_patterns=negative_regex,
                                                    positive_pattern=name_pattern,
                                                    context_window_after=10,
                                                    context_window_before=10,
                                                    ignore_case=True)
            if len(found_matches) > 0:
                name_pages[name].append(page_number)

    return name_pages


def apply_page_offset_to_name_page_dict(name_to_pages: dict[str:int], offset: int) -> dict:
    """removes the offset value from all pages"""
    return {key: [i + offset for i in value] for key, value in name_to_pages.items()}


def run_name_index(pdf_path: str,
                   names_list: list,
                   exclude_pages: list,
                   pages_offset: int = 0) -> dict[str:list[int]]:
    # Extract names and read PDF
    pdf_pages = read_pdf_pages(pdf_path)

    # Use the function to find the pages for each name
    name_to_pages = find_name_pages(names=names_list,
                                    pdf_text=pdf_pages,
                                    exclude_pages=exclude_pages,
                                    footnote_patterns=Constants.FOOTNOTE_RE_PATTERNS)

    name_to_pages = apply_page_offset_to_name_page_dict(name_to_pages=name_to_pages,
                                                        offset=pages_offset)

    return name_to_pages
