#!/usr/env python3

from __future__ import annotations

from constants.constants import DEFAULT_WEBSOCKET_PORT, DEFAULT_SERVICES_DIRECTORY_PATH, DEFAULT_LOGGING_LEVEL, DEFAULT_LOGGING_FILENAME
from utils import utils


class ADConfiguration:
    """
    Auto doodle configuration variables
    It is normally used in read-only and set by the arguments of the main
    """
    websocket_scheduler_port: int = DEFAULT_WEBSOCKET_PORT
    """Port used by the websocket scheduler to access a service"""

    services_directory_path: str = DEFAULT_SERVICES_DIRECTORY_PATH
    """Directory path used to store the .py services"""

    logging_level: str = DEFAULT_LOGGING_LEVEL
    """Logging level of the process"""

    logging_filename: str = DEFAULT_LOGGING_FILENAME
    """Logging filename in which logs are stored"""

    def load_from_blob_of_args(self, *args, **kwargs) -> bool:
        """Function called by the main to fill the internal configuration variables from the passed values"""

        members = utils.get_object_member_variables(self)

        for key in members:
            if key in kwargs and kwargs[key] != None:
                setattr(self, key, kwargs[key])
        return True

    def __repr__(self) -> str:
        members = utils.get_object_member_variables(self)
        return str(members)
