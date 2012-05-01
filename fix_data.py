from datetime import datetime, timedelta
from functools import wraps
from itertools import islice

import makerbase
from makerbase.models import *


def for_class(*classes):
    def do_that(fn):
        @wraps(fn)
        def do_for_class():
            for cls in classes:
                keys = cls.get_bucket().get_keys()
                for key in keys:
                    obj = cls.get(key)
                    fn(obj)
        return do_for_class
    return do_that


@for_class(Maker)
def fix_maker_history(maker):
    for histitem in maker.history:
        # Fix the actions.
        if histitem.action == 'create':
            histitem.action = 'addmaker'
        elif histitem.action == 'edit':
            histitem.action = 'editmaker'

        # Make sure the maker is tagged.
        if histitem.maker is None:
            histitem.add_link(maker, tag='maker')

        histitem.save()


@for_class(Project)
def fix_project_history(project):
    for histitem in project.history:
        # Fix the actions.
        if histitem.action == 'create':
            histitem.action = 'addproject'
        elif histitem.action == 'edit':
            histitem.action = 'editproject'

        # Make sure the project is tagged.
        if histitem.project is None:
            histitem.add_link(project, tag='project')

        histitem.save()


@for_class(Project)
def save_all_projects(project):
    project.save()


@for_class(Maker)
def save_all_makers(maker):
    maker.save()


@for_class(Participation)
def link_party_history_to_party(party):
    for histitem in party.history:
        histitem.add_link(party, tag='participation')
        histitem.save()


@for_class(Project, Maker)
def add_data_to_history(obj):
    history = sorted(obj.history, key=lambda h: h.when, reverse=True)
    histitems = list(islice(history, 1))
    if not histitems:
        return
    newest_item = histitems[0]

    if newest_item.action.endswith('party'):
        new_data = newest_item.participation.get_entity_data()
    else:
        new_data = obj.get_entity_data()

    newest_item.old_data = {}
    newest_item.new_data = new_data
    newest_item.save()


@for_class(Participation)
def remove_party_reasons(party):
    try:
        del party.reason
    except AttributeError:
        pass
    else:
        party.save()
