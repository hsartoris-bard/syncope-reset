import flask
import requests
import json

from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField

bp = flask.Blueprint('main', __name__, url_prefix='/',
        template_folder='templates')

log = flask.current_app.logger

class UsernamePasswordForm(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')
    submit = SubmitField('submit')

@bp.route('/', methods=('GET', 'POST'))
def index():
    form = UsernamePasswordForm()

    if form.validate_on_submit():
        user = form.data['username']
        password = form.data['password']
        log.info(f"Beginning reset for {user}")

        key = update_syncope_password(user, password)
        return flask.render_template('main/index.html',
                key = key)

    return flask.render_template('main/index.html', form = form)


def update_syncope_password(username, password):
    base = "https://cas02.bard.edu/syncope/rest/users/self"

    auth_res = requests.get(base, auth=(username, password))
    if not auth_res.status_code == 200:
        msg = f"Failed to authenticate to Syncope as user {username}"
        log.error(msg)
        raise Exception(msg)

    user_dict = json.loads(auth_res.content)
    key = user_dict.get('key')
    if not key:
        msg = f"Failed to retrieve user key for {username}"
        log.error(f"{msg}; {user_dict}")
        raise Exception(msg)

    resources = user_dict.get('resources') or []
    if not 'AD' in resources:
        resources.append('AD')

    update_dict = {
            "@class": "org.apache.syncope.common.lib.patch.UserPatch",
            "key": key,
            "password": {
                "value": password,
                "onSyncope": True,
                "resources": resources
                }
            }
    update_res = requests.patch(f"{base}/{key}",
            json.dumps(update_dict),
            auth = (username, password),
            headers = {"Content-Type": "application/json"})

    if not update_res.status_code == 200:
        msg = f"Failed to update user {username} with body {update_dict}"
        log.error(msg)
        log.error(update_res.reason)
        log.error(update_res.content)
        raise Exception(msg)
    return key

