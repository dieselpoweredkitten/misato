import os

from kyoto.helpers import Module
from PyODConverter import DocumentConverter

from misato.settings import (
  OFFICE_LISTENER,
  UPLOAD_PATH,
  OUTPUT_PATH,
  MEDIA_URL,
)

from misato.utils import gen_filename, get_filepath


class Office(Module):

  def convert(self, filename):
    input_path = os.path.join(UPLOAD_PATH, filename)
    if os.path.exists(input_path):
      office = DocumentConverter(OFFICE_LISTENER)
      output_path = os.path.join(get_filepath(filename, OUTPUT_PATH), 'index.html')
      result = office.convert(input_path, output_path)
      return True
    else:
      raise Exception('File doesnt exists')

  def url_for(self, filename):
    path = os.path.join(OUTPUT_PATH, filename, 'index.html')
    if os.path.exists(path):
      return os.path.join(MEDIA_URL, filename, 'index.html')
    else:
      raise Exception('File doesnt exists')


class FileManager(Module):

  def get(self, filename):
    """
    Returns file by filename
    """
    path = get_filepath(filename)
    if os.path.exists(path):
      fileobj = open(path, 'rb')
      yield None
      yield fileobj
    else:
      raise Exception('File doesnt exist')

  def create(self, stream):
    """
    Uploads file to tmp directory
    """
    filename = gen_filename()
    path = get_filepath(filename)
    with open(path, 'wb') as output:
      output.write(stream.read())
    return filename

  def delete(self, filename):
    """
    Deletes file
    """
    path = get_filepath(filename)
    if os.path.exists(path):
      os.remove(path)
    else:
      raise Exception('File doesnt exist')
    return True

  def list(self):
    """
    Same as `ls` or `dir`
    """
    return os.listdir(UPLOAD_PATH)
