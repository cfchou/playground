from dynaconf import Dynaconf

# TODO: We like everything to be typed. Upcoming dynaconf 3.1.x will support
#  pydantic.BaseSettings. Until then we use pydantic.BaseModel as a simple
#  container for dynaconf settings and do some naive conversion.
from pydantic import BaseModel

from constant import DEFAULT_ENV, ENVS


class DynaNestedConvertMixin:
    # Mixed to a subclass of BaseModel as a nested setting
    @classmethod
    def create(cls, setting):
        kv = {}
        for f, fv in cls.__fields__.items():
            f_type = fv.type_
            if issubclass(f_type, DynaNestedConvertMixin):
                kv[f] = f_type.create(getattr(setting, f))
            else:
                kv[f] = getattr(setting, f)

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


class ResolvedSettings(BaseModel):
    secrets: Secrets
    current_env: str
    app_name: str
    prefix: str
    restapi: RestApiSetting

    @classmethod
    def create(cls, setting: Dynaconf):
        kv = {}
        for f, fv in cls.__fields__.items():
            f_type = fv.type_
            if issubclass(f_type, DynaNestedConvertMixin):
                if issubclass(f_type, Secrets):
                    env = (
                        DEFAULT_ENV if setting.current_env == 'DEVELOPMENT' else
                        setting.current_env
                    )
                    kv[f] = f_type.create(setting.from_env(env))
                else:
                    kv[f] = f_type.create(getattr(setting, f))
            else:
                kv[f] = getattr(setting, f)

        return cls(**kv)


def get_settings() -> ResolvedSettings:
    # TODO: make ResolvedSettings a singleton
    _setting = Dynaconf(
        environment=True,
        env=DEFAULT_ENV,
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

    return ResolvedSettings.create(_setting)



