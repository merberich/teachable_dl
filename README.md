# teachable_dl

Python 3 command-line tool for downloading your purchased + free courses on the teachable platform.

## Installation

1) Install latest Python 3 version.

2) Download this repository.

3) Start a virtual environment.

4) `pip` install via `requirements.txt`.

5) Create a "login file" containing your username and password to the Teachable SSO (see: https://sso.teachable.com) following the JSON form:
```json
{
  "username": "your-username-or-email-here",
  "password": "your-teachable-sso-password-here"
}
```

The tool should now be ready to use.

## Example

Downloading two different courses from different teachable schools. Login file has been placed in the same directory as the script is executed from. Output has been redirected to a custom folder. Note that more than one course URL can be specified at a time.
```sh
(.venv) example@example:~/scripts/teachable_dl python3 teachable_dl.py -l login_file.json -o ~/online_courses/teachable -u https://courses.data36.com/courses/enrolled/455539 https://milk-street-cooking-school.teachable.com/courses/enrolled/739683
```

## Full Usage

```
usage: teachable_dl.py [-h] -l LOGIN_FILE [-u URL [URL ...]] [-o OUTPUT] [-v]

Teach:Able content downloader.

options:
  -h, --help            show this help message and exit
  -l LOGIN_FILE, --login-file LOGIN_FILE
                        Login file as JSON in form: { "username": "your-username-here", "password": "your-password-
                        here"}
  -u URL [URL ...], --url URL [URL ...]
                        List of URLs of courses to download.
  -o OUTPUT, --output OUTPUT
                        Output directory in which to place downloaded course content.
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
