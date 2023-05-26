from django.contrib import admin
from filter.models import Urls
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

def get_urls(Url):
    """
    Fetches the URLs for PDF files from the given URL directory.

    Args:
        Url (str): The URL of the directory containing PDF files.

    Returns:
        list: A list of URLs for the PDF files found in the directory.
    """
    url_demo = 'https://demo.seqrdoc.com/'
    urls_list = [ ]
    reqs = requests.get(Url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    # Getting the list of available urls for pdf files in our given directory

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.pdf') and not href.endswith('/.pdf'):
            if not href.startswith('http'):
                href = f'{url_demo}{href}'
            urls_list.append(href)
            urls_list.append(href)


    return urls_list

def extract_text_from_remote_pdf(url, target_word):
    """
    Extracts text from a remote PDF file and checks if it contains the target word.

    Args:
        url (str): The URL of the remote PDF file.
        target_word (str): The word to search for in the PDF file.

    Returns:
        bool: True if the target word is found, False otherwise.
    """
    for s_url in get_urls(url):
                response = requests.get(s_url, stream=True)
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

def check_keyword(modeladmin, request, queryset):
    """
    Custom admin action to check if PDF files from selected URLs contain a keyword.

    Args:
        modeladmin (django.contrib.admin.ModelAdmin): The ModelAdmin instance.
        request (django.core.handlers.wsgi.WSGIRequest): The current request.
        queryset (django.db.models.query.QuerySet): The selected Urls objects.

    Returns:
        None
    """
    filtered_urls = []
    for url_obj in queryset:
        target_word = url_obj.keyword
        url = url_obj.Url
        if extract_text_from_remote_pdf(url, target_word):
            url_obj.keyword_found=True
            url_obj.save()
            filtered_urls.append(url_obj.Url)

    if filtered_urls:
        print('Filtered URLs:')
        for url in filtered_urls:
            print(url)
    else:
        print('No URLs with the keyword found.')

class Filtered_url_admin(admin.ModelAdmin):
    list_display = ['id', 'Url','keyword_found']
    ordering = ['id']
    actions = [check_keyword]

admin.site.register(Urls, Filtered_url_admin)
