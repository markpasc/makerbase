import json
import traceback
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit

from flask import abort, flash, make_response, redirect, render_template, request, Response, url_for
from flask.views import MethodView
from flaskext.login import LoginManager, current_user, login_user, login_required
import requests
from werkzeug.datastructures import MultiDict

from makerbase import app
from makerbase.forms import MakerForm, ProjectForm, ParticipationForm, ProjectAddParticipationForm
from makerbase.models import *


@app.route('/')
def home():
    # TODO: LOOOOOL don't get all the keys in the bucket.
    project_keys = Project.get_bucket().get_keys()
    projects = (Project.get(key) for key in project_keys)
    return render_template('home.html', projects=projects)


@app.route('/project/<slug>')
def project(slug):
    forms = {}

    proj = Project.get(slug)
    if proj is None:
        if current_user.is_authenticated():
            forms['project_form'] = ProjectForm()
        html = render_template('project-new.html', slug=slug, **forms)
        return make_response(html, 404)

    parties = list(proj.parties)

    if current_user.is_authenticated():
        forms['project_form'] = ProjectForm(obj=proj)
        forms['add_party_form'] = ProjectAddParticipationForm()
        for party in parties:
            party.form = ParticipationForm(obj=party)

    return render_template('project.html', project=proj, parties=parties, **forms)


@app.route('/maker/<slug>')
def maker(slug):
    forms = {}

    maker = Maker.get(slug)
    if maker is None:
        if current_user.is_authenticated():
            forms['maker_form'] = MakerForm()
        html = render_template('maker-new.html', slug=slug, **forms)
        return make_response(html, 404)

    parties = list(maker.parties)

    if current_user.is_authenticated():
        forms['maker_form'] = MakerForm(obj=maker)

    return render_template('maker.html', maker=maker, parties=parties, **forms)


@app.route('/maker/<slug>/history')
def maker_history(slug):
    maker = Maker.get(slug)
    if maker is None:
        html = render_template('maker-new.html', slug=slug)
        return make_response(html, 404)

    history = list(maker.history)

    return render_template('maker-history.html', maker=maker, history=history)


@app.errorhandler(404)
def not_found(exc):
    return render_template('not_found.html')
