from flask import Flask, request
import requests
import json

app = Flask(__name__)

genralDeleteURL = 'http://spinnaker-elb-514241712.us-west-2.elb.amazonaws.com:8084/applications/{}/tasks'

@app.route('/deleteobject/<applicationName>/', methods=['POST'])
def deleteApp(self, applicationName):
    ''' Delete Deployment Object by name '''
    if request.method == 'POST':
        requestBody = request.data
        headers = {'content-type': 'application/json'}
        print('request Body' + requestBody)
        url = genralDeleteURL.format(applicationName)
        res = requests.post(url, data=requestBody, headers=headers);
        json_data = json.loads(res.text)
        print('responce obj {}'.format(res.status_code))
        return '{}'.format(res.status_code)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)
