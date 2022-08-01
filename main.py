import utils
import argparse
from sys import exit
from credentials import cookies, headers
from colorama import Fore, Style
import lecture_text as lec_text


# TODO: Make the md files look better or render html with css


class Course:
    def __init__(self, url: str, folder_location='./'):
        self.course_url = url if not url.endswith('/') else url[:len(url) - 1]

        if '/enrolled' in self.course_url:
            self.course_url = self.course_url.replace('/enrolled', '')

        self.destination_folder = folder_location

        print(utils.colored_str(Fore.YELLOW,
              string="\nInitializing download...", bold_level=Style.BRIGHT))

        self.course_soup = utils.make_soup(self.course_url, headers, cookies)
        self.course_name = self.course_soup.find(
            'div', {'class': 'course-sidebar'}).find('h2').text.strip()

        lectures_li = self.course_soup.find_all("li", class_="section-item")
        self.lectures = list(
            map(lambda lect_li: lect_li.find('a'), lectures_li))

    def get_lecture_by_id(self, lecture_id):
        try:
            return list(filter(lambda lect_a: lect_a.get("data-ss-lecture-id") == lecture_id, self.lectures))[0]
        except IndexError:
            print("Specified ID is not found in the course")
            exit()

    def get_lecture_title(self, lecture_id):
        lecture = self.get_lecture_by_id(lecture_id)

        lecture_title_list = list(filter(lambda string: string != '' and string != 'Start' and string != 'Preview', list(
            map(lambda el: el.strip(), lecture.text.strip().splitlines()))))

        # Remove numbers from the name
        lecture_title = '- '.join(lecture_title_list[0].split('-')[1:])

        return lecture_title

    def get_resource_title(self, lecture_soup):
        resource_title = lecture_soup.find_all('a', class_='download')
        resource_title = list(
            map(lambda res: res.text.strip(), resource_title))

        return resource_title

    def make_lecture_soup(self, lecture_id):
        lecture_url = f'{self.course_url}/lectures/{lecture_id}'
        return utils.make_soup(lecture_url, headers=headers, cookies=cookies)

    def get_lecture_download_url(self, lecture_soup, multiple=False):
        lecture_download_urls = lecture_soup.find_all(
            'a', class_="download")
        lecture_download_urls = list(
            map(lambda aTags: aTags.get("href"), lecture_download_urls))

        return lecture_download_urls[0] if not multiple else lecture_download_urls

    def check_if_video(self, lecture_soup):
        heading = lecture_soup.find('h2', {'id': 'lecture_heading'})
        icon = heading.find('use', {'xlink:href': '#icon__Video'})

        return True if icon is not None else False

    def download_resources(self, resource_urls, resource_names, lecture_number):
        for (url, name) in zip(resource_urls, resource_names):
            utils.download(
                url, f"{self.destination_folder}{utils.slash[utils.OS]}{lecture_number}- Resource- {name}")

    def download_lecture(self, lecture_id, no_confirm=False):
        lecture_number = self.lectures.index(
            self.get_lecture_by_id(lecture_id)) + 1
        lecture_name = f"{lecture_number}-{self.get_lecture_title(lecture_id)}"
        lecture_soup = self.make_lecture_soup(lecture_id)

        if self.check_if_video(lecture_soup):
            download_urls = self.get_lecture_download_url(
                lecture_soup, multiple=True)
            utils.download(
                download_urls[0], f"{self.destination_folder}{utils.slash[utils.OS]}{lecture_name}.mp4", no_confirm)

            if len(download_urls) > 1:
                resource_names = self.get_resource_title(lecture_soup)
                resource_names = resource_names[1:]
                resource_download_urls = download_urls[1:]
                self.download_resources(
                    resource_download_urls, resource_names, lecture_number)
        else:
            markup = lec_text.get_main_element(lecture_soup, lecture_number)
            lecture_text = lec_text.create_html(lecture_name, markup)
            utils.save_text(
                lecture_text, f"{self.destination_folder}{utils.slash[utils.OS]}{lecture_name}.html", no_confirm)

            # Download resource if available
            resource_names = self.get_resource_title(lecture_soup)

            resource_download_urls = self.get_lecture_download_url(
                lecture_soup, multiple=True)

            self.download_resources(
                resource_download_urls, resource_names, lecture_number)

    def download_lectures(self, from_lecture=0, to_lecture=-1, no_confirm=False):
        if to_lecture == -1:
            to_lecture = len(self.lectures)

        lectures = self.lectures[from_lecture:to_lecture]

        print(utils.colored_str(Fore.YELLOW,
              string=f"Downloading course:"), end=" ")
        print(utils.colored_str(Fore.CYAN,
              string=f"{self.course_name}", bold_level=Style.BRIGHT))
        for lecture in lectures:
            self.download_lecture(lecture.get(
                "data-ss-lecture-id"), no_confirm)
        print(utils.colored_str(Fore.GREEN,
              string="\nFinished Downloading Course"))
        print(utils.colored_str(Fore.WHITE,
              string=f"Files found at {self.destination_folder}"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="cwm-downloader",
        description="Download courses from Mosh Hamedani")

    parser.add_argument('-c', '--courseUrl',
                        help="The URL of the course to be downloaded")
    parser.add_argument('-id', '--lectureId', default="",
                        help="The ID of the lecture to be downloaded")
    parser.add_argument('--fromIndex', default=1, type=int,
                        help="Start index of download")
    parser.add_argument('--toIndex', default=-1, type=int,
                        help="End index of download")
    parser.add_argument('-d', '--destinationDir', default="./",
                        help="The final destination folder (if in windows make sure to double the `\`)")
    parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    parser.add_argument('--noConfirm', default=False, dest='no_confirm',
                        action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    course = Course(args.courseUrl, args.destinationDir)
    if args.lectureId:
        course.download_lecture(args.lectureId, args.no_confirm)
    else:
        course.download_lectures(
            args.fromIndex - 1, args.toIndex, args.no_confirm)
