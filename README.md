# teachable_dl

Python 3 command-line tool for downloading your purchased + free courses on the teachable platform.

## Installation

1) Install latest Python 3 version.

2) Download this repository.

3) Start a virtual environment.

4) `pip` install via `requirements.txt`.

5) Sign in to all relevant teachable courses. Teachable tracks course sessions separately and ends sessions quickly after closing the window, so it is necessary to keep all courses open in the browser during download.

6) Generate a Netscape/Mozilla format CookieJar containing your session information across all courses to download. I recommend using [Export Cookies](https://github.com/rotemdan/ExportCookies), and exporting cookies for all domains if you intend to download multiple courses at once. You should delete this cookie file after finishing downloads for security purposes.

The tool should now be ready to use.

## Example

Downloading two different courses from different teachable schools. Cookies file has been placed in the same directory as the script is executed from. Output has been redirected to a custom folder. Note that more than one course URL can be specified at a time.
```sh
(.venv) example@example:~/scripts/teachable_dl python3 teachable_dl.py -c cookies.txt -o ~/online_courses/teachable -u https://courses.data36.com/courses/enrolled/455539 https://milk-street-cooking-school.teachable.com/courses/enrolled/739683
```

## Full Usage

```
usage: teachable_dl.py [-h] -c COOKIES [-u URL [URL ...]] [-o OUTPUT] [-v]

Teach:Able content downloader.

optional arguments:
  -h, --help            show this help message and exit
  -c COOKIES, --cookies COOKIES
                        Cookies file containing logged-in session for the
                        desired course(s).
  -u URL [URL ...], --url URL [URL ...]
                        List of URLs of courses to download.
  -o OUTPUT, --output OUTPUT
                        Output directory in which to place downloaded course
                        content.
  -v, --verbose         Display status messages during download.
```

## Backlog / TODOs

(pull requests welcome)

- Deal with courses that lock successive sections until previous is completed
- Add semantic versioning
- Consider setting up as PyPi package
- Clean up error/exception handling
- Cache known downloaded content cleanly
- Consider parallelizing lesson downloads
