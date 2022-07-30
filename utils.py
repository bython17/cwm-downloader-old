import requests
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from sys import platform
from os import remove, path
import urllib3.exceptions

OS = platform[:3]
slash = {'lin': '/', 'dar': '/', 'mac': '/', 'win': '\\'}

# Supress the download warning that appears when not verifying an ssl certificate
requests.packages.urllib3.disable_warnings(
    category=urllib3.exceptions.InsecureRequestWarning)


def make_soup(url, headers={}, cookies={}):
    content = requests.get(url, headers=headers, cookies=cookies)
    return BeautifulSoup(content.content, "html.parser")


def save_text(text: str, output_file_name: str):
    with open(output_file_name, 'w') as file:
        file.write(text)
    print(f"Finished downloading `{output_file_name.split(slash[OS])[-1]}`")


def download(url: str, output_file_name):
    description = output_file_name.split(slash[OS])[-1]
    try:
        # make an HTTP request within a context manager
        response = requests.get(
            url, stream=True, verify=False, timeout=20)

        # check header to get content length, in bytes
        total_length = int(response.headers.get("content-length", 0))

        # implement progress bar via tqdm
        with tqdm.wrapattr(open(output_file_name, 'wb'), "write", miniters=1, total=total_length, desc=description) as fout:
            for chunk in response.iter_content(chunk_size=4096):
                fout.write(chunk)

        print(f"Finished downloading `{description}`")

    except requests.exceptions.SSLError:
        print("SSL error occured, retrying download...")
        if path.isfile(output_file_name):
            remove(output_file_name)
        download(url, output_file_name)

    except requests.exceptions.Timeout or urllib3.exceptions.TimeoutError:
        print("Server timeout error occured, retrying download...")
        if path.isfile(output_file_name):
            remove(output_file_name)
        download(url, output_file_name)
