"""Default package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("prometheus-pve-sd")
except PackageNotFoundError:
    __version__ = "0.0.0"
