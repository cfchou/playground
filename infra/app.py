#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

from aws_cdk import core as cdk
from stacks.restapi import RestApiStack
from stacks.cicd import CICDStack

from util.config import get_settings

# Load environment dependent settings
# NOTE: You may use env switch. If not specified, whatever in "default" takes
#  effect.
#  > export CF_INFRA_ENV="dev" | "prod"
settings = get_settings()


# Cleanup old assets to reduce disk space
for asset in Path("cdk.out").glob("asset.*"):
    shutil.rmtree(asset)

app = cdk.App()
if app.node.try_get_context('create_cicd'):
    print("#============================")
    print("# Creating CI/CD stack")
    print("#============================")
    CICDStack(
        app,
        f"{settings.prefix}-cicd",
        settings=settings,
        env=cdk.Environment(
            account=settings.cdk_default_account,
            region=settings.cdk_default_region,
        ),
    )
else:
    print("#============================")
    print("# Creating application stack")
    print("#============================")
    # This could be executed locally or by the deployed CI/CD Stack
    RestApiStack(
        app,
        f"{settings.prefix}-restapi",
        settings=settings,
        env=cdk.Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=os.getenv('CDK_DEFAULT_REGION'),
        ),
    )


app.synth()
