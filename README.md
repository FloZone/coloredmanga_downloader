# ColoredManga Downloader
![Logo](logo.png)

A simple script for browsing the ColoredManga.com website and download the content.

It is written in python.

## Installing dependencies
All mandatory libraries and dependancies are listed in `requirements.txt`.
```bash
pip install -r ./requirements.txt
```

## Command-line help
```
usage: python coloredmanga_downloader.py [-h] [-v] chapter_url

ColoredMangaDownloader 1.0 - Browse the https://coloredmanga.com website and download mangas.

positional arguments:
  chapter_url    The URL of the first chapter of the manga you want to download

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

## Other commands
* `python setup.py lint` : for linting the script file
* `python setup.py fmt` : for formatting the script file
