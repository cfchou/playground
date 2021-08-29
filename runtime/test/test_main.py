import json
import sys
from http import HTTPStatus
from pathlib import Path
from string import Template


# pytest can't auto-discover main which is not a package. Manually make it
# discoverable.
APP_DIR = Path(__file__).parent.parent.absolute()
if APP_DIR not in sys.path:
    sys.path.insert(0, str(APP_DIR))
    from main import app
else:
    from main import app

# NOTE: Not a full-ledged ApiGatewayProxyEvent. Only essential fields that
#  handlers need.
test_event = Template(
    """
{
  "path": "$path",
  "httpMethod": "$method",
  "headers": {
    "x-api-key": "N1FJqKmufg2ammusFO5Q3Ase036MKEu4OXCppYa4"
  }
}
"""
)


def test_get_root():
    event = json.loads(test_event.substitute(path="/", method="GET"))
    resp = app(event, context={})
    assert resp == {
        'statusCode': HTTPStatus.OK,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"message": "Hello from /"}',
        'isBase64Encoded': False,
    }


def test_get_users_single_page():
    event = json.loads(test_event.substitute(path="/users", method="GET"))
    resp = app(event, context={})
    assert resp == {
        'statusCode': HTTPStatus.OK,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"data": [{"uid": "1d5f8ffd-202c-4118-8adc-6ad8e742453b", '
        '"created_at": "2021-08-20T08:45:00", '
        '"name": "cfchou", "email": "cfchou@gmail.com"}], '
        '"cursor": null}',
        'isBase64Encoded': False,
    }


def test_get_user_404():
    uid = '1d5f8ffd-202c-4118-8adc-6ad8e742453b'
    event = json.loads(
        test_event.substitute(path=f"/users/{uid}", method="GET")
    )
    resp = app(event, context={})
    assert resp == {
        'statusCode': HTTPStatus.NOT_FOUND,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"statusCode":404,"message":"User '
        '1d5f8ffd-202c-4118-8adc-6ad8e742453b not found"}',
        'isBase64Encoded': False,
    }
