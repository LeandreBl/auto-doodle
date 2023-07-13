#!/usr/bin/env python3

from __future__ import annotations

import sys
import argparse
import os

from logger.logger import setupLogger, logging

from ad_types.configuration import ADConfiguration
from utils.utils import get_object_member_variables
from websocket_scheduler.websocket_scheduler import WebsocketScheduler

VERSION: float = 0.1

def main(argv: list[str]) -> int:
    main_ad_configuration: ADConfiguration = ADConfiguration()
    parser = argparse.ArgumentParser(
        prog="Auto-Doodle",
        description="Background daemon to provide services from websocket connections"
    )
    members = get_object_member_variables(main_ad_configuration)

    for member in members:
        parser.add_argument(
            f"--{member.replace('_', '-')}", dest=member, type=type(getattr(main_ad_configuration, member)))

    args = parser.parse_args(argv[1:])

    parser_members = get_object_member_variables(args)

    main_ad_configuration.load_from_blob_of_args(**parser_members)

    if not setupLogger(main_ad_configuration.logging_level, os.path.join(main_ad_configuration.logging_directory, main_ad_configuration.logging_filename)):
        return 1

    logging.info(f"Starting Auto-Doodle v{VERSION}")
    logging.debug(main_ad_configuration)

    websocket_scheduler: WebsocketScheduler = WebsocketScheduler(
        main_ad_configuration)

    websocket_scheduler.start()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))  # next section explains the use of sys.exit
