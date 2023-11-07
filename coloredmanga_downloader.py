from argparse import ArgumentParser, ArgumentTypeError
import os
import re
import sys

from bs4 import BeautifulSoup
import requests

SCRIPT_VERSION = 1.00
SCRIPT_NAME = "ColoredMangaDownloader"
SCRIPT_FULLNAME = f"{SCRIPT_NAME} {SCRIPT_VERSION}"

WEBSITE = "https://coloredmanga.com"
DESCRIPTION = f"{SCRIPT_FULLNAME} - Browse the {WEBSITE} website and download mangas."


def parse_args():
    """Parse the script args."""
    parser = ArgumentParser(prog=f"python {os.path.basename(__file__)}", description=DESCRIPTION)
    parser.add_argument("-v", "--version", action="version", version=SCRIPT_FULLNAME)
    parser.add_argument(
        dest="chapter_url",
        type=str,
        help="The URL of the first chapter of the manga you want to download",
    )
    args = parser.parse_args()
    # Validate args
    if WEBSITE not in args.chapter_url:
        raise ArgumentTypeError(f"Invalid arguments: the given URL must be from {WEBSITE}")

    return args


def log(message: str):
    """Simple logger."""
    print(f"[{SCRIPT_NAME}] {message}")


def browse_chapter(chapter_url: str):
    """Browse the chapter page and download the pages."""
    log(f"Exploring {chapter_url}")

    chapter_page = requests.get(chapter_url)
    chapter_data = BeautifulSoup(chapter_page.content, "html.parser")

    # [-1] because the first chapter is always selected
    volume_title = (
        chapter_data.find("select", class_="volume-select").find_all("option", selected=True)[-1].text.strip()
    )
    chapter_title = (
        chapter_data.find("div", class_="chapters_selectbox_holder")
        .find("div", class_="selectpicker_chapter", style=False)
        .find("option", selected=True)
        .text.strip()
    )
    volume_number = "{0:0=3d}".format(int(re.findall(r"\d+", volume_title)[0]))
    chapter_number = "{0:0=3d}".format(int(re.findall(r"\d+", chapter_title)[0]))
    log(f"Chapter found: {volume_title} -- {chapter_title}")

    # Create a directory for the current volume if needed
    volume_dir = f"volume_{volume_number}"
    if not os.path.exists(volume_dir):
        os.makedirs(volume_dir)

    # Download each page file into this dir
    pages = chapter_data.find("div", class_="reading-content").find_all("img", class_="wp-manga-chapter-img")
    page_count = 1
    page_total = len(pages)
    for page in pages:
        log(f"Downloading page {page_count}/{page_total} ")
        page_url = page["src"].strip()
        pagename = "{0:0=3d}".format(page_count)
        filename = f"{chapter_number}-{pagename}.{page_url.split('.')[-1]}"
        with open(os.path.join(volume_dir, filename), "wb") as f:
            f.write(requests.get(page_url).content)
        page_count += 1

    log(f"Chapter downloaded to directory {volume_dir} ✔️")


if __name__ == "__main__":
    args = parse_args()

    browse_chapter(args.chapter_url)

    input("Execution completed 🎉. Press 'Enter' to exit...")
    sys.exit(0)
