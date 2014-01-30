# -*- coding: utf-8 -*-

from js.jquery import jquery
from js.jqueryui import jqueryui
from fanstatic import Library, Resource, Group


# BlueImp Uploader
# http://blueimp.github.io/jQuery-File-Upload/

library = Library('blueimp_upload', 'blueimp_files')

transport = Resource(
    library, 'js/jquery.iframe-transport.js',
    depends=[jquery], bottom=True)

upload = Resource(
    library, 'js/jquery.fileupload.js',
    depends=[transport], bottom=True)

ui = Resource(
    library, 'js/jquery.fileupload-ui.js',
    depends=[upload, jqueryui], bottom=True)

process = Resource(
    library, 'js/jquery.fileupload-process.js',
    depends=[jquery], bottom=True)

css = Resource(library, 'css/jquery.fileupload-ui.css')

uploader = Group([ui, css, process])
