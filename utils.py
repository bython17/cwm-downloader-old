import requests
import shutil
from tqdm.auto import tqdm
from bs4 import BeautifulSoup


def make_soup(url, headers={}, cookies={}):
    content = requests.get(url, headers=headers, cookies=cookies)
    return BeautifulSoup(content.content, "html.parser")


def save_text(text: str, output_file_name: str):
    with open(output_file_name, 'w') as file:
        file.write(text)
    print(f"Finished downloading `{output_file_name.split('/')[-1]}`")


def download(url: str, output_file_name):
    description = output_file_name.split('/')[-1]
    # make an HTTP request within a context manager
    with requests.get(url, stream=True) as content:

        # check header to get content length, in bytes
        total_length = int(content.headers.get("Content-Length"))

        # implement progress bar via tqdm
        with tqdm.wrapattr(content.raw, "read", total=total_length, desc=description) as raw:

            # save the output to a file
            with open(output_file_name, 'wb') as output:
                shutil.copyfileobj(raw, output)
    print(f"Finished downloading `{description}`")
