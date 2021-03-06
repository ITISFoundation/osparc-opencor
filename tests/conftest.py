# pylint:disable=wildcard-import
# pylint:disable=unused-import
# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

import sys
from pathlib import Path

import pytest
import docker
import yaml
import os

@pytest.fixture(scope='session')
def here() -> Path:
    return Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent

@pytest.fixture(scope='session')
def repo_dir(here: Path) -> Path:
    _repo_dir = here.parent
    assert _repo_dir.exists()
    assert _repo_dir.glob(".git")
    return _repo_dir

@pytest.fixture(scope='session')
def tests_dir(here: Path) -> Path:
    tests_dir = here
    assert tests_dir.exists()
    return tests_dir

@pytest.fixture(scope='session')
def validation_dir(project_slug_dir: Path) -> Path:
    validation_dir = project_slug_dir / "validation"
    assert validation_dir.exists()
    return validation_dir

@pytest.fixture(scope='session')
def project_slug_dir(tests_dir: Path) -> Path:
    project_slug_dir = tests_dir.parent
    assert project_slug_dir.exists()
    return project_slug_dir

@pytest.fixture(scope='session')
def src_dir(project_slug_dir: Path) -> Path:
    src_dir = project_slug_dir / "src"
    assert src_dir.exists()
    return src_dir

@pytest.fixture(scope='session')
def tools_dir(project_slug_dir: Path) -> Path:
    tools_dir = project_slug_dir / "tools"
    assert tools_dir.exists()
    return tools_dir

@pytest.fixture(scope='session')
def docker_dir(project_slug_dir: Path) -> Path:
    docker_dir = project_slug_dir / "docker"
    assert docker_dir.exists()
    return docker_dir

@pytest.fixture(scope='session')
def package_dir(src_dir: Path) -> Path:
    return src_dir / "osparc-opencor"

@pytest.fixture(scope='session')
def git_root_dir(here: Path) -> Path:
    # find where .git
    root_dir = here
    while root_dir.as_posix() != "/" and not Path(root_dir / ".git").exists():
        root_dir = root_dir.parent
    if root_dir.as_posix() == "/":
        return None
    return root_dir


@pytest.fixture(scope='session')
def docker_compose_dict(repo_dir):
    with open(repo_dir / "docker-compose.yml") as fh:
        content = yaml.safe_load(fh)

    # TODO: replace all variables
    return content

@pytest.fixture
def docker_client() -> docker.DockerClient:
    return docker.from_env()

@pytest.fixture
def docker_image_key(docker_client: docker.DockerClient, docker_compose_dict) -> str:
    # FIXME: needs to run from make and interpolate properly substitution syntax!!
    image_key = docker_compose_dict['services']['osparc-opencor']['image'] # FIXME: need to interpolate
    image_key = image_key.replace("$", "")
    image_key = image_key.format(**os.environ)
    print("Testing " + image_key)
    docker_images = [image for image in docker_client.images.list() if any(image_key in tag for tag in image.tags)]
    return docker_images[0].tags[0]