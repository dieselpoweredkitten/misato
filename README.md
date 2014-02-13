Misato
=======

Misato does hard work: receives office documents in doc/docx/odt/pdf formats and converts it to html

Installation
=======

For misato-server, you'll need install following libraries and packages:

* `libreoffice` and `python-uno` from your distro repos
* `PyODConverter` from PyPI (install it with pip)
* `kyoto` from [github](https://github.com/kyoto-project/kyoto)

After it, pull this repo, move to misato folder and type into terminal:

```bash
$ python serve.py
```

It starts Misato server on `8060` port.

For client, you'll need only `kyoto` package.


Usage
=======

```python
from kyoto.client import Client

listener = ('example.com', 8060) # misato-server address
server = Client(listener)

filemanager = server.FileManager # used in uploading, retrieving and deleting files
office = server.Office # used in document converting

with open('/path/to/kittens.docx', 'rb') as document:
  # after success upload, returns unique filename for document
  uuid = filemanager.call('create', stream=document)
  # which used as folder for output html
  result = office.call('convert', [uuid])
  # result == true, or false/exception if something went wrong

```
