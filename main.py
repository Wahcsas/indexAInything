import gradio as gr
import pymupdf

from utils import str_utils


def main():
    demo = gr.Interface(
        fn=str_utils.get_pdf_text,
        inputs=[gr.File(label="Document")],
        outputs=gr.Textbox()
    )
    demo.launch()


if __name__ == "__main__":
    main()
