import json
import uuid
from datetime import datetime
from http import HTTPStatus

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import (
    ApiGatewayResolver,
    content_types,
)
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.event_handler.exceptions import (
    InternalServerError,
    NotFoundError,
    ServiceError,
)
from aws_lambda_powertools.logging import correlation_paths
from model.user import User
from model.response import PagedResponse


logger = Logger()
tracer = Tracer()
metrics = Metrics()

# TODO: group routing in packages of different products or resource groups
app = ApiGatewayResolver()


@metrics.log_metrics
@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST
)
@tracer.capture_lambda_handler
def handler(event, context):
    """
    Args:
        event: API Gateway Lambda Proxy Input Format
            https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format  # noqa
        context: Lambda Context runtime methods and attributes
            https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html  # noqa

    Returns: API Gateway Lambda Proxy Output Format
            https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html  # noqa
    """
    return app.resolve(event, context)


@app.get("/")
@tracer.capture_method
def get_root():
    logger.info("======================")
    logger.info(app.current_event.headers)
    logger.info(app.current_event.query_string_parameters)
    logger.info("======================")
    return Response(
        status_code=HTTPStatus.OK,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({"message": f"Hello from {app.current_event.path}"}),
    )


@app.get("/users")
@tracer.capture_method
def get_users():
    # TODO: fine-grained error handling
    try:
        logger.info("======================")
        logger.info(app.current_event.headers)
        logger.info(app.current_event.query_string_parameters)
        logger.info("======================")
        users = [
            User(
                uid=uuid.UUID('1d5f8ffd-202c-4118-8adc-6ad8e742453b'),
                created_at=datetime.fromisoformat('2021-08-20T08:45'),
                name="cfchou",
                email="cfchou@gmail.com",
            ),
        ]
        resp = PagedResponse(data=users)
        return Response(
            status_code=HTTPStatus.OK,
            content_type=content_types.APPLICATION_JSON,
            body=resp.json(),
        )
    except ServiceError as e:
        raise e
    except Exception as e:
        raise InternalServerError(str(e))


@app.get("/users/<uid>")
@tracer.capture_method
def get_check(uid: str):
    # TODO: fine-grained error handling
    try:
        logger.info("======================")
        logger.info(app.current_event.headers)
        logger.info(app.current_event.query_string_parameters)
        logger.info("======================")
        # TEST ==============
        raise NotFoundError(f"User {uid} not found")
    except ServiceError as e:
        raise e
    except Exception as e:
        raise InternalServerError(str(e))


@app.get("/login")
@tracer.capture_method
def get_actions():
    # TODO: fine-grained error handling
    try:
        logger.info("======================")
        logger.info(app.current_event.headers)
        logger.info(app.current_event.query_string_parameters)
        logger.info("======================")
        resp = PagedResponse(data=[])
        return Response(
            status_code=HTTPStatus.OK,
            content_type=content_types.APPLICATION_JSON,
            body=resp.json(),
        )
    except ServiceError as e:
        raise e
    except Exception as e:
        raise InternalServerError(str(e))
