import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import pandas as pd
import concurrent.futures
from timeit import default_timer as timer

start = timer()

def process_pdf_files():
    url_demo = 'https://demo.seqrdoc.com/'
    url = 'https://demo.seqrdoc.com/bestiu/backend/pdf_file/'
    keyword = 'AGRICULTURE'
    filtered_urls = []

    # Fetch URLs for PDF files from the given URL directory
    session = requests.Session()
    reqs = session.get(url)
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
        count = 0
        try:
            response = session.get(url, stream=True)
            pdf_file = io.BytesIO(response.content)
            try:
                reader = PyPDF2.PdfReader(pdf_file)
                for page_number, page in enumerate(reader.pages, start=1):
                    text = page.extract_text()
                    if target_word.lower() in text.lower():
                        occurrences.append(page_number)
                        count += text.lower().count(target_word.lower())
            except PyPDF2.utils.PdfReadError:
                pass
        except requests.exceptions.RequestException:
            print(f'Error connecting to {url}. Skipping...')
        return occurrences, count

    # Check the count and page numbers of the target word in PDF files from selected URLs
    print('Filtered URLs:')
    filtered_urls_with_keyword = []
    occurrences = []
    counts = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = []
        for url in filtered_urls:
            result = executor.submit(extract_text_from_remote_pdf, url, keyword)
            results.append((url, result))

        for url, result in results:
            url_occurrences, count = result.result()
            print(f'{url}: {count} occurrences')
            print(f'Page numbers: {url_occurrences}')
            if count >= 1:
                filtered_urls_with_keyword.append(url)
                occurrences.append(url_occurrences)
                counts.append(count)

    # Export filtered URLs with counts to Excel
    if filtered_urls_with_keyword:
        df = pd.DataFrame({'Filtered URLs': filtered_urls_with_keyword, 'Count': counts, 'Page Numbers': occurrences})
        excel_file = 'filtered_urls.xlsx'
        df.to_excel(excel_file, index=False)
        print('Filtered URLs exported to filtered_urls.xlsx')
    else:
        print('No URLs with the keyword found.')


if __name__ == '__main__':
    process_pdf_files()

end = timer()
print(end - start)
