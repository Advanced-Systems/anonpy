#!/usr/bin/env python3

from configparser import ConfigParser
from pathlib import Path
from types import TracebackType
from typing import Any, Dict, List, Optional, Self, Type, Union

from ..internals.utils import convert


class ConfigHandler:
    def __init__(
            self: Self,
            path: Optional[Union[str, Path]]=None,
            defaults: Dict=None,
            encoding: str="utf-8",
        ) -> None:
        self.path = Path(path) if path is not None else None
        self.encoding = encoding
        self.__config = ConfigParser(defaults=defaults)
        self__file_obj = None

    def __enter__(self: Self) -> Self:
        self.read()
        self.__file_obj = open(self.path, mode="w", encoding=self.encoding)
        return self

    def __exit__(
            self: Self,
            type: Optional[Type[BaseException]],
            value: Optional[BaseException],
            traceback: Optional[TracebackType]
        ) -> bool:
        self.__config.write(self.__file_obj)
        self.__file_obj.close()

    def __str__(self) -> str:
        return str(self.json)

    #region Methods

    def save(self: Self) -> None:
        """
        Save the configuration file.

        NOTE: This method will overwrite the content of the previous configuration
        file if it already existed.
        """
        with open(self.path, mode="w", encoding=self.encoding) as file_handler:
            self.__config.write(file_handler)

    def read(self: Self) -> None:
        """
        Deserialize the configuration file.
        """
        if self.path.exists():
            self.__config.read(self.path, encoding=self.encoding)

    def add_section(self: Self, section: str, settings: Optional[Dict]=None) -> None:
        """
        Create a new section in the configuration.
        """
        if settings is None:
            self.__config.add_section(section)
        else:
            self.__config[section] = {k: str(v) for k,v in settings.items()}

    def remove_section(self: Self, section: str) -> bool:
        """
        Remove a section. Return `True` if the section existed, else `False`.
        """
        return self.__config.remove_section(section)

    def get_sections(self: Self) -> List[str]:
        """
        Return a list of section names, excluding `[DEFAULT]`.
        """
        return self.__config.sections()

    def get_options(self: Self, section: str) -> List[str]:
        """
        Return a list of option names for the given section name.
        """
        return self.__config.options(section)

    def get_option(self: Self, section: str, option: str) -> Optional[Any]:
        """
        Get the value of an option for a given section.
        """
        return convert(self.__config.get(section, option))

    def set_option(self: Self, section: str, option: str, value: Optional[Any]) -> None:
        """
        Set the value of an option for a given section.
        """
        self.__config.set(section, option, str(value))

    def remove_option(self: Self, section: str, option: str) -> bool:
        """
        Remove an option. Return `True` if the option existed, else `False`.
        """
        return self.__config.remove_option(section, option)

    #endregion

    #region Properties

    @property
    def json(self: Self) -> Dict[str, Dict[str, Optional[Any]]]:
        """
        Convert the content of the INI file to JSON, excluding `[DEFAULT]`.
        """
        return {
            section: {
                option: convert(value) for option, value in self.__config[section].items()
            } for section in self.__config.sections()
        }

    #endregion
