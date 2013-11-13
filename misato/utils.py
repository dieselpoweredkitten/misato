import os
import uuid

from misato.settings import UPLOAD_PATH

def gen_filename():
  filename = str(uuid.uuid4())
  path = os.path.join(UPLOAD_PATH, filename)
  if not os.path.exists(path):
    return filename
  else:
    return generate_filename()

def get_filepath(filename, path=UPLOAD_PATH):
  return os.path.join(path, filename)
