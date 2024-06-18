import pymupdf


def get_pdf_text(pdf_file: str):
    doc = pymupdf.open(pdf_file)
    text_pages: list = [page.get_text() for page in doc]
    pure_text: str = ' '.join(text_pages)
    pure_text = " ".join(pure_text.split())  # remove all special chars lile \n, \t, multiple space etc.
    return pure_text
