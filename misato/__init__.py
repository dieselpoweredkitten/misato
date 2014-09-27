import magic
import tarfile
import hashlib

import os
import os.path

import shutil
import tempfile

import logging
import contextlib

import kyoto
import kyoto.conf

import pylokit
import wand.image


@kyoto.private
@contextlib.contextmanager
def convert_to_pdf(path, mimetype):
    """
    Converts given document to PDF
    """
    with tempfile.NamedTemporaryFile(mode="wb") as output:
        if mimetype == "application/pdf": # just copy
            shutil.copy(path, output)
        else:
            with pylokit.Office(kyoto.conf.settings.LIBREOFFICE_PATH) as office:
                with office.documentLoad(path) as document:
                    document.saveAs(output.name, fmt="pdf")
        yield output.name

@kyoto.private
@contextlib.contextmanager
def convert_to_png(path):
    """
    Converts given document to bunch of PNG images
    TODO: set additional image attributes, like compression
    """
    with wand.image.Image(filename=path) as document:
        directory = tempfile.mkdtemp()
        filename = os.path.join(directory, "%d.png")
        document.save(filename=filename)
        yield directory
    shutil.rmtree(directory)

@kyoto.private
@contextlib.contextmanager
def extract_text_data(path, mimetype):
    """
    Tries to extract text from document
    """
    if mimetype == "application/pdf":
        raise NotImplementedError
    else:
        with tempfile.NamedTemporaryFile(mode="wb") as output:
            with pylokit.Office(kyoto.conf.settings.LIBREOFFICE_PATH) as office:
                with office.documentLoad(path) as document:
                    document.saveAs(output.name, fmt="txt")
            yield output.name

@kyoto.private
@contextlib.contextmanager
def create_archive(doc, pdf, txt, imgs):
    with tempfile.NamedTemporaryFile(mode="wb") as tfile:
        with tarfile.open(tfile.name, "w:gz") as archive:
            archive.add(doc, arcname="document.bin")
            archive.add(pdf, arcname="document.pdf")
            archive.add(txt, arcname="document.txt")
            archive.add(imgs, arcname="pages/")
        yield tfile.name

@kyoto.private
def create_checksum(archive):
    h = hashlib.new("sha1")
    with open(archive, "rb") as archive:
        while archive:
            chunk = archive.read(kyoto.conf.settings.READ_CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

@kyoto.private
@contextlib.contextmanager
def receive_document(stream):
    with tempfile.NamedTemporaryFile(mode="wb") as document:
        for chunk in stream:
            document.write(chunk)
            document.flush()
        yield document.name

@kyoto.private
def return_stream(path):
    with open(path, "rb") as stream:
        while stream:
            chunk = stream.read(kyoto.conf.settings.READ_CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

@kyoto.private
@contextlib.contextmanager
def process_document(doc, mimetype):
    """
    doc -> pdf + txt -> png -> archive
    """
    with convert_to_pdf(doc, mimetype) as pdf:
        with extract_text_data(doc, mimetype) as txt:
            with convert_to_png(pdf) as img:
                with create_archive(doc, pdf, txt, img) as arc:
                    yield arc

@kyoto.blocking
def process(checksum, stream=None):
    with receive_document(stream) as document:
        with magic.Magic(mimetype=True) as m:
            mimetype = m.from_file(document)
        if mimetype in kyoto.conf.settings.ALLOWED_MIMETYPES:
            with process_document(document, mimetype) as archive:
                metadata = {
                    "mimetype": mimetype,
                    "checksum": create_checksum(archive)
                }
                yield metadata
                yield from return_stream(archive)
        else:
            raise NotImplementedError
