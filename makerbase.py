import json
from urllib import urlencode
from urlparse import parse_qs, urlunsplit

from flask import Flask, abort, redirect, render_template, request, url_for
from flaskext.login import LoginManager, login_user
import requests
import riak


app = Flask(__name__)

login_manager = LoginManager()
login_manager.setup_app(app, add_context_processor=True)

riakclient = riak.RiakClient(port=8087, transport_class=riak.RiakPbcTransport)


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
    raise NotImplementedError()


@app.errorhandler(404)
def not_found(exc):
    return render_template('not_found.html')


class Robject(object):

    _bucket = None

    def __init__(self, *args, **kwargs):
        if args:
            self.id = args[0]
        if kwargs:
            self.__dict__.update(kwargs)

    @classmethod
    def get(cls, userid):
        entity = riakclient.bucket(cls._bucket).get(userid.encode('utf-8'))
        if not entity or not entity.exists():
            app.logger.warning("Tried to load %s with id %r but found none", cls.__name__, userid)
            return None

        self = cls()
        self.__dict__.update(entity.get_data())
        self.id = userid
        self._entity = entity
        app.logger.debug("Found for %s id %r entity %r! Returning %s %r!", cls._bucket, userid, entity, cls.__name__, self)
        return self

    def get_entity_data(self):
        return dict((k, v) for k, v in self.__dict__.iteritems() if not k.startswith('_'))

    def save(self):
        try:
            entity = self._entity
        except AttributeError:
            entity = riakclient.bucket(self._bucket).new(self.id.encode('utf-8'), data=self.get_entity_data())
            self._entity = entity
        else:
            entity.set_data(self.get_entity_data())
        entity.store()


class Project(Robject):
    _bucket = 'project'

class Maker(Robject):
    _bucket = 'maker'

class Participation(Robject):
    _bucket = 'participation'

class User(Robject):

    _bucket = 'user'

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id

login_manager.user_loader(User.get)

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
