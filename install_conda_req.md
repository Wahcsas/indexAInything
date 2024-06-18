# Install requirements unsing windows
## using windows
Get-Content requirements.txt | ForEach-Object { conda install --yes $_ }


## using linux
while read requirement; do conda install --yes $requirement; done < requirements.txt


## manual install outside of conda:
* pip install gradio
* pip install PyMuPDF
* pip install python-docx
* pip install gradio_pdf