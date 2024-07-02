# IndexAInything

This project is a Python application that leverages a Large Language Model (LLM) to extract names from the text of a PDF document. The project uses `gradio` for the UI, and `openAI` API for language model processing.

## Features

- **PDF Text Extraction**: Extracts text from PDF files.
- **Text Splitting**: Splits extracted text into tokenized paragraphs.
- **LLM Prompting**: Sends text prompts to an LLM for name extraction.
- **User Interface**: Provides a simple web interface to upload PDF files and retrieve extracted names.

## Requirements

- Python 3.7 or higher
- Python Libraries see requirements.txt

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pdf-name-extractor.git
   cd pdf-name-extractor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the OpenAI API:**
   Ensure that the `Constants.py` file contains the correct settings for connecting to the OpenAI API:
   ```python
   # Constants.py
   SYSTEM_PROMPT = "Your system prompt here"
   USER_BASE_PROMPT = "Your user base prompt here"
   MODEL_NAME = "gpt-3.5-turbo"
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

1. Open your web browser and go to the address provided by Gradio after launching the application.
2. Upload your PDF file using the provided file upload button.
3. Click the 'Start' button to begin the extraction process.
4. Extracted names will be displayed in the textbox output.

## Project Structure

- `main.py`: The main application file that sets up the Gradio interface and handles the workflow.
- `Constants.py`: Contains constant values used throughout the project.
- `API_Connector/openAI.py`: Handles the connection and communication with the OpenAI API.
- `utils/str_utils.py`: Utility functions for handling and processing text.
- `utils/prompt_utils.py`: Utility functions for creating and managing prompts for the LLM.

## Example

To run the project, execute the following command in your terminal:

```bash
python main.py
```

This will start a local server with the Gradio interface. Navigate to the provided URL in your web browser, upload a PDF, and click 'Start' to see the extracted names.


## License
    to be decided