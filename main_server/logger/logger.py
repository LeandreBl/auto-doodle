#!/usr/bin/env python3

from __future__ import annotations

import logging
import os


def setupLogger(loglevel: str, logfilename: str) -> bool:
    LOG_LEVELS = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG
    }

    loglevel = loglevel.upper()

    if loglevel not in LOG_LEVELS:
        print(
            f'Invalid log-level: {loglevel}, it must be one of {LOG_LEVELS.keys()}')
        return False

    log_directory: str = os.path.dirname(logfilename)

    if not os.path.exists(log_directory):
        os.makedirs(os.path.dirname(logfilename))

    log_format: str = '[%(levelname)-8s] [%(asctime)s] [#%(threadName)-8s] [%(filename)s:%(lineno)d] -- %(message)s'

    logging.basicConfig(
        format=log_format,
        level=loglevel,
        handlers=[
            logging.FileHandler(logfilename, 'a'),
            logging.StreamHandler()
        ]
    )
    return True
