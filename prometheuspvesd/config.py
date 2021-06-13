#!/usr/bin/env python3
"""Global settings definition."""

import os
from pathlib import Path
from pathlib import PurePath

import anyconfig
import environs
import jsonschema.exceptions
import ruamel.yaml
from appdirs import AppDirs
from jsonschema._utils import format_as_index

import prometheuspvesd.exception
from prometheuspvesd.utils import Singleton

config_dir = AppDirs("prometheus-pve-sd").user_config_dir
default_config_file = os.path.join(config_dir, "config.yml")
cache_dir = AppDirs("prometheus-pve-sd").user_cache_dir
default_output_file = os.path.join(cache_dir, "pve.json")


class Config():
    """
    Create an object with all necessary settings.

    Settings are loade from multiple locations in defined order (last wins):
    - default settings defined by `self._get_defaults()`
    - yaml config file, defaults to OS specific user config dir (https://pypi.org/project/appdirs/)
    - provides cli parameters
    """

    SETTINGS = {
        "config_file": {
            "default": "",
            "env": "CONFIG_FILE",
            "type": environs.Env().str
        },
        "logging.level": {
            "default": "WARNING",
            "env": "LOG_LEVEL",
            "file": True,
            "type": environs.Env().str
        },
        "logging.format": {
            "default": "console",
            "env": "LOG_FORMAT",
            "file": True,
            "type": environs.Env().str
        },
        "output_file": {
            "default": default_output_file,
            "env": "OUTPUT_FILE",
            "file": True,
            "type": environs.Env().str
        },
        "loop_delay": {
            "default": 300,
            "env": "LOOP_DELAY",
            "file": True,
            "type": environs.Env().int
        },
        "service": {
            "default": True,
            "env": "SERVICE",
            "file": True,
            "type": environs.Env().bool
        },
        "exclude_state": {
            "default": [],
            "env": "EXCLUDE_STATE",
            "file": True,
            "type": environs.Env().list
        },
        "exclude_vmid": {
            "default": [],
            "env": "EXCLUDE_VMID",
            "file": True,
            "type": environs.Env().list
        },
        "pve.server": {
            "default": "",
            "env": "PVE_SERVER",
            "file": True,
            "type": environs.Env().str
        },
        "pve.user": {
            "default": "",
            "env": "PVE_USER",
            "file": True,
            "type": environs.Env().str
        },
        "pve.password": {
            "default": "",
            "env": "PVE_PASSWORD",
            "file": True,
            "type": environs.Env().str
        },
        "pve.auth_timeout": {
            "default": 5,
            "env": "PVE_AUTH_TIMEOUT",
            "file": True,
            "type": environs.Env().int
        },
        "pve.verify_ssl": {
            "default": True,
            "env": "PVE_VERIFY_SSL",
            "file": True,
            "type": environs.Env().bool
        },
    }

    def __init__(self, args={}):
        """
        Initialize a new settings class.

        :param args: An optional dict of options, arguments and commands from the CLI.
        :param config_file: An optional path to a yaml config file.
        :returns: None

        """
        self._args = args
        self._schema = None
        self.config_file = default_config_file
        self.config = None
        self._set_config()

    def _get_args(self, args):
        cleaned = dict(filter(lambda item: item[1] is not None, args.items()))

        normalized = {}
        for key, value in cleaned.items():
            normalized = self._add_dict_branch(normalized, key.split("."), value)

        # Override correct log level from argparse
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        log_level = levels.index(self.SETTINGS["logging.level"]["default"])
        if normalized.get("logging"):
            for adjustment in normalized["logging"]["level"]:
                log_level = min(len(levels) - 1, max(log_level + adjustment, 0))
            normalized["logging"]["level"] = levels[log_level]

        return normalized

    def _get_defaults(self):
        normalized = {}
        for key, item in self.SETTINGS.items():
            normalized = self._add_dict_branch(normalized, key.split("."), item["default"])

        self.schema = anyconfig.gen_schema(normalized)
        return normalized

    def _get_envs(self):
        normalized = {}
        for key, item in self.SETTINGS.items():
            if item.get("env"):
                prefix = "PROMETHEUS_PVE_SD_"
                envname = prefix + item["env"]
                try:
                    value = item["type"](envname)
                    normalized = self._add_dict_branch(normalized, key.split("."), value)
                except environs.EnvError as e:
                    if '"{}" not set'.format(envname) in str(e):
                        pass
                    else:
                        raise prometheuspvesd.exception.ConfigError(
                            "Unable to read environment variable", str(e)
                        )

        return normalized

    def _set_config(self):
        args = self._get_args(self._args)
        envs = self._get_envs()
        defaults = self._get_defaults()

        # preset config file path
        if envs.get("config_file"):
            self.config_file = self._normalize_path(envs.get("config_file"))

        if args.get("config_file"):
            self.config_file = self._normalize_path(args.get("config_file"))

        source_files = []
        source_files.append(self.config_file)

        for config in source_files:
            if config and os.path.exists(config):
                with open(config, "r", encoding="utf8") as stream:
                    s = stream.read()
                    try:
                        file_dict = ruamel.yaml.safe_load(s)
                    except (
                        ruamel.yaml.composer.ComposerError, ruamel.yaml.scanner.ScannerError
                    ) as e:
                        message = "{} {}".format(e.context, e.problem)
                        raise prometheuspvesd.exception.ConfigError(
                            "Unable to read config file {}".format(config), message
                        )

                    if self._validate(file_dict):
                        anyconfig.merge(defaults, file_dict, ac_merge=anyconfig.MS_DICTS)
                        defaults["logging"]["level"] = defaults["logging"]["level"].upper()

        if self._validate(envs):
            anyconfig.merge(defaults, envs, ac_merge=anyconfig.MS_DICTS)

        if self._validate(args):
            anyconfig.merge(defaults, args, ac_merge=anyconfig.MS_DICTS)

        if "config_file" in defaults:
            defaults.pop("config_file")

        defaults["logging"]["level"] = defaults["logging"]["level"].upper()
        defaults["logging"]["format"] = defaults["logging"]["format"].strip().lower()

        Path(PurePath(self.config_file).parent).mkdir(parents=True, exist_ok=True)
        Path(PurePath(defaults["output_file"]).parent).mkdir(parents=True, exist_ok=True)

        self.config = defaults

    def _normalize_path(self, path):
        if not os.path.isabs(path):
            base = os.path.join(os.getcwd(), path)
            return os.path.abspath(os.path.expanduser(os.path.expandvars(base)))
        else:
            return path

    def _validate(self, config):
        try:
            anyconfig.validate(config, self.schema, ac_schema_safe=False)
        except jsonschema.exceptions.ValidationError as e:
            schema_error = "Failed validating '{validator}' in schema{schema}\n{message}".format(
                validator=e.validator,
                schema=format_as_index(list(e.relative_schema_path)[:-1]),
                message=e.message
            )
            raise prometheuspvesd.exception.ConfigError("Configuration error", schema_error)

        return True

    def _add_dict_branch(self, tree, vector, value):
        key = vector[0]
        tree[key] = value \
            if len(vector) == 1 \
            else self._add_dict_branch(tree[key] if key in tree else {}, vector[1:], value)
        return tree


class SingleConfig(Config, metaclass=Singleton):
    """Singleton config class."""

    pass
