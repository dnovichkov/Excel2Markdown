# Excel2Markdown
[![Build Status](https://travis-ci.com/dnovichkov/Excel2Markdown.svg?branch=master)](https://travis-ci.com/dnovichkov/Excel2Markdown)
## Technical Details

Tested for Python3.6, 3.7. 

Links for virtual env setting:
[https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html) and 
[https://virtualenv.pypa.io/en/stable/userguide/](https://docs.python.org/3/library/venv.html)

For my Win-machine:
```
python -m venv env
call venv/scripts/activate.bat
```

Requirements install:

```
pip install -r requirements.txt
```


Run script 

```
python main.py ExcelTestFile.xlsx
```

Run tests:
`python -m unittest discover tests/`
