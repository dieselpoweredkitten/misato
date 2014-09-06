import magic
import misato
import os.path
import unittest


class ConvertingTestCase(unittest.TestCase):

    def test_convert_to_pdf(self):
        pdf = misato.convert_to_pdf("samples/sample.odt")
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_file(pdf)
            self.assertEqual(mimetype, "application/pdf")

    def test_convert_to_png(self):
        pdf = misato.convert_to_pdf("samples/sample.odt")
        images = misato.convert_to_png(pdf)
        self.assertTrue(images.startswith("/tmp/"))
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_file(os.path.join(images, "0.png"))
            self.assertEqual(mimetype, "image/png")

    def test_convert(self):
        stream = misato.return_stream("samples/sample.odt")
        response = misato.convert(stream)
        self.assertEqual(next(response), {"pages_count": 1})
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_buffer(next(response))
            self.assertEqual(mimetype, "application/gzip")
