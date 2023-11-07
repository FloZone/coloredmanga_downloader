from argparse import ArgumentParser, ArgumentTypeError
import os
import shutil
import sys
import zipfile

from bs4 import BeautifulSoup
import requests

SCRIPT_VERSION = 1.2
SCRIPT_NAME = "ColoredMangaDownloader"
SCRIPT_FULLNAME = f"{SCRIPT_NAME} {SCRIPT_VERSION}"
WEBSITE = "https://coloredmanga.com"
DESCRIPTION = f"{SCRIPT_FULLNAME} - Browse the {WEBSITE} website and download mangas."

DIRECTORIES = []


def parse_args():
    """Parse the script args."""
    parser = ArgumentParser(prog=f"python {os.path.basename(__file__)}", description=DESCRIPTION)
    parser.add_argument("-v", "--version", action="version", version=SCRIPT_FULLNAME)
    parser.add_argument(
        dest="chapter_url",
        type=str,
        help="The URL of the first chapter of the manga you want to download",
    )
    parser.add_argument("--all", action="store_true", help="Download all chapters from the given one until the end")
    parser.add_argument("--cbz", action="store_true", help="Compress downloaded volumes to CBZ files")
    parser.add_argument(
        "--clean", action="store_true", help="Delete downloaded files after script execution (use with --cbz option)"
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
    """
    Browse the chapter page and download the pages.
    Return the next chapter URL if it exists, else None.
    """
    global DIRECTORIES

    log(f"Exploring {chapter_url}")

    chapter_data = BeautifulSoup(requests.get(chapter_url).content, "html.parser")

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
    volume_name = chapter_url.rstrip("/").split("/")[-2]
    chapter_name = chapter_url.rstrip("/").split("/")[-1]
    log(f"Chapter found: {volume_title} -- {chapter_title}")

    # Create a directory for the current volume if needed
    if not os.path.exists(volume_name):
        os.makedirs(volume_name)
        DIRECTORIES.append(volume_name)

    # Download each page file into this dir
    pages = chapter_data.find("div", class_="reading-content").find_all("img", class_="wp-manga-chapter-img")
    page_count = 1
    page_total = len(pages)
    for page in pages:
        log(f"Downloading page {page_count}/{page_total}")
        page_url = page["src"].strip()
        pagename = "{0:0=3d}".format(page_count)
        filename = f"{chapter_name}-{pagename}.{page_url.split('.')[-1]}"
        with open(os.path.join(volume_name, filename), "wb") as f:
            f.write(requests.get(page_url).content)
        page_count += 1

    log(f"Chapter downloaded to directory {volume_name} ✔️\n")

    next_chapter = chapter_data.find("a", class_="btn next_page")
    if next_chapter:
        return next_chapter["href"].strip()
    else:
        return None


if __name__ == "__main__":
    args = parse_args()

    next_chapter_url = browse_chapter(args.chapter_url)
    # Download all remaining chapters
    if args.all:
        while next_chapter_url:
            next_chapter_url = browse_chapter(next_chapter_url)

    # CBZ compress downloaded volumes
    if args.cbz:
        for volume_dir in DIRECTORIES:
            cbz_file = zipfile.ZipFile(f"{volume_dir}.cbz", "w")
            for _, __, files in os.walk(volume_dir):
                for filename in files:
                    cbz_file.write(os.path.join(volume_dir, filename), filename)
            cbz_file.close()
        # Clean downloaded files
        if args.clean:
            for volume_dir in DIRECTORIES:
                shutil.rmtree(volume_dir)

    input("🎉 Execution completed 🎉 Press 'Enter' to exit...")
    sys.exit(0)
