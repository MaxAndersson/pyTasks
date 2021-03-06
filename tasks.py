import urllib2
import json
import os.path
from celery import Celery

app = Celery('tasks', backend='amqp', broker='amqp://')

def downloadFile(name):
    url = "http://smog.uppmax.uu.se:8080/swift/v1/tweets/{}".format(name)

    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()
    return file_name
def getFile(aFile):
    if os.path.isfile(aFile):
        return aFile
    else:
        return downloadFile(aFile)

@app.task
def aTask():
    return 'aTask'

@app.task
def countMentionInTweetFile(aFile,words):
    searchwords = [[word, 0] for word in words]
    file_name = getFile(aFile)
    with open(file_name,'r') as lines:
        for line in lines:
            if line != '\n':
                tweet = json.loads(line)
                if tweet['text'][:2] != 'RT':
                    #print tweet['text']
                    for word in searchwords:
                        word[1] = word[1] + tweet['text'].count(word[0])
    return dict(searchwords)
