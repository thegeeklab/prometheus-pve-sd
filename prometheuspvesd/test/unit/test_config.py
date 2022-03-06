"""Test Config class."""
import pytest
import ruamel.yaml

import prometheuspvesd.exception
from prometheuspvesd.config import Config

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


def test_yaml_config(mocker, defaults):
    mocker.patch(
        "prometheuspvesd.config.default_config_file", "./prometheuspvesd/test/data/config.yml"
    )
    config = Config()

    defaults["pve"]["user"] = "root"
    defaults["pve"]["password"] = "secure"
    defaults["pve"]["server"] = "proxmox.example.com"

    assert config.config == defaults


def test_yaml_config_error(mocker, capsys):
    mocker.patch(
        "prometheuspvesd.config.default_config_file", "./prometheuspvesd/test/data/config.yml"
    )
    mocker.patch.object(ruamel.yaml.YAML, "load", side_effect=ruamel.yaml.composer.ComposerError)

    with pytest.raises(prometheuspvesd.exception.ConfigError) as e:
        Config()

    assert "Unable to read config file ./prometheuspvesd/test/data/config.yml" in str(e.value)
