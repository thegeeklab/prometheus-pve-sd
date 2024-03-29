#!/usr/bin/env python3
"""Custom exceptions."""


class PrometheusSDError(Exception):
    """Generic exception class for Prometheus-pve-sd."""

    def __init__(self, msg, original_exception=""):
        super().__init__(f"{msg}\n{original_exception}")
        self.original_exception = original_exception


class APIError(PrometheusSDError):
    """Errors related to API connections."""

    pass


class ConfigError(PrometheusSDError):
    """Errors related to config file handling."""

    pass
