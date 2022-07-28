import utils
import argparse
from credentials import cookies, headers


class Course:
    def __init__(self, url: str, folder='./'):
        self.course_url = url if not url.endswith('/') else url[:len(url) - 1]
        self.destination_folder = folder

        print("Initializing download...")
        self.course_soup = utils.make_soup(self.course_url)
        lectures_li = self.course_soup.find_all("li", class_="section-item")
        self.lectures = list(
            map(lambda lect_li: lect_li.find('a'), lectures_li))

    def save_lecture_text(self, lecture_id):
        lecture_soup = self.make_lecture_soup(lecture_id)
        title = lecture_soup.find("h2", {'id': 'lecture_heading'}).text.strip()
        content = lecture_soup.find(
            "div", {'class': 'lecture-text-container'}).text.strip()

        return f'{title} \n\n{content}'

    def get_lecture_by_id(self, lecture_id):
        return list(filter(lambda lect_a: lect_a.get("data-ss-lecture-id") == lecture_id, self.lectures))[0]

    def get_lecture_title(self, lecture_id):
        lecture = self.get_lecture_by_id(lecture_id)

        lecture_title_list = list(filter(lambda string: string != '' and string != 'Start' and string != 'Preview', list(
            map(lambda el: el.strip(), lecture.text.strip().splitlines()))))

        # Remove numbers from the name
        lecture_title = lecture_title_list[0].split('-')[1]

        return lecture_title

    def get_resource_title(self, lecture_id):
        lecture_soup = self.make_lecture_soup(lecture_id)
        resource_title = lecture_soup.find('a', class_='download').text.strip()
        return resource_title

    def make_lecture_soup(self, lecture_id):
        lecture_url = f'{self.course_url}{utils.slash[utils.OS]}lectures{utils.slash[utils.OS]}{lecture_id}'
        return utils.make_soup(lecture_url, headers=headers, cookies=cookies)

    def get_lecture_download_url(self, lecture_id):
        lecture_soup = self.make_lecture_soup(lecture_id)
        lecture_download_url = lecture_soup.find(
            'a', class_="download").get("href")
        return lecture_download_url

    def check_if_video(self, lecture_id):
        lecture_soup = self.make_lecture_soup(lecture_id)
        heading = lecture_soup.find('h2', {'id': 'lecture_heading'})
        icon = heading.find('use', {'xlink:href': '#icon__Video'})

        return True if icon is not None else False

    def download_lecture(self, lecture_id):
        lecture_number = self.lectures.index(
            self.get_lecture_by_id(lecture_id)) + 1
        lecture_name = f"{lecture_number}-{self.get_lecture_title(lecture_id)}"

        if self.check_if_video(lecture_id):
            download_url = self.get_lecture_download_url(lecture_id)
            utils.download(
                download_url, f"{self.destination_folder}{utils.slash[utils.OS]}{lecture_name}.mp4")
        else:
            lecture_text = self.save_lecture_text(lecture_id)
            utils.save_text(
                lecture_text, f"{self.destination_folder}{utils.slash[utils.OS]}{lecture_name}.md")

            # Download resource if available
            try:
                resource_name = self.get_resource_title(lecture_id)
                resource_download_url = self.get_lecture_download_url(
                    lecture_id)
                utils.download(
                    resource_download_url, f"{self.destination_folder}{utils.slash[utils.OS]}Resource- {resource_name}")
            except:
                pass

    def download_lectures(self, from_lecture=0, to_lecture=-1):
        lectures = self.lectures[from_lecture:to_lecture]
        for lecture in lectures:
            self.download_lecture(lecture.get("data-ss-lecture-id"))
        print("\nFinished Downloading Course")
        print(f"Files found at {self.destination_folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="CWM Downloader",
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

    args = parser.parse_args()

    course = Course(args.courseUrl, args.destinationDir)
    if args.lectureId:
        course.download_lecture(args.lectureId)
    else:
        course.download_lectures(args.fromIndex - 1, args.toIndex)
