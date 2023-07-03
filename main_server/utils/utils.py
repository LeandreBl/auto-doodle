#!/usr/bin/env python3

from __future__ import annotations

from typing import Any
import os

def get_object_member_variables(obj: object) -> dict[str, Any]:
    return {attr:getattr(obj, attr) for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__")}

def get_matching_filenames_in_directory(directory_path: str, extension: str) -> list[str]:
    return list(filter(lambda filepath: filepath.endswith(extension), filter(os.path.isfile, map(lambda filename: os.path.join(directory_path, filename), os.listdir(directory_path)))))