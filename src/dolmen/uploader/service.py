# -*- coding: utf-8 -*-

import ConfigParser
import cgi
import datetime
import hashlib
import logging
import os
import re
import shutil
import uuid

from os.path import join
from stat import ST_SIZE, ST_CTIME
from .ticket import get_ticket_path, generate_ticket


RETRY = 10
CHUNKSIZE = 4096
FILEINFO = 'fileinfo'
INNER_ENCODING = 'utf-8'
HTTP_ENCODING = 'iso-8859-1'

logger = logging.getLogger('verification')
logger.setLevel(logging.INFO)


_filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
_windows_device_files = (
    'CON', 'AUX', 'COM1', 'COM2', 'COM3',
    'COM4', 'LPT1', 'LPT2', 'LPT3', 'PRN', 'NUL')


def clean_filename(filename):
    """Borrowed from Werkzeug : http://werkzeug.pocoo.org/
    """
    if isinstance(filename, unicode):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('ascii', 'ignore')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_ascii_strip_re.sub('', '_'.join(
                   filename.split()))).strip('._')

    # on nt a couple of special files are present in each folder. We
    # have to ensure that the target file is not such a filename. In
    # this case we prepend an underline
    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename


def write_fileinfo(path, **more):
    config = ConfigParser.RawConfigParser()
    stats = os.stat(path)
    config.add_section(FILEINFO)
    config.set(FILEINFO, 'size', stats[ST_SIZE])
    config.set(FILEINFO, 'date', stats[ST_CTIME])

    for key, info in more.items():
        config.set(FILEINFO, key, info)

    config_path = path + '.cfg'
    with open(config_path, 'wb') as configfile:
        config.write(configfile)
    return config_path


def create_file(path, name):
    filepath = join(path, name)
    try:
        if not os.path.exists(filepath):
            return filepath
    except OSError, e:
        logger.error(e)
    return None


def create_directory(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    except OSError, e:
        return None


def persist_files(environ, destination, basename):
    """Document me.
    """
    fields = cgi.FieldStorage(
        fp=environ['wsgi.input'], environ=environ, keep_blank_values=1)    

    # store files on fs
    files = []
    index = 1
        
    for name in fields.keys():
        field = fields[name]
        if not isinstance(field, list):
            # handle multiple fields of same name (html5 uploads)
            field = [field]

        for item in field:
            if isinstance(item, cgi.FieldStorage) and item.filename:
                # this is a file field.
                filename = "%s_%s" % (basename, index)
                path = join(destination, filename)
                with open(path, 'w') as upload:
                    shutil.copyfileobj(item.file, upload)

                files.append((filename, path))
                original = clean_filename(item.filename)
                write_fileinfo(path, **{'filename': original})
                index += 1

    return files


class FilesystemHandler(object):
    """Document me.
    """

    def __init__(self, tmpdir, upload, namespace):
        self.__temp = tmpdir
        self.__upload = upload
        self.namespace = namespace

    @property
    def upload_path(self):
        path = join(self.__upload, self.namespace)
        return create_directory(path)

    @property
    def temporary_path(self):
        path = join(self.__temp, self.namespace)
        return create_directory(path)

    def ticket_files(self, ticket):
        path, filename = get_ticket_path(ticket)
        for listed in os.listdir(path):
            if listed.startswith(filename) and not listed.endswith('.cfg'):
                yield listed

    def upload(self, id, environ):
        """The heart of the handler.
        """
        path, basename = get_ticket_path(id)
        destination = create_directory(join(self.upload_path, path))
        create_directory(destination)
        files = persist_files(environ, destination, basename)
        return files


class Uploader(object):
    """the uploading application
    """
    def __init__(self, tmpdir, upload, namespace):
        self.handler = FilesystemHandler(tmpdir, upload, namespace)

    def __call__(self, environ, start_response):
        ticket, ticket_path, filename = generate_ticket()
        files = self.handler.upload(ticket, environ)
        status = '200 OK'
        response_headers = [('Content-type','text/plain')]
        start_response(status, response_headers)
        return [path for filename, path in files]


def upload_service(*global_conf, **local_conf):
    namespace = local_conf.get('namespace')
    tmpdir = local_conf.get('tmpdir')
    upload = local_conf.get('upload')

    return Uploader(tmpdir, upload, namespace)
