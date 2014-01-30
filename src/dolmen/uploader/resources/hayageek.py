# -*- coding: utf-8 -*-

from js.jquery import jquery
from js.jqueryui import jqueryui
from fanstatic import Library, Resource, Group


# Hayageek uploader
# http://hayageek.com/docs/jquery-upload-file.php

library = Library('hayageek_upload', 'hayageek_files')

upload = Resource(
    library, 'jquery.uploadfile.js',
    depends=[jquery], bottom=True)

css = Resource(library, 'uploadfile.css')

uploader = Group([upload, css])
