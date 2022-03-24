# WSE
import flask
from flask import request, jsonify

# WSGI
from gevent.pywsgi import WSGIServer

# Logging
import logging
import os
from datetime import datetime

app = flask.Flask(__name__)
#app.config["DEBUG"] = True


# Create some test data for our catalog in the form of a list of dictionaries.
TestResults = [
    {'transaction_id': 'PLSC2105050001',
     'inference_model': 'PLScomment',
     'inference_content': 'PROMIS帳入ERF=8，實物移至Hold Lot Room的”已收費暫放區”存放',
     'inference_file': 'smb://AI_TEMP/LabelInspection/AMD_BOX_0001.jpg',
     'inference_Result': 'Continue',
     'inference_ResultFile': 'smb://AI_TEMP/LabelInspection/Result/AMD_BOX_0001.jpg',
     'inference_ResultConfidence': 99.82
     }
]


@app.route('/', methods=['GET'])
def home():
    # events record
    now = datetime.now()
    daystr = now.strftime("%Y%m%d")
    root = os.path.dirname(os.path.abspath(__file__))
    eventdir = os.path.join(root,'events')
    if not os.path.exists(eventdir):
        os.mkdir(eventdir) 
    event_file = os.path.join(eventdir, 'PLS_cmt_events_'+ daystr +'.log')
    print(event_file)

    return '''<h1>Distant Reading Archive</h1>
<p>NLP API for applications.</p>'''


# A route to return all of the available entries in our catalog.
@app.route('/api/inference/PLScomment/test', methods=['GET'])
def api_all():
    return jsonify(TestResults)

@app.before_first_request
def before_first_request():
    log_level = logging.INFO
    
    now = datetime.now()
    daystr = now.strftime("%Y%m%d")

    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)
    root = os.path.dirname(os.path.abspath(__file__))
    logdir = os.path.join(root, 'logs')
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    log_file = os.path.join(logdir, 'PLS_cmt_server_logs_'+ daystr +'.log')
    handler = logging.FileHandler(log_file)
    handler.setLevel(log_level)
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    defaultFormatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler.setFormatter(defaultFormatter)




#app.run()

# production
http_server = WSGIServer(('',5000),app, log=app.logger)
http_server.serve_forever()
