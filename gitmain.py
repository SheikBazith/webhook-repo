from multiprocessing import current_process

from bson import json_util
from flask import Flask
from flask import json
from flask import request
from pymongo import MongoClient
from datetime import datetime
from datetime import date
from bson.json_util import loads

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['admin']
coll = db['example']
@app.route('/')
def index():
    x = coll.find_one()
    return json.loads(json_util.dumps(x))

@app.route('/github', methods = ['POST']) #routing all the events into /github URL
def api_gh_msg():
    data = request.json # requesting the redirection of github process into json format

    filename = 'numbers.json'  # use the file extension .json
    with open(filename, 'w') as file_object:
        my_info = json.dump(request.json, file_object)
    if request.headers['Content-Type'] == 'application/json' and 'action' in data or 'pusher' in data: # if the redirected values is in json format
                                                                                                       # and json files contains action and pusher label which
                                                                                                       # indicates that pull and push request has occured respectively
                                                                                                       #then it will go inside the if statement
        today = date.today()
        now = datetime.now()
        current_date = today.strftime("%b-%d-%Y")
        current_time = now.strftime("%H:%M:%S")

        if 'action' in data:# if action label exists in json file then it means pull request has been performed
            author = data['sender']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            # timestamp = data['pull_request']['updated_at']
            if data['action'] == 'opened':# if action is opened it means pull request
                print(author+" submitted a pull request from "+ from_branch +" to "+ to_branch +" on " +current_date+ " at " + current_time)
                pull = {"author": author,"action": "pull",  "from_branch": from_branch, "to_branch": to_branch, "date": current_date,
                         "time": current_time}
                coll.insert_one(pull)
            elif data['action'] == 'closed' and data['pull_request']['merged'] is True:# if action is closed it means merging process has been performed
                print(author+" submitted a merge request from "+ from_branch +" to "+ to_branch +" on " +current_date+ " at " + current_time)
                merge = {"author": author,"action": "merge",  "from_branch": from_branch, "to_branch": to_branch,"date": current_date, "time": current_time}
                coll.insert_one(merge)
        elif 'pusher' in data and len(data['commits'][0]['added']) > 0 and 'commits' in data:# if pusher exists and commits more than 1 file to be pushed then it means push action is performed
            author = data['pusher']['name']
            result = data['ref']
            push_branch = result.rsplit('/', 1)[1]
            print(author + " pushed files to " + push_branch+ " branch on " + current_date + " at " + current_time)
            push = {"author": author,"action": "push", "from_branch": push_branch, "date": current_date,
                    "time": current_time}
            coll.insert_one(push)

    return data

if __name__ == "__main__":
    app.run(debug=True)