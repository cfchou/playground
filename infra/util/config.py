import os
from typing import Optional

from dynaconf import Dynaconf

# TODO: We like everything to be typed. Upcoming dynaconf 3.1.x will support
#  pydantic.BaseSettings. Until then we use pydantic.BaseModel as a simple
#  container for dynaconf settings and do some naive conversion.
from pydantic import BaseModel, Field

from .constant import DEFAULT_ENV, ENVS


__NOTSET__ = object()

class DynaNestedConvertMixin:
    # Mixed to a subclass of BaseModel as a nested setting
    @classmethod
    def create(cls, setting):
        kv = {}
        for f, fv in cls.__fields__.items():
            f_type = fv.type_
            v = getattr(setting, f, __NOTSET__)
            if v == __NOTSET__:
                continue
            if issubclass(f_type, DynaNestedConvertMixin):
                kv[f] = f_type.create(v)
            else:
                kv[f] = v

        return cls(**kv)


class DBSetting(BaseModel, DynaNestedConvertMixin):
    dsn: str


class Secrets(BaseModel, DynaNestedConvertMixin):
    client_id: str
    client_secret: str
    db: DBSetting


class ThrottleSetting(BaseModel, DynaNestedConvertMixin):
    rate: int
    burst: int


class RestApiSetting(BaseModel, DynaNestedConvertMixin):
    throttle: ThrottleSetting


class CICDSetting(BaseModel, DynaNestedConvertMixin):
    connection_arn: str  # connection arn
    repo: str
    branch: str


class ResolvedSettings(BaseModel):
    # TODO: secret should be mandatory
    secrets: Optional[Secrets]
    current_env: str
    app_name: str
    prefix: str
    restapi: RestApiSetting
    cicd: CICDSetting
    cdk_default_account: Optional[str] = Field(
        default_factory=lambda: os.environ.get("CDK_DEFAULT_ACCOUNT")
    )
    cdk_default_region: Optional[str] = Field(
        default_factory=lambda: os.environ.get("CDK_DEFAULT_REGION")
    )

    @classmethod
    def create(cls, setting: Dynaconf):
        kv = {}
        for f, fv in cls.__fields__.items():
            f_type = fv.type_
            if issubclass(f_type, DynaNestedConvertMixin):
                if issubclass(f_type, Secrets):
                    # NOTE: it seems that current_env's secret isn't
                    #  automatically selected.
                    env = (
                        # NOTE: 'DEVELOPMENT' is used by dynaconf internally
                        #  if no env specified
                        DEFAULT_ENV if setting.current_env == 'DEVELOPMENT' else
                        setting.current_env
                    )
                    kv[f] = f_type.create(setting.from_env(env))
                else:
                    v = getattr(setting, f, __NOTSET__)
                    if v != __NOTSET__:
                        kv[f] = f_type.create(v)
            else:
                v = getattr(setting, f, __NOTSET__)
                if v != __NOTSET__:
                    kv[f] = v

        return cls(**kv)


def get_settings(env=DEFAULT_ENV) -> ResolvedSettings:
    # TODO: make ResolvedSettings a singleton
    _setting = Dynaconf(
        environment=True,
        env=env,
        # env can be overwritten:
        #  > export CF_INFRA_ENV="dev" | "prod"
        env_switcher="CF_INFRA_ENV",

        # NOTE: Settings can be overwritten in env var prefixed by "CF_INFRA_".
        #  For example, for Dynaconf.prefix
        #  > export CF_INFRA_PREFIX="test-app"
        envvar_prefix="CF_INFRA",

        # NOTE: `settings_files` = Load this files in the order.
        settings_files=['settings.toml', '.secrets.toml'],
        load_dotenv=True,
    )

    if _setting.current_env not in ENVS:
        raise AssertionError(f"{_setting.current_env=} not supported")
    resolved = ResolvedSettings.create(_setting)

    #if resolved.cdk_default_account is None:
    #    resolved.cdk_default_account = os.environ.get("CDK_DEFAULT_ACCOUNT")
    #if resolved.cdk_default_region is None:
    #    resolved.cdk_default_account = os.environ.get("CDK_DEFAULT_ACCOUNT")

    return resolved



