"""Test Config class."""

from typing import Any

import pytest
import ruamel.yaml
from pytest_mock import MockerFixture

import prometheuspvesd.exception
from prometheuspvesd.config import Config

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


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
