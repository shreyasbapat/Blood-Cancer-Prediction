import datetime
import functools
import os
import re
import urllib

from flask import (Flask, flash, Markup, redirect, render_template, request,
                   Response, session, url_for)

from werkzeug import secure_filename
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache


# Blog configuration values.

# You may consider using a one-way hash to generate the password, and then
# use the hash again in the login view to perform the comparison. This is just
# for simplicity.
ADMIN_PASSWORD = 'secret'
APP_DIR = os.path.dirname(os.path.realpath(__file__))

# The playhouse.flask_utils.FlaskDB object accepts database URL configuration.
UPLOAD_FOLDER = '.'
# The secret key is used internally by Flask to encrypt session data stored
# in cookies. Make this unique for your app.
SECRET_KEY = 'shhh, secret!'

# This is used by micawber, which will attempt to generate rich media
# embedded objects with maxwidth=800.
SITE_WIDTH = 800


# Create a Flask WSGI app and configure it using values from the module.
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['last_name'] = ""

oembed_providers = bootstrap_basic(OEmbedCache())



def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

@app.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        username = request.form.get('username')
        # TODO: If using a one-way hash, you would also hash the user-submitted
        # password and do the comparison on the hashed versions.
        if password == app.config['ADMIN_PASSWORD'] and username == "admin":
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return render_template('upload_ready.html')
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')



@app.route('/upload/',methods = ['GET','POST'])
def upload_file():
    if request.method =='POST':
        file = request.files['file[]']
        if file:
            filename = secure_filename(file.filename)
            app.config['last_name'] = file.filename
            filenamecom = os.path.join(app.config['UPLOAD_FOLDER'],file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            os.rename(filenamecom, "static/"+file.filename)
            return render_template('show.html', user_image = "../static/"+file.filename)
    return render_template('upload.html')

def tell_the_fortune(path):
    li = [0.8,0.5,0.4,0.2]
    return li.index(max(li))

@app.route('/analyse/')
def analyse_it():
    path = "../static/" + app.config['last_name']
    maxi = tell_the_fortune(path)
    dis = {
        0 : "Monocyte",
        1 : "Lymphocyte",
        2 : "Neutrophil",
        3 : "Eosinophil",
    }
    disease = {
        0 : "bacterial, fungal, viral, and protozoal infection.",
        1 : "cancer of the blood or lymphatic system or An autoimmune disorder causing ongoing (chronic) inflammation.",
        2 : "high stress levels or you might be smoking cigarettes or sniffing tobacco. You might even face chronic myeloid leukemia.",
        3 : "Endocrine disorders, Autoimmune disorders, Skin disorders, Parasitic and fungal diseases or Tumors and Toxins.",
    }
    return render_template('result.html', cell = dis[maxi], count = maxi + 2, disease = disease[maxi])

@app.route('/last/')
def last_page():
    path  = "../static/1_1.jpg"
    path1 = "../static/1_2.jpg"
    mask = "../static/mask.jpg"
    return render_template('image_report.html', wbc_image=mask, wbc_image1=path1, wbc_image2=path)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
