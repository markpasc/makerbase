#!/usr/bin/env python

import codecs
import json
import os
from os.path import join, exists

from makerbase.models import *


for dirname in ('makers', 'projects'):
    if not exists(dirname):
        os.mkdir(dirname)

for key in Maker.get_bucket().get_keys():
    maker = Maker.get(key)

    filename = join('makers', maker._id + '.json')
    with codecs.open(filename, 'w', 'utf-8') as f:
        data = maker.get_api_data(include_links=False)
        json.dump(data, f, indent=4, sort_keys=True)

for key in Project.get_bucket().get_keys():
    project = Project.get(key)

    filename = join('projects', project._id + '.json')
    with codecs.open(filename, 'w', 'utf-8') as f:
        parties = list()
        for party in project.parties:
            data = party.get_api_data(include_links=False)
            del data['id']
            data['maker'] = party.maker._id
            parties.append(data)

        data = project.get_api_data(include_links=False)
        data['participations'] = parties
        json.dump(data, f, indent=4, sort_keys=True)
