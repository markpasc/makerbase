# coding=utf-8

from wtforms import Form, DateField, FieldList, FormField, HiddenField, TextField, validators


class ParticipationForm(Form):

    role = TextField(u'Role', [validators.Length(min=1, max=140)])
    start_date = DateField(u'Start date')
    end_date = DateField(u'End date', [validators.Optional()])


class ProjectForm(Form):

    name = TextField(u'Name', [validators.Length(min=1, max=50), validators.Required()])
    html_url = TextField(u'Web URL', [validators.URL(require_tld=True), validators.Required()],
        description=u'Web URLs should be the address of a hosted web app or the official web site for a project of some other kind.')
    description = TextField(u'Description', [validators.Length(max=140)])
    avatar_url = HiddenField(u'Avatar URL', [validators.URL(require_tld=True)],
        description=u'Avatar images should display at 150×150 and 75×75 pixel sizes.')


class ProjectAddParticipationForm(ParticipationForm):

    maker = HiddenField(u'Maker ID', [validators.Required()])
