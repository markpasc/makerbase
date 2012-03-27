import json
import traceback
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit

from flask import abort, flash, redirect, render_template, request, Response, url_for
from flask.views import MethodView
from flaskext.login import LoginManager, current_user, login_user, login_required
import requests
from werkzeug.datastructures import MultiDict

from makerbase import app
from makerbase.forms import ProjectForm, ParticipationForm, ProjectAddParticipationForm
from makerbase.models import *


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/project/<slug>')
def project(slug):
    proj = Project.get(slug)
    if proj is None:
        # TODO: don't 404, but rather offer to create the project?
        abort(404)

    parties = list(proj.parties)

    forms = {}
    if current_user.is_authenticated():
        forms['project_form'] = ProjectForm(obj=proj)
        forms['add_party_form'] = ProjectAddParticipationForm()
        for party in parties:
            party.form = ParticipationForm(obj=party)

    return render_template('project.html', project=proj, parties=parties, **forms)


@app.route('/maker/<slug>')
def maker(slug):
    maker = Maker.get(slug)
    if maker is None:
        # TODO: don't 404, but offer to create a page for this maker?
        abort(404)

    return render_template('maker.html', maker=maker)


@app.errorhandler(404)
def not_found(exc):
    return render_template('not_found.html')
