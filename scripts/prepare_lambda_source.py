"""Prepare the source directory used by Terraform's Lambda package step."""

from pathlib import Path
import shutil


# This file lives in scripts/, so parents[1] moves up one level to the project
# root: ai-content-processor/.
ROOT_DIR = Path(__file__).resolve().parents[1]

# Terraform will package this generated folder for Lambda. It should contain
# only the files Lambda needs at runtime, not infra/, .terraform/, git files, or
# other local development files.
BUILD_DIR = ROOT_DIR / "build" / "lambda-src"


def remove_python_artifacts(path: Path) -> None:
    """Remove bytecode artifacts from the generated Lambda source tree."""
    # Python creates __pycache__ directories when files are imported locally.
    # They are generated cache files, so Lambda does not need them.
    for pycache_dir in path.rglob("__pycache__"):
        shutil.rmtree(pycache_dir)

    # .pyc files are compiled Python bytecode. They are also generated cache
    # files, so remove them from the Lambda source folder before packaging.
    for pyc_file in path.rglob("*.pyc"):
        pyc_file.unlink()


def main() -> None:
    # If build/lambda-src already exists from a previous run, delete it first.
    # This prevents old files from staying in the Lambda package after you
    # rename or remove files from app/.
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    # Recreate build/lambda-src. parents=True means Python also creates the
    # parent build/ directory if it does not exist yet, like mkdir -p.
    BUILD_DIR.mkdir(parents=True)

    # Copy app/ into build/lambda-src/app/. Keeping the app/ folder name is what
    # makes this Terraform handler path work:
    # app.workers.sqs_worker.lambda_handler
    shutil.copytree(ROOT_DIR / "app", BUILD_DIR / "app")

    # Copy requirements.txt next to app/. The Terraform Lambda module looks for
    # this file and uses it to install Python dependencies into the Lambda zip.
    shutil.copy2(ROOT_DIR / "requirements.txt", BUILD_DIR / "requirements.txt")

    # Clean out local Python cache files so the generated Lambda package source
    # contains source files and dependency metadata only.
    remove_python_artifacts(BUILD_DIR)


if __name__ == "__main__":
    # This makes the script run when called with:
    # python3 scripts/prepare_lambda_source.py
    main()
