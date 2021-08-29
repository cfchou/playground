#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

from aws_cdk import core as cdk
from stacks.restapi import RestApiStack

from config import get_settings

# Load environment dependent settings
# NOTE: You may use env switch. If not specified, whatever in "default" takes
#  effect.
#  > export CF_INFRA_ENV="dev" | "prod"
settings = get_settings()


# Cleanup old assets to reduce disk space
for asset in Path("cdk.out").glob("asset.*"):
    shutil.rmtree(asset)

app = cdk.App()
RestApiStack(
    app,
    f"{settings.prefix}-restapi",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    settings=settings,
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION'),
    ),
    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    # env=core.Environment(account='123456789012', region='us-east-1'),
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

app.synth()
