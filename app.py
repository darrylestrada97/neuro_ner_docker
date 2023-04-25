from flask import Flask, render_template, request, Response, jsonify, g
import os
from pharmaconer_runner import PharmaCoNERRunner
import sqlite3
import json
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
LOG = False
SERVER = True
app.config['BASIC_AUTH_USERNAME'] = 'plantl'
app.config['BASIC_AUTH_PASSWORD'] = 'plantl'
app.config['JSON_AS_ASCII'] = False
basic_auth = BasicAuth(app)


def convert_json(blob):
    """Currently, we are storing data logs by dumping JSON blobs into SQLite. Whether to create a proper SQL hierarchy,
    or use a NoSQL database (like shelve or Mongo) is TBD/TODO/WIP
    https://chrisostrouchov.com/post/python_sqlite/"""
    return json.loads(blob.decode())


def adapt_json(data):
    return (json.dumps(data, sort_keys=True)).encode()


sqlite3.register_adapter(dict, adapt_json)
sqlite3.register_adapter(list, adapt_json)
sqlite3.register_adapter(tuple, adapt_json)
sqlite3.register_converter('JSON', convert_json)

pharmaCoNERRunner = ''
db_path = ''


def start(server=SERVER):
    """Initialize config"""
    global pharmaCoNERRunner
    global db_path
    # PharmaCoNER and db config
    if server:
        pharmaconer_path = '/app/PharmaCoNER-Tagger'
        output_path = '/app/demos_output'
        parameters_path = '/app/pharmaconer_deploy_parameters.ini'
        db_path = '/app/logs.db'
    else:
        pharmaconer_path = '/home/jordiae/Documents/PharmacoNERTask/FarmacoNER/src/CustomNeuroNER/'
        output_path = '/home/jordiae/Documents/PharmacoNERTask/FarmacoNER/task/deploy_test_output2'
        parameters_path = '/home/jordiae/PycharmProjects/PharmaCoNERDemoBackend/pharmaconer_deploy_parameters.ini'
        db_path = '/home/jordiae/PycharmProjects/PharmaCoNERDemoBackend/logs.db'
    pharmaCoNERRunner = PharmaCoNERRunner(pharmaconer_path, output_path, parameters_path)
    # Database
    if LOG and not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE queries (timestamp INTEGER, message TEXT, success INTEGER, data JSON, \
                    PRIMARY KEY (timestamp));")
        conn.commit()
        conn.close()


start()


def get_db():
    """Helper to get database"""
    db = getattr(g, '_db_path', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Helper to close database"""
    db = getattr(g, 'db_path', None)
    if db is not None:
        db.close()


@app.route('/api/submit', methods=['POST'])
def api_submit():

    """Submit form with text to tag, returns JSON"""
    result = request.json
    #pharmaCoNERRunner.update_model(result['model'])
    output = pharmaCoNERRunner.run(result['inputText'])
    if LOG:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        int_success = '1' if output['success'] else '0'
        sql_command = "INSERT INTO queries (timestamp, message, success, data) VALUES(" + str(int(output['timestamp']))\
                      + ',"' + output['message'] + '", ' + int_success + ", '" + json.dumps(output['data']) + "');"
        cur.execute(sql_command)
        conn.commit()
        conn.close()
    return jsonify(success=output['success'], data=output['data'], message=output['message'])


@app.route('/api/list', methods=['GET'])
@basic_auth.required
def api_list():
    """List all non-error queries"""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT data FROM queries WHERE success=1")
        rows = cur.fetchall()
        conn.close()
        processed_rows = []
        for row in rows:
            processed_rows.append(json.loads(row[0]))
        return jsonify(success=True, data=processed_rows, message='Data retrieved successfully.')
    except BaseException as error:
        return jsonify(success=False, data=[], message='Error: ' + str(error))



'''
@app.route('/submit', methods=['POST'])
def submit():
    """Submit form with text to tag"""
    result = request.form
    output = pharmaCoNERRunner.run(result['inputText'])
    plain_text_res = str(output)
    return Response(plain_text_res, mimetype='text/utf-8')


@app.route('/')
def form():
    """Home page, form"""
    return render_template('form.html')
'''

if __name__ == '__main__':
    app.run()
