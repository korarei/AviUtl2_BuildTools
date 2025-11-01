import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import validate, ValidationError


@dataclass
class Install():
    clean: bool
    directory: Path | None
    files: list[Path]


def load(path: Path, dst: Path | None) -> Install:
    schema: dict[str, Any] = {
        "type": "object",
        "required": ["project", "build", "install"],
        "properties": {
            "project": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "author": {"type": "string"}
                }
            },
            "build": {
                "type": "object",
                "required": ["directory", "scripts"],
                "properties": {
                    "clean": {"type": "boolean"},
                    "directory": {"type": "string"},
                    "scripts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["suffix", "source"],
                            "properties": {
                                "name": {"type": "string"},
                                "suffix": {"type": "string"},
                                "newline": {"type": "string"},
                                "source": {
                                    "type": "object",
                                    "properties": {
                                        "tag": {"type": "string"},
                                        "include_directories": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "variables": {
                                            "type": "object",
                                            "additionalProperties": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "install": {
                "type": "object",
                "properties": {
                    "clean": {"type": "boolean"},
                    "directory": {"type": "string"}
                }
            }
        },
        "additionalProperties": True
    }

    try:
        with open(path, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON file: {path}")

    try:
        validate(data, schema)
    except ValidationError as e:
        raise ValueError(f"Invalid config file: {e.message}")

    root: Path = path.parent
    proj_name: str = data["project"]["name"]
    build: Path = root / Path(data["build"]["directory"])
    files: list[Path] = []
    for script in data["build"]["scripts"]:
        name: str = script.get("name", proj_name)
        suffix: str = script["suffix"]
        files.append(build / f"{name}{suffix}")

    directory: str | None = data["install"].get("directory", None)

    return Install(
        data["install"].get("clean", True),
        dst or (Path(directory).resolve() if directory else None),
        files
    )


def install(path: Path, dst: Path | None = None) -> None:
    data: Install = load(path, dst)

    if data.directory is None:
        return

    if data.clean and data.directory.exists() and data.directory.is_dir():
        shutil.rmtree(data.directory)

    data.directory.mkdir(parents=True, exist_ok=True)

    for file in data.files:
        if file.exists() and file.is_file():
            shutil.copy2(file, data.directory)
