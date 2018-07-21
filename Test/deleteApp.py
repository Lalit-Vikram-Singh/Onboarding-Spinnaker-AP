import os
import json
from flask import Flask
from flask_restplus import Resource, fields
#from Lalit.restplus import api_restplus
from flask_restplus import Api
from app.api_1_0.decorators import json_schema_validate
from flask import request
from jinja2 import Template
from app.constants import URL
from app.util import Client
from app.exceptions import BadRequestError


app = Flask(__name__)


api_restplus = Api(version='1.0', title='Spinnaker Provision API', description='Provisioning API Service for Spinnaker')


deleteApplication = api_restplus.namespace('deleteApplication',
                                           description='Delete operation over spinnaker applications', ordered=True)

application = api_restplus.model('Application', {
    'application': fields.String(description='Name of application', required=True, example='deleteabcccc'),
    'description': fields.String(description='Description of current task', required=True,
                                 example='Delete application'),
    'job': fields.List(api_restplus.model('Job', {
        'type': fields.String(description='Type of job', required=True, example='deleteApplication'),
        'application': fields.Nested(api_restplus.model('InnerApplicationObject', {
            'name': fields.String(description='Name of application', required=True, example='deleteabcccc')
        }))
    }))

})


@deleteApplication.route('/applications/<applicationName>/tasks')
class DeleteApplication(Resource):
    ''' Delete application by name '''

    @api_restplus.response(200, 'Application Delete Successfully')
    @api_restplus.response(400, 'Validation Error in Json')
    #@json_schema_validate('application_delete.json')
    @api_restplus.expect(application, validate=True)
    def post(self, applicationName):
        app.logger.info("deleting  application")

        # /home/ipsg/lalit/codebase/Spinnaker-roer/Lalit/model/application_delete.json
        #with open(os.path.join(self.get_json_template_base_dir(), 'application_delete.json')) as template_file:
        #    template = Template(template_file.read())

        with open(os.path.join('/home/ipsg/lalit/codebase/Spinnaker-roer/Lalit/model/', 'application_delete.json')) as template_file:
            template = Template(template_file.read())

        content = request.get_json()


        json_payload = template.render(
            {"name": content['applicationName'], "description": content['description'],
             "job": json.dumps(content['job'])})

        app.logger.info("JSON for deleting application:{}".format(json_payload))

       # url = URL.APPLICATION_CREATE_URL.format(app.config['SPINNAKER_BASE_URL'], content["applicationName"])
       # http: // spinnaker - elb - 514241712.us - west - 2.elb.amazonaws.com: 8084 / applications / lalittestabc / tasks
        spinnakerBaseUrl = 'http://spinnaker-elb-514241712.us-west-2.elb.amazonaws.com:8084/applications/'
        #url = URL.APPLICATION_CREATE_URL.format(app.config['SPINNAKER_BASE_URL'], content["applicationName"])
        url = URL.APPLICATION_CREATE_URL.format(spinnakerBaseUrl, applicationName, '/tasks')

        app.logger.info("Final URL for deleting application:{}".format(url))

        # setting request body content type to json to avoid error
        try:
            response_json = Client().execute_request('post', url, json=json.loads(json_payload))
            return response_json
        except BadRequestError as e:
            app.logger.error("Bad Request Error -> Status:{}\nMsg:{}".format(e.status, e.message))
            return {"error": "Bad Request Error", "msg": str(e.message)}, 500

    def get_json_template_base_dir(self):
        return os.path.join(*[app.config['PAYLOAD_TEMPLATES_BASE_DIR'], 'application', 'payloads'])

if __name__ == '__main__':
    app.run()
