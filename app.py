
#!flask/bin/python
from flask import Flask, jsonify, render_template, redirect
from flask import *
import tasks
import subprocess
import sys
import os
import uuid

app = Flask(__name__)
tasks_store = []

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)


app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

@app.route('/', methods = ['GET'])
def index():
    name = 'Max'
    return render_template('index.html', name=name)

def reduce_finished_tasks(partial_results):
    consolidated = {}
    for result in partial_results:
        for (key,elem) in result.items:
            if key in consolidated:
                consolidated[key] = consolidated['key'] + elem
            else:
                consolidated[key] = elem
    return consolidated

@app.route('/task/<task_id>', methods = ['GET'])
def tasks_results(task_id):
    find_task = [task for task in tasks_store if str(task['id']) == task_id]
    if len(find_task) > 0:
        task = find_task.pop()
        if task['ready'] == None:
            task['ready'] = []
        if task['finished'] == None:
            task['finished'] = []
        task['ready'] = task['ready'].append([aTask for aTask in task['results'] if aTask.ready == True])
        task['results'] = list(set(task['results']) - set(task['ready']))
        task['finished'] = task['finished'].append([aTask.get() for aTask in task['ready']])
        task['count_finished'] = len(task['finished'])
        task['summary'] = reduce_finished_tasks(task['finished'])
        return json.dumps(task)
    else:
        return redirect(url_for(index))
@app.route('/countwords', methods=['GET'])
def countWords():
    bucketURL = 'http://smog.uppmax.uu.se:8080/swift/v1/tweets/'
    words = ['han','hon','den','det','denna','denne','hen']
    files = os.popen('curl {}'.format(bucketURL)).read().rsplit('\n')
    task = {}
    task['id'] = uuid.uuid1()
    task['results'] = [tasks.countMentionInTweetFile.delay(aFile,words) for aFile in files]
    task['count_deployed'] = len(task['results'])
    tasks_store.append(task)

    return redirect(url_for('tasks_results',task_id = str(task['id'])))

if __name__ == '__main__':

    app.run(host='0.0.0.0',debug=True)
