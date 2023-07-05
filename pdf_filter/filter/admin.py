from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Urls
import requests
from bs4 import BeautifulSoup
import fitz
import io
import time


def get_urls(url):
    """
    Fetches the URLs for PDF files from the given URL directory.

    Args:
        url (str): The URL of the directory containing PDF files.

    Returns:
        list: A list of URLs for the PDF files found in the directory.
    """
    url_demo = 'https://demo.seqrdoc.com/'
    urls_list = []
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    # Getting the list of available URLs for PDF files in the given directory
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.pdf') and not href.endswith('/.pdf'):
            if not href.startswith('http'):
                href = f'{url_demo}{href}'
            urls_list.append(href)

    return urls_list


def extract_text_from_remote_pdf(url, target_word):
    """
    Extracts text from a remote PDF file and checks if it contains the target word.

    Args:
        url (str): The URL of the remote PDF file.
        target_word (str): The word to search for in the PDF file.

    Returns:
        Tuple[List[int], int, bool]: A tuple containing a list of page occurrences, count, and a boolean indicating if the target word is found.
    """
    occurrences = []
    count = 0

    response = requests.get(url, stream=True)
    pdf_file = io.BytesIO(response.content)
    try:
        doc = fitz.open(stream=pdf_file, filetype='pdf')
        for page_number in range(doc.page_count):
            page = doc.load_page(page_number)
            text = page.get_text()
            if target_word.lower() in text.lower():
                occurrences.append(page_number + 1)  # Adding 1 to match PyPDF2 page numbering
                count += text.lower().count(target_word.lower())
        if occurrences:
            return occurrences, count, True
    except fitz.errors.PDFError:
        pass

    return occurrences, count, False


def export_to_csv(modeladmin, request, queryset):
    start_time = time.time()  # Start time

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filtered_urls.csv"'
    writer = csv.writer(response)
    writer.writerow(['URL', 'Keyword', 'Page Numbers', 'Count', 'Keyword Found'])

    for url_obj in queryset:
        target_word = url_obj.keyword
        url = url_obj.Url
        urls = get_urls(url)
        c=0
        for s_url in urls:
            occurrences, count, found = extract_text_from_remote_pdf(s_url, target_word)
            writer.writerow([s_url, target_word, occurrences, count, str(found)])
            c+=1
            print(s_url, target_word, occurrences, count,c)

    end_time = time.time()  # End time
    runtime = end_time - start_time

    print(f"Runtime: {runtime} seconds")
    return response


class UrlsAdmin(admin.ModelAdmin):
    list_display = ['id', 'Url', 'keyword_found']
    ordering = ['id']
    actions = [export_to_csv]


admin.site.register(Urls, UrlsAdmin)
