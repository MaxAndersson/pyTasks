
#!flask/bin/python
from flask import Flask, jsonify, render_template
import tasks
import subprocess
import sys

app = Flask(__name__)

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

@app.route('/', methods = ['GET'])
def index():
    name = 'Max'
    return render_template('index.html', name=name)


@app.route('/countwords', methods=['GET'])
def countWords():
    aFile = 'tweets_19.txt'
    words = ['han','hon','den','det','denna','denne','hen']
    return tasks.countMentionInTweetFile(aFile,words)

if __name__ == '__main__':

    app.run(host='0.0.0.0',debug=True)
