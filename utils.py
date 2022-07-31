import requests
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from sys import platform
from os import path
from time import sleep
from socket import gaierror
import urllib3.exceptions
from colorama import Back, Fore, Style

OS = platform[:3]
slash = {'lin': '/', 'dar': '/', 'mac': '/', 'win': '\\'}
custom_bar_format = "{desc}        %s{bar} {n_fmt}/{total_fmt} %s{rate_fmt} %seta %s{remaining}%s" % (
    Fore.GREEN, Fore.RED, Style.RESET_ALL, Fore.CYAN, Style.RESET_ALL)

# Supress the download warning that appears when not verifying an ssl certificate
requests.packages.urllib3.disable_warnings(
    category=urllib3.exceptions.InsecureRequestWarning)


def make_soup(url, headers={}, cookies={}):
    try:
        content = requests.get(url, headers=headers,
                               cookies=cookies, timeout=60)
        return BeautifulSoup(content.content, "html.parser")
    except Exception as e:
        handle_error(f"UKNOWN ERROR(utils.make_soup): {e}", 5, True, callback=make_soup,
                     url=url, headers=headers, cookies=cookies)


def colored_str(fore_color, back_color=False, string='', bold_level=""):
    return f"{fore_color}{bold_level}{string}{Style.RESET_ALL}" if not back_color else f"{back_color}{fore_color}{bold_level}{string}{Style.RESET_ALL}"


def save_text(text: str, output_file_name: str):
    with open(output_file_name, 'w') as file:
        file.write(text)
    print(f"Finished downloading `{output_file_name.split(slash[OS])[-1]}`")


def download(url: str, output_file_name):
    description = output_file_name.split(slash[OS])[-1]
    extension_type_dict = {
        'mp4': 'video lecture',
        'md': 'text lecture',
    }

    try:
        download_type = extension_type_dict[description.split('.')[-1]]
    except:
        download_type = 'resource'

    try:
        # make an HTTP request within a context manager
        response = requests.get(
            url, stream=True, verify=False, timeout=60)

        # check header to get content length, in bytes
        total_length = int(response.headers.get("content-length", 0))

        print(
            f"\n    {Fore.MAGENTA}Downloading {download_type}: {Style.RESET_ALL}{description}")
        # implement progress bar via tqdm
        with tqdm.wrapattr(open(output_file_name, 'wb'), "write", miniters=1, total=total_length, desc="", bar_format=custom_bar_format, ascii=" ━", ncols=80) as fout:

            for chunk in response.iter_content(chunk_size=4096):
                fout.write(chunk)

    except requests.exceptions.SSLError:
        handle_error('SSL ERROR', 0, url, output_file_name)

    except (requests.exceptions.Timeout, urllib3.exceptions.TimeoutError, requests.exceptions.ReadTimeout):
        handle_error("SERVER TIMEOUT", 0, url, output_file_name)

    except requests.exceptions.ConnectionError:
        handle_error("CONNECTION ERROR", 5, url, output_file_name)

    except gaierror as e:
        handle_error(f"NETWORK ERROR: {e}", 0,
                     url, output_file_name, retry=False)
    except Exception as e:
        handle_error(
            f"UNKNOWN ERROR(utils.download): {e}", 0, url, output_file_name)


def handle_error(err, delay, retry=True, callback=download, **kwargs):
    retry_donwload_text = "retrying download" if retry else 'canceling download'
    if delay and retry:
        retry_donwload_text += f' after {delay}s'

    print(colored_str(Fore.WHITE, Back.RED,
                      string=f"!{err}, {retry_donwload_text}..."))
    if retry:
        sleep(delay)
        callback(**kwargs)


if __name__ == "__main__":
    download("http://ipv4.download.thinkbroadband.com/20MB.zip",
             'Thisisadummyscriptthatplayssomethingcoollsajflsadjflsajflasjdlfjsaldfjsadfdkfhaskdfhs.zip')
