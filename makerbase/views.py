import json
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit

from flask import abort, redirect, render_template, request, url_for, flash
from flaskext.login import LoginManager, login_user, login_required
import requests

from makerbase import app
from makerbase.forms import ProjectForm
from makerbase.models import *


login_manager = LoginManager()
login_manager.setup_app(app, add_context_processor=True)
login_manager.user_loader(User.get)


@app.template_filter('date')
def date_format(dt, format):
    return dt.strftime(format)


@app.template_filter('pretty_url')
def pretty_url(url):
    urlparts = urlsplit(url)
    host, path = urlparts.netloc, urlparts.path
    if host.startswith('www.'):
        host = host[4:]
    if path == '/':
        path = ''
    elif len(path) > 23:
        path = path[:20] + '...'
    return host + path


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/project/<slug>')
def project(slug):
    proj = Project.get(slug)
    if proj is None:
        # TODO: don't 404, but rather offer to create the project?
        abort(404)

    return render_template('project.html', project=proj)


@app.route('/maker/<slug>')
def maker(slug):
    maker = Maker.get(slug)
    if maker is None:
        # TODO: don't 404, but offer to create a page for this maker?
        abort(404)

    return render_template('maker.html', maker=maker)


@app.route('/project/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(slug):
    proj = Project.get(slug)
    if proj is None:
        # TODO: don't 404, but rather offer to create the project?
        abort(404)

    form = ProjectForm(request.form, proj)
    if request.method == 'POST' and form.validate():
        # TODO: save a historical project item
        form.populate_obj(proj)
        proj.save()

        flash('derp')
        return redirect(url_for('project', slug=slug))

    return render_template('edit_project.html', form=form, project=proj)


@app.errorhandler(404)
def not_found(exc):
    return render_template('not_found.html')


@app.route('/signin/github')
def signin_github():
    params = {
        'client_id': app.config['GITHUB_CLIENT_ID'],
        'redirect_url': urlunsplit(('http', 'localhost:5000', url_for('complete_github'), None, None)),
        'scope': '',
    }
    return redirect('https://github.com/login/oauth/authorize?%s' % urlencode(params))


@app.route('/complete/github')
def complete_github():
    try:
        code = request.args.get('code')
    except KeyError:
        raise  # TODO

    params = {
        'client_id': app.config['GITHUB_CLIENT_ID'],
        'client_secret': app.config['GITHUB_SECRET'],
        'code': code,
    }
    token_resp = requests.post('https://github.com/login/oauth/access_token', data=params)
    token_params = parse_qs(token_resp.content)
    access_token = token_params['access_token']

    user_resp = requests.get('https://api.github.com/user', data={'access_token': access_token})
    github_user = json.loads(user_resp.content)

    userid = u"github:%s" % github_user['login']
    user = User.get(userid)
    if user is None:
        user = User(userid)
    user.name = github_user['name']
    user.avatar_url = github_user['avatar_url']
    user.profile_url = github_user['html_url']
    user.save()

    login_user(user)

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.config.from_envvar('MAKERBASE_SETTINGS')
    app.run(debug=True)