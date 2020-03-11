import flask

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

        # TODO
        #return something

    return flask.render_template('main/index.html', form = form)
