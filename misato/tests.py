import os
import os.path

import magic
import misato
import unittest


class MisatoTestCase(unittest.TestCase):

    def setUp(self):
        self.pdf = misato.convert_to_pdf("samples/sample.odt")

    def test_convert_to_pdf(self):
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_file(self.pdf)
            self.assertEqual(mimetype, "application/pdf")

    def test_convert_to_png(self):
        previews = misato.convert_to_png(self.pdf)
        self.assertTrue(previews.startswith("/tmp/"))
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_file(os.path.join(previews, "0.png"))
            self.assertEqual(mimetype, "image/png")

    def test_create_metadata(self):
        previews = misato.convert_to_png(self.pdf)
        metadata = misato.create_metadata(previews)
        self.assertTrue(isinstance(metadata, dict))
        self.assertEqual(metadata.get("pages_count"), 1)

    def test_convert_odt(self):
        stream = misato.return_stream("samples/sample.odt")
        response = misato.convert(stream)
        self.assertEqual(next(response), {"pages_count": 1})
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_buffer(next(response))
            self.assertEqual(mimetype, "application/gzip")

    def test_convert_doc(self):
        stream = misato.return_stream("samples/sample.doc")
        response = misato.convert(stream)
        self.assertEqual(next(response), {"pages_count": 1})
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_buffer(next(response))
            self.assertEqual(mimetype, "application/gzip")

    def test_convert_docx(self):
        stream = misato.return_stream("samples/sample.docx")
        response = misato.convert(stream)
        self.assertEqual(next(response), {"pages_count": 1})
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_buffer(next(response))
            self.assertEqual(mimetype, "application/gzip")

    def tearDown(self):
        os.remove(self.pdf)
