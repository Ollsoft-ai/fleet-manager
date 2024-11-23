from flask import render_template, request, redirect, url_for, session, current_app
from . import main

@main.route('/')
def index():
    return render_template('index.html')

#@main.app_context_processor
#def inject_conf_var():
#    return dict(
#        current_app.config['LANGUAGES'],
#    )
