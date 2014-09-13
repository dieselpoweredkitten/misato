import os
import shutil

import os.path
import tempfile

import magic
import tarfile

import kyoto
import kyoto.conf

import pylokit
import wand.image


@kyoto.private
def convert_to_pdf(path):
    """
    Converts given document to PDF
    """
    (fd, output) = tempfile.mkstemp(suffix=".pdf")
    with pylokit.Office(kyoto.conf.settings.LIBREOFFICE_PATH) as office:
        with office.documentLoad(path) as document:
            document.saveAs(output, fmt="pdf")
    return output

@kyoto.private
def convert_to_png(path):
    """
    Converts given document to bunch of PNG images
    TODO: set additional image attributes, like compression
    """
    with wand.image.Image(filename=path) as document:
        directory = tempfile.mkdtemp()
        filename = os.path.join(directory, "%d.png")
        document.save(filename=filename)
    return directory

@kyoto.private
def create_metadata(previews):
    """
    Returns dictionary that contains additional info about converted document, e.g. pages count
    """
    previews = os.listdir(previews)
    return {
        "pages_count": len(previews)
    }

@kyoto.private
def create_archive(pdf, previews):
    (_, filename) = tempfile.mkstemp(prefix="archive_")
    with tarfile.open(filename, "w:gz") as archive:
        archive.add(pdf, arcname="document.pdf")
        archive.add(previews, arcname="previews/")
    return filename

@kyoto.private
def delete_tempfiles(files):
    try:
        for f in files:
            if f:
                os.remove(f)
    except Exception as exception:
        pass

@kyoto.private
def delete_tempdirs(dirs):
    try:
        for d in dirs:
            if d:
                shutil.rmtree(d)
    except Exception as exception:
        pass

@kyoto.private
def receive_stream(signature, stream):
    (_, filename) = tempfile.mkstemp(prefix="original_")
    with open(filename, "wb") as document:
        document.write(signature)
        for chunk in stream:
            document.write(chunk)
    return filename

@kyoto.private
def return_stream(path):
    with open(path, "rb") as stream:
        while stream:
            chunk = stream.read(kyoto.conf.settings.READ_CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

@kyoto.blocking
def convert(stream=None):
    signature = next(stream)
    with magic.Magic(mimetype=True) as m:
        mimetype = m.from_buffer(signature)
        if not mimetype in kyoto.conf.settings.ALLOWED_MIMETYPES:
            raise ValueError("Invalid document mimetype: {0}".format(mimetype))
        else:
            original = pdf = archive = previews = None
            try:
                original = receive_stream(signature, stream)
                if mimetype != "application/pdf":
                    pdf = convert_to_pdf(original)
                else:
                    pdf = original
                previews = convert_to_png(pdf)
                metadata = create_metadata(previews)
                archive = create_archive(pdf, previews)
            except Exception as exception:
                raise
            else:
                yield metadata
                yield from return_stream(archive)
            finally:
                delete_tempfiles([original, pdf, archive])
                delete_tempdirs([previews])
