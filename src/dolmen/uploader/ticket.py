# -*- coding: utf-8 -*-

import re
import uuid
from os.path import join


UUID = re.compile(
    "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


def get_ticket_path(uid, check=True):
    if check is True:
        assert UUID.match(uid)
    # sequence of paths to create + filename
    dirpath = join(uid[0:2], uid[2:4], uid[4:6], uid[6:8])
    return dirpath, uid[9:]


def generate_ticket():
    ticket = str(uuid.uuid1())
    dirpath, filename = get_ticket_path(ticket, check=False)
    return ticket, dirpath, filename
