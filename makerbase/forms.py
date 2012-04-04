# coding=utf-8

from datetime import datetime
from itertools import chain

from wtforms import Form, DateTimeField, FieldList, FormField, HiddenField, TextField, validators


class MonthField(DateTimeField):

    def __init__(self, label=None, validators=None, format='%Y-%m', **kwargs):
        super(MonthField, self).__init__(label, validators, format, **kwargs)

    def process_formdata(self, valueslist):
        if not valueslist:
            return
        date_str = u' '.join(valueslist).strip().lower()

        dt = None
        formats = (self.format, '%Y/%m', '%m-%Y', '%m/%Y', '%b %Y', '%Y %b', '%B %Y', '%Y %B')
        formats = chain(formats, (format.replace('%Y', '%y') for format in formats))
        for format in formats:
            try:
                dt = datetime.strptime(date_str, format)
            except ValueError:
                pass
            else:
                break

        if dt is None:
            self.data = None
            raise ValueError("value %r not in month format" % date_str)
        self.data = dt.date()


class MakerForm(Form):

    name = TextField(u'Name', [validators.Length(min=1, max=100), validators.Required()])
    avatar_url = TextField(u'Avatar URL', [validators.URL(require_tld=True), validators.Optional()],
        description=u'Avatar images should display at 150×150 and 75×75 pixel sizes.')
    html_url = TextField(u'Web URL', [validators.URL(require_tld=True), validators.Required()],
        description=u"Web URLs should be the address of the person's main personal web site.")


class ParticipationForm(Form):

    role = TextField(u'Role', [validators.Length(min=1, max=140)])
    start_date = MonthField(u'Start month')
    end_date = MonthField(u'End month', [validators.Optional()])


class ProjectForm(Form):

    name = TextField(u'Name', [validators.Length(min=1, max=50), validators.Required()])
    html_url = TextField(u'Web URL', [validators.URL(require_tld=True), validators.Required()],
        description=u'Web URLs should be the address of a hosted web app or the official web site for a project of some other kind.')
    description = TextField(u'Description', [validators.Length(max=140)])
    avatar_url = TextField(u'Avatar URL', [validators.URL(require_tld=True), validators.Optional()],
        description=u'Avatar images should display at 150×150 and 75×75 pixel sizes.')


class ProjectAddParticipationForm(ParticipationForm):

    maker = TextField(u'Maker ID', [validators.Required()])
