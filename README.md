# Astra

AviUtl ExEdit2のスクリプトビルド，インストール，パッケージングを行うツール．

## インストール方法

### pipでインストール

```bash
pip install git+https://github.com/korarei/AviUtl2_Astra.git@v0.1.0
```

## 使用方法

### 設定

  `astra.config.json`をスクリプトと同じ階層に用意する．

  パスは基本的にこの設定ファイルからの相対パスで指定する．

  ただし，`assets`のパスはアーカイブパスで指定する．

  ```JSON
  {
    "project": {
      "name": "Project",
      "version": "v0.1.0",
      "author": "name"
    },
    "build": {
      "clean": true,
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
  ```

  上記設定ファイルは以下のコマンドでも作成できる．

  ```bash
  astra init
  ```

### ビルド

  `astra.config.json`のあるフォルダに移動し，以下のコマンドを実行する．

  ```bash
  astra build
  ```

  ビルドは`astra.config.json`と同階層にある`{name}{tag}{suffix}`に対して行う．

  `${VAR}`のように書いたところは`variables`で指定した文字に置換される．

  `variables`以外に`PROJECT_NAME`と`SCRIPT_NAME`を使用できる．`version`と`author`が設定されている場合`VERSION`と`AUTHOR`を使用できる．

  `--#include "a.hlsl"`のように書いた場合，スクリプトからの相対パス検索を行い，見つかった場合その内容で置換する．

  `--#include <a.hlsl>`のように書いた場合，`include_directories`からの相対パス検索を行い，見つかった場合その内容で置換する．

### インストール

  ビルド後，`astra.config.json`のあるフォルダで以下のコマンドを実行する．

  ```bash
  astra install
  ```

### パッケージング

  ビルド後，`astra.config.json`のあるフォルダで以下のコマンドを実行する．

  ```bash
  astra package
  ```

## License

LICENSEに記載．

## Credits

### jsonschema

https://github.com/python-jsonschema/jsonschema

---

The MIT License

Copyright (c) 2013 Julian Berman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

## Change Log
- **v0.1.0**
  - Release
