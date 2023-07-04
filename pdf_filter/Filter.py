import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import pandas as pd

url_demo = 'https://demo.seqrdoc.com/'
url = 'https://demo.seqrdoc.com/bestiu/backend/pdf_file/'
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
    occurrences = []
    try:
        response = requests.get(url, stream=True)
        pdf_file = io.BytesIO(response.content)
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if target_word.lower() in text.lower():
                    occurrences.append(page_number)
        except PyPDF2.utils.PdfReadError:
            pass
    except requests.exceptions.RequestException:
        print(f'Error connecting to {url}. Skipping...')
    return occurrences

# Check the count and page numbers of the target word in PDF files from selected URLs
print('Filtered URLs:')
for url in filtered_urls[1:10]:
    occurrences = extract_text_from_remote_pdf(url, keyword)
    count = len(occurrences)
    print(f'{url}: {count} occurrences')
    print(f'Page numbers: {occurrences}')

# Export filtered URLs to Excel
filtered_urls_with_keyword = [url for url in filtered_urls if extract_text_from_remote_pdf(url, keyword)]
if filtered_urls_with_keyword:
    df = pd.DataFrame({'Filtered URLs': filtered_urls_with_keyword})
    excel_file = 'filtered_urls1.xlsx'
    df.to_excel(excel_file, index=False)
    print('Filtered URLs exported to filtered_urls.xlsx')
else:
    print('No URLs with the keyword found.')
