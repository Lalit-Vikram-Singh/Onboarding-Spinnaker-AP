from flask import current_app as app
from .restplus import api_restplus
from flask_restplus import Resource, fields
from app.constants import URL
from app.util import Client
from app.exceptions import BadRequestError

deletePipeline = api_restplus.namespace('deletePipeline',
                                        description='Delete operation over spinnaker applications pipeline',
                                        ordered=True)


@deletePipeline.route('/pipelines/<applicationName>/<pipelineName>')
class DeletePipeline(Resource):
    ''' Delete Pipeline by name '''

    @api_restplus.response(200, 'Pipeline Deleted Successfully')
    def delete(self, applicationName, pipelineName):
        app.logger.info("deleting  pipeline")

        url = URL.APPLICATION_CREATE_URL.format(app.config['SPINNAKER_BASE_URL'], '/pipelines/', applicationName, '/',
                                                pipelineName)
        app.logger.info("Final URL for deleting pipeline:{}".format(url))

        # setting request body content type to json to avoid error
        try:
            response_json = Client().execute_request('delete', url)
            return response_json
        except BadRequestError as e:
            app.logger.error("Bad Request Error -> Status:{}\nMsg:{}".format(e.status, e.message))
            return {"error": "Bad Request Error", "msg": str(e.message)}, 500


