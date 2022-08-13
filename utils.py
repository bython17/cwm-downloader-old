from urllib import request
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


def does_overwrite(file):
    response = input(colored_str(Fore.YELLOW, False, bold_level=Style.DIM,
                     string=f'\n!WARNING: The file "{file}" already exists. Do you want to repace it? (y,n):') + ' ').lower()
    if response in ['yes', 'y', 'ofcourse']:
        return True
    else:
        return False


def make_soup(url, request_session, get_content=False, timeout=60):
    try:
        content = request_session.get(url, timeout=timeout)

        return BeautifulSoup(content.content, "html.parser") if not get_content else content
    except Exception as e:
        return handle_error(f"UKNOWN ERROR(utils.make_soup): {e}", 5, True, callback=make_soup,
                            url=url, request_session=request_session, timeout=timeout)


def colored_str(fore_color, back_color=False, string='', bold_level=""):
    return f"{fore_color}{bold_level}{string}{Style.RESET_ALL}" if not back_color else f"{back_color}{fore_color}{bold_level}{string}{Style.RESET_ALL}"


def save_text(text: str, output_file_name: str, recursed=False):
    output_file_name = path.expanduser(output_file_name)
    description = output_file_name.split(slash[OS])[-1]

    if not path.isfile(output_file_name) or recursed:
        with open(output_file_name, 'w') as file:
            file.write(text)
        print(
            f"\n    {Fore.MAGENTA}Finished downloading: {Style.RESET_ALL}{description}")
    else:
        if does_overwrite(description):
            save_text(text, output_file_name, True)
        else:
            return


def download(url: str, output_file_name, request_session, recursed=False, timeout=60,):
    output_file_name = path.expanduser(output_file_name)

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
        if not path.isfile(output_file_name) or recursed:
            # make an HTTP request within a context manager
            response = request_session.get(
                url, stream=True, timeout=timeout)

            response.raise_for_status()

            # check header to get content length, in bytes
            total_length = int(response.headers.get("content-length", 0))

            print(
                f"\n    {Fore.MAGENTA}Downloading {download_type}: {Style.RESET_ALL}{description}")
            # implement progress bar via tqdm
            with tqdm.wrapattr(open(output_file_name, 'wb'), "write", miniters=1, total=total_length, desc="", bar_format=custom_bar_format, ascii=" ━", ncols=80) as fout:

                for chunk in response.iter_content(chunk_size=4096):
                    fout.write(chunk)
        else:
            if does_overwrite(description):
                download(url, output_file_name, request_session, recursed=True)
            else:
                return

    except requests.exceptions.SSLError:
        handle_error('SSL ERROR', 0, True, callback=download,
                     url=url, output_file_name=output_file_name, request_session=request_session, recursed=True)

    except (requests.exceptions.Timeout, urllib3.exceptions.TimeoutError, requests.exceptions.ReadTimeout):
        handle_error("SERVER TIMEOUT", 0, True, callback=download,
                     url=url, output_file_name=output_file_name, request_session=request_session, recursed=True)

    except requests.exceptions.ConnectionError:
        handle_error("CONNECTION ERROR", 5, True, callback=download,
                     url=url, output_file_name=output_file_name, request_session=request_session, recursed=True)

    except gaierror as e:
        handle_error(f"NETWORK ERROR: {e}", 5,
                     True, callback=download, url=url, output_file_name=output_file_name, request_session=request_session, recursed=True)
    except Exception as e:
        handle_error(
            f"UNKNOWN ERROR(utils.download): {e}", 5, True, callback=download, url=url, output_file_name=output_file_name, request_session=request_session, recursed=True)


def handle_error(err, delay, retry=True, callback=download, **kwargs):
    retry_donwload_text = "retrying download" if retry else 'canceling download'
    if delay and retry:
        retry_donwload_text += f' after {delay}s'

    print(colored_str(Fore.WHITE, Back.RED,
                      string=f"!{err}, {retry_donwload_text}..."))
    if retry:
        sleep(delay)
        return callback(**kwargs)
