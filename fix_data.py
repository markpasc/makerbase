from datetime import datetime, timedelta
from functools import wraps

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
