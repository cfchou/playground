import shutil

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    core as cdk,
)
from aws_cdk.aws_apigateway import (
    ApiKeySourceType,
    ThrottleSettings,
    ThrottlingPerMethod,
)
from aws_cdk.aws_lambda_python import PythonFunction, PythonLayerVersion

from util.config import ResolvedSettings
from util.constant import (
    RUNTIME_DIR,
    RUNTIME_STAGING_DIR,
    LAYER_STAGING_DIR,
    STAGING_DIR,
)


class RestApiStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, *,
        settings: ResolvedSettings, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # clean up previous staged files
        if STAGING_DIR.exists():
            shutil.rmtree(STAGING_DIR)

        # copy files to staging
        ignore = shutil.ignore_patterns(
            "Pipfile*", "requirements.txt", "poetry.lock", ".venv", ".idea"
        )
        shutil.copytree(RUNTIME_DIR, RUNTIME_STAGING_DIR, ignore=ignore)
        LAYER_STAGING_DIR.mkdir()
        deps = [
            RUNTIME_DIR / "Pipfile",
            RUNTIME_DIR / "poetry.lock",
            RUNTIME_DIR / "requirements.text",
        ]
        for d in deps:
            if d.exists():
                shutil.copy(d, LAYER_STAGING_DIR)

        layer = PythonLayerVersion(
            self,
            f'{settings.prefix}-restapi-layer',
            entry=str(LAYER_STAGING_DIR),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
            layer_version_name=f'{settings.prefix}-restapi-layer',
        )
        self.app = PythonFunction(
            self,
            f"{settings.prefix}-restapi-handler",
            entry=str(RUNTIME_STAGING_DIR),
            handler='handler',
            index='main.py',
            runtime=lambda_.Runtime.PYTHON_3_8,
            layers=[layer],
        )

        # Lambda-Proxy
        # https://medium.com/@lakshmanLD/lambda-proxy-vs-lambda-integration-in-aws-api-gateway-3a9397af0e6d  # noqa
        api = apigateway.LambdaRestApi(
            self,
            f"{settings.prefix}-restapi-gateway",
            handler=self.app,
            proxy=False,
            api_key_source_type=ApiKeySourceType.HEADER,
        )

        # Method + Resource
        # GET /users
        users = api.root.add_resource("users")
        users_get = users.add_method("GET", api_key_required=True)
        # GET /login
        login = api.root.add_resource("login")
        login_get = login.add_method("GET", api_key_required=True)

        plan = api.add_usage_plan(
            "UserPlanLight",
            name=f"{settings.prefix}-restapi-light",
            # api_stages=[api.deployment_stage],  # latest deployment
            # NOTE: This is a cap for ThrottlingPerMethod
            throttle=ThrottleSettings(
                burst_limit=settings.restapi.throttle.burst,
                rate_limit=settings.restapi.throttle.rate),
        )
        # plan.add_api_key(ApiKey(self, 'ApiKey'))
        method_throttle = [
            ThrottlingPerMethod(
                method=users_get,
                throttle=ThrottleSettings(burst_limit=20, rate_limit=10),
            ),
            ThrottlingPerMethod(
                method=login_get,
                throttle=ThrottleSettings(burst_limit=2, rate_limit=1),
            ),
        ]
        plan.add_api_stage(
            stage=api.deployment_stage, throttle=method_throttle
        )
        self.api = api
