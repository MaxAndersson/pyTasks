
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
results_store = []

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
        for (key,elem) in result.items():
            if key in consolidated:
                consolidated[key] = consolidated[key] + elem
            else:
                consolidated[key] = elem
    return consolidated

@app.route('/task/<task_id>', methods = ['GET'])
def tasks_results(task_id):
    find_task = [task for task in tasks_store if str(task['id']) == task_id]
    if len(find_task) > 0:
        task = find_task.pop()
        ready = [aTask for aTask in task['results'] if aTask.ready() == True]
        results = [aTask.get() for aTask in ready]
        summary = reduce_finished_tasks(results)

        return json.dumps(dict(
        id=task['id'],
        count_deployed=task['count_deployed'],
        count_finished=len(results),
        summary=summary,
        task_ids     = [aTask.__str__() for aTask in ready]
        ))
    else:
        return redirect(url_for('index'))
@app.route('/countwords', methods=['GET'])
def countWords():
    bucketURL = 'http://smog.uppmax.uu.se:8080/swift/v1/tweets/'
    words = ['han','hon','den','det','denna','denne','hen']
    files = os.popen('curl {}'.format(bucketURL)).read().rsplit('\n')
    task = {}
    task['id'] = uuid.uuid1()
    #task['results'] = [tasks.countMentionInTweetFile.delay(aFile,words) for aFile in files]
    task['results'] = [tasks.countMentionInTweetFile.delay('tweets_19.txt',words),tasks.countMentionInTweetFile.delay('tweets_19.txt',words)]
    task['count_deployed'] = len(task['results'])
    tasks_store.append(task)
    print task
    return redirect(url_for('tasks_results',task_id = str(task['id'])))

if __name__ == '__main__':

    app.run(host='0.0.0.0',debug=True)
