# yt-dlp-metadata2nfo

Generate NFO files (for emby / jellyfin / plex) as metadata files from yt-dlp's .info.json files.

Support Youtube, AcFun and Bilibili.

## Usage

1. `git clone https://github.com/unacro/yt-dlp-metadata2nfo.git && cd yt-dlp-metadata2nfo.git`
2. `poetry install`
3. `cp .env.example .env` and edit `.env` file
4. `poetry run start`

**Notice**: Need enable **NFO** as first prority metadata saver.

> **注意**：控制台 > 媒体库 > 管理媒体库 > 媒体资料储存方式：勾上 NFO 并作为首选项。
