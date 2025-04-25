"""Module for the Config class."""

from __future__ import annotations

import dataclasses
import typing
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional, get_origin

import yaml

from reflex_cli import constants
from reflex_cli.utils.exceptions import ConfigError, ConfigInvalidFieldValueError

RegionOption = Literal[
    "ams",
    "arn",
    "atl",
    "bog",
    "bom",
    "bos",
    "cdg",
    "den",
    "dfw",
    "ewr",
    "eze",
    "fra",
    "gdl",
    "gig",
    "gru",
    "hkg",
    "iad",
    "jnb",
    "lax",
    "lhr",
    "mad",
    "mia",
    "nrt",
    "ord",
    "otp",
    "phx",
    "qro",
    "scl",
    "sea",
    "sin",
    "sjc",
    "syd",
    "waw",
    "yul",
    "yyz",
]

VmType = Literal[
    "c1m.5",
    "c1m1",
    "c1m2",
    "c2m.5",
    "c2m1",
    "c2m2",
    "c2m4",
    "c4m1",
    "c4m2",
    "c4m4",
    "c4m8",
]


def _validate_type(value: Any, _type: type, key: str = ""):
    if not isinstance(value, _type):
        raise (
            ConfigInvalidFieldValueError(
                f"Invalid value for {key}. Expected a {_type}, got {value} of type {type(value).__name__}."
            )
            if key
            else ConfigInvalidFieldValueError(
                f"Invalid value. Expected a {_type}, got {value} of type {type(value).__name__}."
            )
        )


def _validate_literal(value: Any, key: str = "", valid_values: Sequence[str] = ()):
    _validate_type(value, str, key)
    if value not in valid_values:
        raise (
            ConfigInvalidFieldValueError(
                f"Invalid value for {key}. Expected one of {valid_values}, got {value}."
            )
            if key
            else ConfigInvalidFieldValueError(
                f"Invalid value. Expected one of {valid_values}, got {value}."
            )
        )


def _validate_list(value: Any, item_type: type, key: str = ""):
    _validate_type(value, list, key)
    for item in value:
        _validate_dispatch(item, item_type, key=f"{key} item" if key else "")


def _validate_dict(value: Any, key_type: type, value_type: type, key: str = ""):
    _validate_type(value, dict, key)
    for key, val in value.items():
        _validate_dispatch(key, key_type, key=f"{key} key" if key else "")
        _validate_dispatch(val, value_type, key=f"{key} value" if key else "")


def _validate_optional(value: Any, non_optional_type: type, key: str = ""):
    if value is not None:
        _validate_dispatch(value, non_optional_type, key)


def _validate_dispatch(
    value: Any,
    _type: Any,
    key: str = "",
):
    if _type in [str, int, float, bool]:
        _validate_type(value, _type, key)
    origin = get_origin(_type)
    if origin is typing.Union:
        args = typing.get_args(_type)
        if len(args) == 2 and type(None) in args:
            non_optional_type = next(arg for arg in args if arg is not type(None))
            _validate_optional(value, non_optional_type, key)
        return
    if origin is list:
        item_type = typing.get_args(_type)[0]
        _validate_list(value, item_type, key)
    if origin is typing.Literal:
        _validate_literal(value, key, typing.get_args(_type))
    if origin is dict:
        key_type, value_type = typing.get_args(_type)
        _validate_dict(value, key_type, value_type, key)


@dataclass
class Config:
    """Configuration class for the CLI."""

    name: Optional[str] = dataclasses.field(default=None)  # noqa: UP007
    description: Optional[str] = dataclasses.field(default=None)  # noqa: UP007
    vmtype: Optional[VmType] = dataclasses.field(default=None)  # noqa: UP007
    regions: Optional[dict[RegionOption, int]] = dataclasses.field(default=None)  # noqa: UP007
    hostname: Optional[str] = dataclasses.field(default=None)  # noqa: UP007
    envfile: str = dataclasses.field(default=".env")
    project: Optional[str] = dataclasses.field(default=None)  # noqa: UP007
    packages: list[str] = dataclasses.field(default_factory=list)

    _cloud_yaml_path: Path = dataclasses.field(
        default_factory=lambda: Path.cwd() / constants.Dirs.CLOUD
    )

    def __post_init__(self):
        """Post-initialization validation for the Config class.

        Raises:
            ConfigInvalidFieldValueError: If any field value is invalid.

        # noqa: DAR401

        """
        evaluated_type = typing.get_type_hints(Config)
        for field in dataclasses.fields(self):
            if field.name.startswith("_"):
                continue
            field_type = evaluated_type.get(field.name)
            if field_type is None:
                raise ConfigInvalidFieldValueError(f"Invalid field: {field}")
            try:
                _validate_dispatch(
                    getattr(self, field.name), field_type, key=field.name
                )
            except ValueError as e:
                raise ConfigInvalidFieldValueError(
                    "Invalid cloud.yml. " + str(e)
                ).with_traceback(e.__traceback__) from None

    @classmethod
    def from_yaml(cls, yaml_path: Path = Path.cwd() / constants.Dirs.CLOUD) -> Config:
        """Creates a Config instance from a YAML file.

        Args:
            yaml_path: The path to the YAML file. Defaults to "cloud.yml" in the current directory.

        Returns:
            Config: A Config instance with the values from the YAML file.

        Raises:
            ConfigError: If the YAML file is not found.

        """
        try:
            with yaml_path.open() as file:
                data = yaml.safe_load(file)
            return cls(_cloud_yaml_path=yaml_path, **data)
        except FileNotFoundError as e:
            raise ConfigError(f"Config file not found at {yaml_path}.") from e

    @classmethod
    def from_yaml_or_default(
        cls, yaml_path: Path = Path.cwd() / constants.Dirs.CLOUD
    ) -> Config:
        """Creates a Config instance from a YAML file or returns a default instance.

        Args:
            yaml_path: The path to the YAML file. Defaults to "cloud.yml" in the current directory.

        Returns:
            Config: A Config instance with the values from the YAML file or a default instance.

        """
        try:
            return cls.from_yaml(yaml_path)

        except ConfigError:
            return cls()

    def with_overrides(self, **kwargs: Any) -> Config:
        """Creates a new Config instance with overrides.

        Args:
            **kwargs: Key-value pairs of fields to override. The values take
                      precedence over the existing instance values.

        Returns:
            Config: A new Config instance with updated values.

        """
        return dataclasses.replace(self, **kwargs)

    def exists(self) -> bool:
        """Check if the config file exists.

        Returns:
            bool: True if the config file exists, False otherwise.

        """
        return self._cloud_yaml_path.exists()
