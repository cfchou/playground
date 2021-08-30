from typing import Optional

import constructs
from aws_cdk import core as cdk
from aws_cdk.core import Environment
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep

from util.config import ResolvedSettings
from .restapi import RestApiStack


class CICDStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, *,
        settings: ResolvedSettings,
        env: Optional[Environment] = None,
        outdir: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, env=env, **kwargs)

        source = CodePipelineSource.connection(
            repo_string=settings.cicd.repo,
            branch=settings.cicd.branch,
            connection_arn=settings.cicd.connection_arn,
        )
        synth = ShellStep(
            f"{settings.prefix}-step",
            input=source,
            install_commands=[
                "npm install -g aws-cdk",
                "cd infra",
                "pip install pipenv",
                "python3 -m venv /venv",
                "export PATH=/venv/bin:$PATH",
                "export VIRTUAL_ENV=/venv",
                "pipenv install --keep-outdated --ignore-pipfile",
            ],
            commands=["cdk synth"],
            primary_output_directory="infra/cdk.out"
        )

        self.pipeline = CodePipeline(
            self, f"{settings.prefix}-pipeline",
            pipeline_name=f"{settings.prefix}-pipeline",
            synth=synth,
            # NOTE: because RestApiStack uses docker to bundle files
            docker_enabled_for_synth=True,
        )

        self.pipeline.add_stage(
            RestApiStage(
                self,
                f"{settings.prefix}-stage",
                settings=settings,
                env=env,
                outdir=outdir,
            )
        )


class RestApiStage(cdk.Stage):
    def __init__(
        self, scope: constructs.Construct, id: str, *,
        settings: ResolvedSettings,
        env: Optional[Environment] = None,
        outdir: Optional[str] = None
    ) -> None:
        super().__init__(scope, id, env=env, outdir=outdir)
        RestApiStack(
            self,
            f"{settings.prefix}-restapi",
            settings=settings,
            env=env,
        )


