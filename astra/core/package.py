import io
import json
import os
import re
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import validate, ValidationError


@dataclass
class Text():
    file: Path
    content: str


@dataclass
class Assets():
    directory: Path
    url: str | None
    texts: list[Text]


@dataclass
class Notes():
    source: Path


@dataclass
class Package():
    clean: bool
    directory: Path
    name: str
    files: list[Path]
    assets: list[Assets]
    notes: Notes


def load(path: Path, tmp: Path) -> Package:
    schema: dict[str, Any] = {
        "type": "object",
        "required": ["project", "build", "package"],
        "properties": {
            "project": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "author": {"type": "string"}
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
                "package": {
                    "type": "object",
                    "required": ["directory", "archive", "notes"],
                    "properties": {
                        "clean": {"type": "boolean"},
                        "directory": {"type": "string"},
                        "archive": {
                            "type": "object",
                            "properties": {
                                "files": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "assets": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["directory"],
                                        "properties": {
                                            "directory": {"type": "string"},
                                            "url": {"type": "string"},
                                            "texts": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": ["file", "content"],
                                                    "properties": {
                                                        "file": {"type": "string"},
                                                        "content": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "notes": {
                            "type": "object",
                            "required": ["source"],
                            "properties": {
                                "source": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "additionalProperties": True
        }
    }

    try:
        with open(path, encoding="utf-8") as f:
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
    directory: Path = root / Path(data["package"]["directory"])

    files: list[Path] = [
        root / Path(f) for f in data["package"]["archive"].get("files", [])]
    for script in data["build"]["scripts"]:
        name: str = script.get("name", proj_name)
        suffix: str = script["suffix"]
        files.append(build / f"{name}{suffix}")

    assets: list[Assets] = []
    for asset in data["package"]["archive"].get("assets", []):
        dst: Path = directory / tmp / Path(asset["directory"])

        texts: list[Text] = []
        for text in asset.get("texts", []):
            texts.append(Text(
                dst / Path(text["file"]),
                text["content"]
            ))

        assets.append(Assets(
            dst,
            asset.get("url", None),
            texts
        ))

    notes: Notes = Notes(
        root / Path(data["package"]["notes"]["source"])
    )

    return Package(
        data["package"].get("clean", True),
        directory,
        proj_name,
        files,
        assets,
        notes
    )


def create_release_notes(src: Path, dst: Path) -> None:
    if not src.exists():
        return

    try:
        lines: list[str] = src.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        raise RuntimeError(f"Failed to read {src}: {e}")

    try:
        idx: int = next(i for i, l in enumerate(lines)
                        if l.strip() == "## Change Log")
    except StopIteration:
        raise ValueError("Missing required section: '## Change Log'")

    log: list[str] = lines[idx + 1:]

    ver_re: re.Pattern[str] = re.compile(r"- \*\*(v[\d.]+)\*\*")
    chg_re: re.Pattern[str] = re.compile(r"^\s*-\s(.+)")

    changes: list[str] = []
    in_section: bool = False
    for l in log:
        if ver_re.match(l):
            if in_section:
                break

            in_section = True
            continue

        if in_section and (m := chg_re.match(l)):
            changes.append(f"- {m.group(1).strip()}")

    if not changes:
        return

    content: str = "## What's Changed\n" + "\n".join(changes) + "\n"
    (dst / "release_notes.txt").write_text(content, encoding="utf-8", newline="\n")


def pack(src: Path, dst: Path, name: str) -> None:
    if not dst.exists() or not dst.is_dir():
        return

    with zipfile.ZipFile(dst / f"{name}.zip", 'w', zipfile.ZIP_DEFLATED) as zf:
        for curr, _, files in os.walk(src):
            root: Path = Path(curr)
            rel: Path = root.relative_to(src)
            base: Path = Path(name) / rel if rel != Path('.') else Path(name)

            for f in files:
                zf.write(root / f, (base / f).as_posix())


def download_assets(url: str, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(url) as response:
        data: bytes = response.read()

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        zf.extractall(dst)


def copy(src: list[Path], dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)

    for path in src:
        if path.exists():
            if path.is_dir():
                shutil.copytree(path, dst / path.name, dirs_exist_ok=True)
            else:
                shutil.copy2(path, dst)


def package(path: Path, tmp: Path = Path("tmp")) -> None:
    data: Package = load(path, tmp)

    if data.clean and data.directory.exists() and data.directory.is_dir():
        shutil.rmtree(data.directory)

    data.directory.mkdir(parents=True, exist_ok=True)

    copy(data.files, data.directory / tmp)

    for asset in data.assets:
        if asset.url:
            download_assets(asset.url, asset.directory)

        for text in asset.texts:
            text.file.parent.mkdir(parents=True, exist_ok=True)
            text.file.write_text(text.content, encoding="utf-8", newline="\n")

    create_release_notes(data.notes.source, data.directory)

    pack(data.directory / tmp, data.directory, data.name)

    shutil.rmtree(data.directory / tmp)
