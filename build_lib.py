import os
import re
import shutil
import zipfile
import argparse
import json
from pathlib import Path
from typing import TypedDict


class Docs(TypedDict):
    README: Path
    LICENSE: Path

class Dirs(TypedDict):
    template: Path
    build: Path
    release: Path

class Paths(TypedDict):
    template: Path
    script: Path

class Config(TypedDict):
    project: str
    docs: Docs
    dirs: Dirs
    paths: Paths
    replacements: dict[str, str | Path]


def get_args():
    parser = argparse.ArgumentParser(description="AviUtl2 Script Builder")

    parser.add_argument(
        "--version",
        default = "v0.1.0",
        help = "Script version (default: v0.1.0)"
    )

    return parser.parse_args()


def load_config(path: Path, root: Path) -> Config:
    try:
        with open(path, 'r', encoding="utf-8") as f:
            config = json.load(f)

        project = config.get("project", "")
        suffix = config.get("suffix", ".anm2")
        config["directories"] = {k: Path(v) for k, v in config.get("directories", {}).items()}
        replacements = config.get("replacements", {})
        dirs: Dirs = {
            "template": root / config["directories"].get("template", Path("scripts")),
            "build": root / config["directories"].get("build", Path("build")),
            "release": root / config["directories"].get("build", Path("build")) / "release"
        }

        return {
            "project": project,
            "docs": {
                "README": root / "README.md",
                "LICENSE": root / "LICENSE"
            },
            "dirs": dirs,
            "paths": {
                "template": dirs["template"] / (project + "_template" + suffix),
                "script": dirs["release"] / (project + suffix)
            },
            "replacements": {
                **{k: Path(v) for k, v in replacements.get("files", {}).items()},
                **{k: v for k, v in replacements.get("strings", {}).items()},
                "PROJECT_NAME": project,
                "VERSION": get_args().version
            }
        }
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")


def build_script(template: Path, output: Path, replacements: dict[str, str | Path], write_newline: str | None = "\r\n"):
    try:
        content = template.read_text(encoding="utf-8")
        pattern = r"\$\{([a-zA-Z0-9_]+)\}"

        def replacer(match: re.Match[str]) -> str:
            key = match.group(1)
            val = replacements.get(key)

            if val is None:
                return match.group(0)
            
            if isinstance(val, Path):
                if (val.exists()):
                    return val.read_text(encoding="utf-8")
                else:
                    return match.group(0)
            else:
                return str(val)

        updated_content = re.sub(pattern, replacer, content)

        output.parent.mkdir(exist_ok=True, parents=True)
        output.write_text(updated_content, encoding="utf-8", newline=write_newline)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def copy_docs(src: Docs, dst: Path):
    for _, path in src.items():
        if isinstance(path, Path) and path.exists():
            shutil.copy2(path, dst)


def create_release_note(src: Path, dst: Path):
    if not src.exists():
        return

    try:
        lines = src.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        raise RuntimeError(f"Failed to read {src}: {e}")

    try:
        start_index = next(i for i, line in enumerate(lines) if line.strip() == "## Change Log")
    except StopIteration:
        raise ValueError("Missing required section: '## Change Log'")

    lines = lines[start_index + 1:]

    version_header_pattern = re.compile(r"- \*\*(v[\d.]+)\*\*")
    change_line_pattern = re.compile(r"^\s*-\s(.+)")

    changes: list[str] = []
    found_version = False
    for line in lines:
        if version_header_pattern.match(line):
            if found_version:
                break
            found_version = True
            continue

        if found_version:
            match = change_line_pattern.match(line)
            if match:
                changes.append(f"- {match.group(1).strip()}")

    if not changes:
        return

    content = "## What's Changed\n" + "\n".join(changes) + "\n"
    output = dst / "release_note.txt"
    output.write_text(content, encoding="utf-8", newline="\n")


def create_zip(src: Path, dst: Path, zip_name: str, root_name: str | None = None):
    if root_name is None:
        root_name = zip_name
    
    output = dst / (zip_name + ".zip")

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(src):
            root_path = Path(root)
            rel_path = root_path.relative_to(src)

            if rel_path == Path('.'):
                arc_path = Path(root_name)
            else:
                arc_path = Path(root_name) / rel_path

            for file in files:
                file_path = root_path / file
                arc_file_path = arc_path / file
                zipf.write(file_path, arc_file_path.as_posix())
