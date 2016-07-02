from flask import Flask, render_template, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap, WebCDN
from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp' # FIXME
manager = Manager(app)
bootstrap = Bootstrap(app)
app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
    '//cdnjs.cloudflare.com/ajax/libs/jquery/3.0.0/' # Use jquery 3.0.0
)

class RegisterForm(Form):
    email = StringField('Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Register')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print("A new user have successfully registred")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


if __name__ == '__main__':
    manager.run()

