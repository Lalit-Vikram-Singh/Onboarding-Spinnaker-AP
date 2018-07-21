from flask import current_app as app
from .decorators import json_schema_validate
from .restplus import api_restplus
from flask_restplus import Resource, fields
from flask import request
import requests
import json
from jinja2 import Template
import os
from app.constants import URL
from app.util import Client
from app.exceptions import BadRequestError

ns = api_restplus.namespace('applications', description='Operations related to spinnaker applications', ordered=True)

application = api_restplus.model('Application', {
    'applicationName': fields.String(description='Name of application', required=True, example='TestApp'),
    'owner': fields.Nested(api_restplus.model('OwnerData', {
        'name': fields.String(required=True, example='TestUser'),
        'email': fields.String(required=True, example='test@test.com'),
        'groups': fields.Nested(api_restplus.model('GroupData', {
            'read': fields.List(fields.String(example='sra-udeploy-dev')),
            'readWrite': fields.List(fields.String(example='sra-dev-team'))
            # 'read': fields.List(fields.String(example=['readgroup1','readgroup2'])),
            # 'readWrite': fields.List(fields.String(example=['writegroup1','writegroup2']))
        }))
    }))
})


@ns.route('/')
class ApplicationCollections(Resource):
    '''Shows a list of all applications, and lets you POST to add new applications'''

    @api_restplus.response(200, 'Success')
    def get(self):
        app.logger.info("getting application")
        # app.logger.info(self.test_variable)
        return "get application code goes here..Hurray!!!"

    @api_restplus.response(201, 'Application Created Successfully')
    @api_restplus.response(400, 'Validation Error in Json')
    @json_schema_validate('application_create.json')
    @api_restplus.expect(application, validate=True)
    def post(self):
        app.logger.info("creating application")

        with open(os.path.join(self.get_json_template_base_dir(), 'create_application.json')) as template_file:
            template = Template(template_file.read())

        content = request.get_json()

        json_payload = template.render(
            {"name": content['applicationName'], "email": content['owner']['email'],
             "owner_name": content['owner']['name'], "read": json.dumps(content['owner']['groups']['read']),
             "read_write": json.dumps(content['owner']['groups']['readWrite'])})

        app.logger.info("JSON for creating application:{}".format(json_payload))

        # todo log returned status of rest calls
        # todo add exception handling
        # todo check what happens if application with same name is created again..does it override properties
        # todo check if application exists
        # todo construct appropriate response message
        # todo write code to add ad-group of sra-admins
        # app.logger.info("app name: {}".format(content["applicationName"]))
        url = URL.APPLICATION_CREATE_URL.format(app.config['SPINNAKER_BASE_URL'], content["applicationName"])

        app.logger.info("Final URL for creating application:{}".format(url))

        # setting request body content type to json to avoid error
        try:
            response_json = Client().execute_request('post', url, json=json.loads(json_payload))
            return response_json
        except BadRequestError as e:
            app.logger.error("Bad Request Error -> Status:{}\nMsg:{}".format(e.status, e.message))
            return {"error": "Bad Request Error", "msg": str(e.message)}, 500

    def get_json_template_base_dir(self):
        return os.path.join(*[app.config['PAYLOAD_TEMPLATES_BASE_DIR'], 'application', 'payloads'])


@ns.route('/<applicationName>/loadbalancer')
class ApplicationLoadbalancerCollection(Resource):
    def get(self, applicationName):
        app.logger.info("Getting loadbalancers for application:{}".format(applicationName))
        headers = {"Content-Type": "application/json"}

        url = URL.APPLICATION_LOADBALANCER_GET_URL.format(app.config['SPINNAKER_BASE_URL'], applicationName)

        app.logger.info("URL for fetching loadbalancer for application:{}".format(url))

        r = requests.get(url, auth=(app.config['SPINNAKER_USERNAME'], app.config['SPINNAKER_PASSWORD']), verify=False,
                         headers=headers)

        return r.json()
