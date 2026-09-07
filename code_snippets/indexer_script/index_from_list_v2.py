import docx
import pymupdf
import re
from docx import Document
from pathlib import Path

# Paths to your files (adjust these as necessary)
docx_path = Path(r"D:\python_projects\indexer_script\02689 Dahlke_One nation under God_Der US-Katholizismus und die Politik_Personenregister.docx")
pdf_path = Path(r"D:\python_projects\indexer_script\02689_Dahlke_One-Nation-under-God_rk5.pdf")

exclude_pages = [1, 2, 3, 4, 5, 6, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288]
                 # pages to exclude, e.g., table of contents

pages_offset = 0  # offset of page numbers as written in pdf from acutal pymupdf counting

footnote_patterns = [
    r'[Vv]gl\. name'
    r'[Ss]iehe\s+\w+\s+\w+\s+und name',
    r'[Vv]gl\.\s+\w+\s+\w+\s+und name'
    r'[Ss]iehe auch name',
    r'[.]\s\nname:',
    r'[.]\sname:'
]
#
# english_footnote_patterns = [
#     r'[C,c]f. name'
#     r'[S,s]ee\s+\w+\s+\w+\s+and name',
#     r'[C,c]f.\s+\w+\s+\w+\s+and name'
#     r'[S,s]ee also name',
#     r'[.]\s\nname:',
#     r'[.]\sname:',
#     r'chöningh, name'  # special case for line: Urheberrechtlich geschütztes Material! Copyright 2024 Brill Schöningh, Paderbor
# ]
#

def filter_positive_matches(text, positive_pattern, negative_patterns, context_window_before=10, context_window_after=10, ignore_case=True):
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

def extract_names_from_docx(docx_path):
    # Load the DOCX file
    doc = docx.Document(docx_path)
    names = []

    # Assuming each name is in a separate paragraph
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:  # Make sure there's text and not just an empty string
            names.append(text)

    return names


def read_pdf_with_pages(pdf_path) -> dict[int:str]:
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


def find_name_pages(names:list, pdf_text:dict[int:str],
                    exclude_pages: list, footnote_patterns:str,
                    remove_part_split_char: str | None=None):
    name_pages = {name: [] for name in names}

    for name in names:
        parts = name.split(', ')
        last_name:str = parts[0]
        first_name:str = parts[1] if len(parts) > 1 else ''

        if remove_part_split_char:
            if remove_part_split_char in last_name:
                last_name = last_name.split('(')
                last_name = last_name[0].strip()

        # Pattern to match full name, last name, and possessive forms, but not as part of footnotes
        name_pattern = rf'\b{last_name}(?:,?\s+{first_name})?\b|\b{first_name}\s+{last_name}\b'

        # Prepare regex for footnotes
        negative_regex_last_name = [n.replace('name', last_name) for n in footnote_patterns]
        negative_regex_all_names = [n.replace('name', f"{first_name} {last_name}") for n in footnote_patterns]
        negative_regex = negative_regex_last_name + negative_regex_all_names
        for page_number, text in pdf_text.items():
            if page_number in exclude_pages:
                continue  # Skip excluded pages
            text = text.replace(' ', ' ')  # replace nonbreak space with normal space for better more unified search results
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


def make_page_dict_unique(name_to_pages: dict[str:int]) -> dict:
    """removes any duplicate page number in the pages list"""
    return {key: list(set(value)) for key, value in name_to_pages.items()}


def update_docx_with_pages(docx_path, name_to_pages, output_path):
    # Load the existing DOCX file
    doc = Document(docx_path)

    # Iterate over each paragraph, check if it's a name, and append page numbers if it is
    for para in doc.paragraphs:
        original_text = para.text.strip()
        if original_text in name_to_pages:
            pages = sorted(name_to_pages[original_text])
            # Create a string of page numbers, separated by commas
            pages_str = ', '.join(map(str, pages))
            # Update the paragraph text with page numbers
            para.text = f"{original_text} {pages_str}"

    # Save the updated document to a new file
    doc.save(output_path)


# Extract names and read PDF
names_list = extract_names_from_docx(docx_path)
pdf_pages = read_pdf_with_pages(pdf_path)

# Use the function to find the pages for each name
name_to_pages = find_name_pages(names=names_list,
                                pdf_text=pdf_pages,
                                exclude_pages=exclude_pages,
                                footnote_patterns=footnote_patterns,
                                remove_part_split_char='(')
name_to_pages = apply_page_offset_to_name_page_dict(name_to_pages=name_to_pages,
                                                    offset=pages_offset)
name_to_pages = make_page_dict_unique(name_to_pages=name_to_pages)

# Print some sample outputs to verify
for name, pages in list(name_to_pages.items())[:5]:  # print results for the first 5 names
    print(f"{name}: {sorted(pages)}")

# Define the path for the output DOCX file
output_docx_path = Path(docx_path.parent, docx_path.stem + '_pages_added' + docx_path.suffix)

# Update the DOCX file with the pages
update_docx_with_pages(docx_path, name_to_pages, output_docx_path)

print("The DOCX file has been updated and saved to:", output_docx_path)
