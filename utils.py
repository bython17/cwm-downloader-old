import requests
import shutil
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from sys import platform
from os import remove, path

OS = platform[:3]
slash = {'lin': '/', 'dar': '/', 'mac': '/', 'win': '\\'}


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
        response = requests.get(url, stream=True, allow_redirects=True)

        # check header to get content length, in bytes
        total_length = int(response.headers.get("content-length", 0))

        # implement progress bar via tqdm
        with tqdm.wrapattr(open(output_file_name, 'wb'), "write", miniters=1, total=total_length, desc=description) as fout:
            for chunk in response.iter_content(chunk_size=4096):
                fout.write(chunk)

    except requests.exceptions.SSLError:
        print("SSL error occured, retrying download...")
        if path.isfile(output_file_name):
            remove(output_file_name)
        download(url, output_file_name)

    print(f"Finished downloading `{description}`")
