import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import pandas as pd

url_demo = 'https://demo.seqrdoc.com/'
url = '	https://demo.seqrdoc.com/bestiu/backend/pdf_file/'
keyword = 'AGRICULTURE'
filtered_urls = []

# Fetch URLs for PDF files from the given URL directory
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.endswith('.pdf') and not href.endswith('/.pdf'):
        if not href.startswith('http'):
            href = f'{url_demo}{href}'
        filtered_urls.append(href)

# Extract text from a remote PDF file and check if it contains the target word
def extract_text_from_remote_pdf(url, target_word):
    response = requests.get(url, stream=True)
    pdf_file = io.BytesIO(response.content)
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            if target_word.lower() in text.lower():
                return True
    except PyPDF2.utils.PdfReadError:
        pass
    return False

# Check if PDF files from selected URLs contain a keyword
print('Filtered URLs:')
for url in filtered_urls:
    if extract_text_from_remote_pdf(url, keyword):
        print(url)

# Export filtered URLs to Excel
filtered_urls_with_keyword = [url for url in filtered_urls if extract_text_from_remote_pdf(url, keyword)]
if filtered_urls_with_keyword:
    df = pd.DataFrame({'Filtered URLs': filtered_urls_with_keyword})
    excel_file = 'filtered_urls.xlsx'
    df.to_excel(excel_file, index=False)
    print('Filtered URLs exported to filtered_urls.xlsx')
else:
    print('No URLs with the keyword found.')
