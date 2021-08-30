from pathlib import Path

DEFAULT_ENV = "dev"
ENVS = ["dev", "prod"]

PROJECT_DIR = Path(__file__).parent.parent.parent.absolute()
STAGING_DIR = PROJECT_DIR / "staging"

RUNTIME_DIR = PROJECT_DIR / "runtime"

RUNTIME_STAGING_DIR = STAGING_DIR / "runtime"
LAYER_STAGING_DIR = STAGING_DIR / "layer"
