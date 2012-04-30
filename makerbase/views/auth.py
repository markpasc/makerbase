import json
from urllib import urlencode
from urlparse import parse_qs, parse_qsl, urlsplit, urlunsplit

from flask import redirect, request, session, url_for
from flaskext.login import LoginManager, login_user, logout_user
import oauth2
import requests

from makerbase import app
from makerbase.models import User


login_manager = LoginManager()
login_manager.setup_app(app, add_context_processor=True)
login_manager.user_loader(User.get)


@app.route('/signin/github')
def signin_github():
    try:
        next_url = request.args['next']
    except KeyError:
        pass
    else:
        session['signin_next_url'] = next_url

    urlparts = urlsplit(request.base_url)
    params = {
        'client_id': app.config['GITHUB_CLIENT_ID'],
        'redirect_url': urlunsplit((urlparts.scheme, urlparts.netloc, url_for('complete_github'), None, None)),
        'scope': '',
    }
    redirect_url = 'https://github.com/login/oauth/authorize?%s' % urlencode(params)
    return redirect(redirect_url)


@app.route('/signin/twitter')
def signin_twitter():
    urlparts = urlsplit(request.base_url)
    callback_url = urlunsplit((urlparts.scheme, urlparts.netloc, url_for('complete_twitter'), None, None))

    consumer = oauth2.Consumer(key=app.config['TWITTER_KEY'], secret=app.config['TWITTER_SECRET'])
    client = oauth2.Client(consumer)
    query_args = {'oauth_callback': callback_url}
    request_token_url = urlunsplit(('https', 'api.twitter.com', '/oauth/request_token', urlencode(query_args), None))
    resp, content = client.request(request_token_url, 'GET')
    assert resp.status == 200

    request_token = dict(parse_qsl(content))
    session['twitter_request_token'] = request_token
    redirect_url = 'https://api.twitter.com/oauth/authorize?oauth_token=%s' % request_token['oauth_token']

    try:
        next_url = request.args['next']
    except KeyError:
        pass
    else:
        session['signin_next_url'] = next_url

    return redirect(redirect_url)


@app.route('/signout')
def signout():
    logout_user()
    return redirect(url_for('home'))


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
    user.name = github_user.get('name') or github_user['login']
    user.avatar_url = github_user['avatar_url']
    user.profile_url = github_user['html_url']
    user.save()

    login_user(user)

    try:
        next_url = session['signin_next_url']
    except KeyError:
        next_url = url_for('home')
    else:
        del session['signin_next_url']
    return redirect(next_url)


@app.route('/complete/twitter')
def complete_twitter():
    try:
        verifier = request.args.get('oauth_verifier')
    except KeyError:
        raise  # TODO

    request_token = session['twitter_request_token']
    del session['twitter_request_token']

    consumer = oauth2.Consumer(key=app.config['TWITTER_KEY'], secret=app.config['TWITTER_SECRET'])
    token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(verifier)
    client = oauth2.Client(consumer, token)
    resp, content = client.request('https://api.twitter.com/oauth/access_token', 'POST')
    assert resp.status == 200

    access_token = dict(parse_qsl(content))
    token = oauth2.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
    client = oauth2.Client(consumer, token)
    resp, content = client.request('https://api.twitter.com/account/verify_credentials.json?skip_status=true')
    assert resp.status == 200

    twitter_user = json.loads(content)
    userid = u'twitter:%s' % twitter_user['id']
    user = User.get(userid)
    if user is None:
        user = User(userid)
    user.name = twitter_user['name']
    user.avatar_url = twitter_user['profile_image_url']
    user.profile_url = u'https://twitter.com/%s' % twitter_user['screen_name']
    user.save()

    login_user(user)

    try:
        next_url = session['signin_next_url']
    except KeyError:
        next_url = url_for('home')
    else:
        del session['signin_next_url']
    return redirect(next_url)
