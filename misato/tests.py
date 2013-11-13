import os
from io import BytesIO
from unittest import TestCase
from misato.utils import get_filepath
from misato.settings import UPLOAD_PATH
from misato.modules import FileManager, Office


class FileManagerTest(TestCase):

  def setUp(self):
    self.module = FileManager()
    self.fileobj = BytesIO('test')

  def test_create(self):
    response = self.module.create(self.fileobj)
    self.assertTrue(len(response) > 1)
    is_exists = os.path.exists(get_filepath(response))
    self.assertTrue(is_exists)

  def test_get(self):
    files = os.listdir(UPLOAD_PATH)
    if len(files) < 1:
      self.test_create()
      files = os.listdir(UPLOAD_PATH)
    document = files[0]
    response = self.module.get(document)
    result = next(response)
    self.assertEqual(result, None)
    fileobj = next(response)
    self.assertEqual(fileobj.read(), 'test')

  def test_get_unknown_file(self):
    document = 'kittens.pdf'
    with self.assertRaises(Exception, message="File doesnt exists"):
      response = self.module.get(document)
      next(response)

  def test_delete_unknown_file(self):
    document = 'kittens.pdf'
    with self.assertRaises(Exception, message="File doesnt exists"):
      response = self.module.delete(document)

  def test_list(self):
    response = self.module.list()
    self.assertEqual(response, [])

  def tearDown(self):
    files = os.listdir(UPLOAD_PATH)
    for item in files:
      item = os.path.join(UPLOAD_PATH, item)
      os.remove(item)


class OfficeTest(TestCase):

  def setUp(self):
    self.office = Office()
    self.filemanager = FileManager()

  def test_convert_unknown_file(self):
    filename = 'kittens.docx'
    with self.assertRaises(Exception, message="File doesnt exists"):
      result = self.office.convert(filename)

  def test_convert_docx(self):
    with open('test_data/demo.docx') as fileobj:
      uuid = self.filemanager.create(fileobj)
      result = self.office.convert(uuid)
      self.assertTrue(result)

  def test_convert_pdf(self):
    with open('test_data/rust.pdf') as fileobj:
      uuid = self.filemanager.create(fileobj)
      result = self.office.convert(uuid)
      self.assertTrue(result)

  def test_url_for_unknown_file(self):
    with self.assertRaises(Exception, message='File doesnt exists'):
      media_url = self.office.url_for('2ba3f1')
