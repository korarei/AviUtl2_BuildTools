import json
from pathlib import Path
from typing import Any


def init(dst: Path, force: bool) -> None:
    template: dict[str, Any] = {
        "project": {
            "name": "Project",
            "version": "v0.1.0",
            "author": "name"
        },
        "build": {
            "clean": True,
            "directory": "build",
            "scripts": [
                {
                    "name": "Effect",
                    "suffix": ".anm2",
                    "newline": "\r\n",
                    "source": {
                        "tag": ".in",
                        "include_directories": [
                            "includes"
                        ],
                        "variables": {
                            "LABEL": "加工"
                        }
                    }
                }
            ]
        },
        "install": {
            "clean": True,
            "directory": "C:/ProgramData/aviutl2/Script"
        },
        "package": {
            "clean": True,
            "directory": "package",
            "archive": {
                "files": [
                    "../README.md",
                    "../LICENSE"
                ],
                "assets": [
                    {
                        "directory": "assets",
                        "url": "https://",
                        "texts": [
                            {
                                "file": "credits.txt",
                                "content": "This is a sample asset."
                            }
                        ]
                    }
                ]
            },
            "notes": {
                "source": "../README.md"
            }
        }
    }

    path: Path = dst / "astra.config.json"

    if not force and path.exists():
        return

    with open(path, 'w', encoding="utf-8") as f:
        json.dump(template, f, indent=4, ensure_ascii=False)
