## Code with Mosh Course Downloader

This project is created for people that bought a course from https://codewithmosh.com and want to download a single lecture or a whole course just using the command line

## Installation

Clone the project

```bash
git clone https://github.com/bython17/cwm-downloader/
```

Go to the project directory

```bash
cd cwm-downloader
```

Add a `credentials.py` file

-> `credentials.py` is the file that contains the header and cookie dictionaries in order to simulate a "signed in" user.

To get the header and cookies dictionary

1. Sign in to your account and go to an enrolled course that you have purchased

2. Inspect the page and go the Networks tab

3. Right click on the first request

4. Copy the cURL of the request

![copying the cURL of a request](https://drive.google.com/uc?id=1Vlyed-H9NrAMsSVSsVLEC19M6WxW-eJV)

5. Go to https://curlconvertor.com and paste the cURL (that you copied)

6. From the site copy the generated cookies and headers dictionary

![copying the headers and cookies dictionaries](https://drive.google.com/uc?id=1zPgUTP0gjpE7T5671bO3zElpwvat5IyP)

7. Create a `credentials.py` file in the same directory as the project source

8. Paste the contents you copied from the website

## Dependencies

beautifulsoup4, tqdm, requests, colorama

```bash
python -m pip install beautifulsoup4 tqdm requests colorama
```

## Running the project

You can either run the `main.py` script directly using python or compile the app to a binary. To do that:

Install pyinstaller

```bash
python -m pip install pyinstaller
```

Navigate to the project directory and run

```bash
pyinstaller --noconfirm --onefile --console main.py
```

### Tip

Add the destination directory to `PATH` or move the binary to a directory that is already added to the `PATH` in order to access the command from wherever you want.
