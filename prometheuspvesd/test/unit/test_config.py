"""Test Config class."""

import os
from typing import Any

import pytest
import ruamel.yaml
from pytest_mock import MockerFixture

import prometheuspvesd.exception
from prometheuspvesd.config import Config

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


@pytest.fixture(autouse=True)
def _no_filesystem_side_effects(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.mkdir")


def test_yaml_config(mocker: MockerFixture, defaults: dict[str, Any]) -> None:
    mocker.patch(
        "prometheuspvesd.config.default_config_file", "./prometheuspvesd/test/data/config.yaml"
    )
    config = Config()

    defaults["pve"]["user"] = "root"
    defaults["pve"]["password"] = "secure"
    defaults["pve"]["server"] = "proxmox.example.com"
    defaults["pve"]["token_name"] = "pve_sd"
    defaults["pve"]["token_value"] = "01234567-89ab-cdef-0123-456789abcdef"

    assert config.config == defaults


def test_yaml_config_error(mocker: MockerFixture) -> None:
    mocker.patch(
        "prometheuspvesd.config.default_config_file", "./prometheuspvesd/test/data/config.yaml"
    )
    mocker.patch.object(ruamel.yaml.YAML, "load", side_effect=ruamel.yaml.composer.ComposerError)

    with pytest.raises(prometheuspvesd.exception.ConfigError) as e:
        Config()

    assert "Unable to read config file ./prometheuspvesd/test/data/config.yaml" in str(e.value)


def test_get_envs_skips_unset_variables() -> None:
    config = Config(args={})

    assert config._get_envs() == {}


def test_get_envs_reads_set_variables(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {"PROMETHEUS_PVE_SD_METRICS_PORT": "9999"})
    config = Config(args={})

    assert config._get_envs() == {"metrics": {"port": 9999}}


def test_get_envs_reads_list_variables(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {"PROMETHEUS_PVE_SD_EXCLUDE_VMID": "100,101"})
    config = Config(args={})

    assert config._get_envs() == {"exclude_vmid": ["100", "101"]}


def test_get_envs_invalid_variable_raises(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {"PROMETHEUS_PVE_SD_METRICS_PORT": "not-an-int"})

    with pytest.raises(prometheuspvesd.exception.ConfigError):
        Config(args={})


def test_validate_error_uses_json_path() -> None:
    config = Config(args={})

    with pytest.raises(prometheuspvesd.exception.ConfigError) as e:
        config._validate({"metrics": {"port": "not-an-int"}})

    assert "Failed validating 'type' in schema $.metrics.port" in str(e.value)
