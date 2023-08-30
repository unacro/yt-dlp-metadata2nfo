import os
import json
from xml.etree import ElementTree as et
import xml.dom.minidom as minidom
from loguru import logger
from .config import Config


class MetadataFileHandler(object):

    TargetPath: str = Config.get("TARGET_PATH")

    @classmethod
    def _get_metadata_raw_file_list(cls, force_rewrite: bool = False,
                                    dir_path: str = "") -> list:
        if dir_path == "":
            dir_path = cls.TargetPath
        logger.debug("Ready to process path: [{}]", dir_path)
        raw_file_list: list = []
        for home, _, files in os.walk(dir_path):
            for filename in files:
                if filename.lower().endswith(".info.json"):
                    logger.debug("Found {}", filename)
                    nfo_file: str = filename.split(".info.json")[0] + ".nfo"
                    if force_rewrite or not os.path.isfile(
                            os.path.join(home, nfo_file)):
                        raw_file_list.append(os.path.join(home, filename))
        return raw_file_list

    @classmethod
    def _read_metadata_info(cls, metadata_json_file: str) -> dict:
        json_dict: dict = {}
        try:
            with open(metadata_json_file, 'r', encoding="utf8") as f:
                json_dict = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read metadata file(*.info.json): {e}")
        return json_dict

    @classmethod
    def _gen_metadata_xml(cls, raw_file: str) -> bool:
        metadata: dict = cls._read_metadata_info(raw_file)
        if not metadata:
            return False  # not get data
        if "_type" not in metadata or metadata["_type"] == "playlist":
            return False  # only process video
        # already use --parse-metadata "video::(?P<formats>)" in yt-dlp.conf
        # if "formats" in metadata:
        #     del metadata["formats"]
        root_node = et.Element('musicvideo')  # regarded as mv

        # Title 标题
        et.SubElement(root_node, "title").text = metadata["fulltitle"]

        # Sort title 短标题
        et.SubElement(root_node, "sorttitle").text = metadata["title"]

        # Artists 艺术家
        et.SubElement(root_node, "artist").text = f"{metadata['uploader']}"

        # Album 专辑
        upload_date: str = '-'.join([
            metadata["upload_date"][:4],
            metadata["upload_date"][4:6],
            metadata["upload_date"][6:],
        ])
        description: str = ""
        et.SubElement(root_node, "album").text = upload_date
        if metadata["extractor"] == "youtube":
            # et.SubElement(root_node, "album").text = "y2b" + metadata["id"]
            description = f"""\
<a href="https://www.youtube.com/watch?v={metadata['id']}">
{metadata['fulltitle']}</a>&nbsp;by
<a href="https://www.youtube.com/{metadata['uploader_id']}">
{metadata['uploader']}</a><br><br>
"""
        elif metadata["extractor"] == "AcFunVideo":
            # et.SubElement(root_node, "album").text = "ac" + metadata["id"]
            description = f"""\
<a href="https://www.acfun.cn/v/ac{metadata['id']}">
{metadata['fulltitle']}</a>&nbsp;by
<a href="https://www.acfun.cn/u/{metadata['uploader_id']}">
{metadata['uploader']}</a><br><br>
"""
        else:  # bilibili
            # et.SubElement(root_node, "album").text = metadata["id"]
            description = f"""\
<a href="https://www.bilibili.com/video/{metadata['id']}">
{metadata['fulltitle']}</a>&nbsp;by
<a href="https://space.bilibili.com/{metadata['uploader_id']}">
{metadata['uploader']}</a><br><br>
"""

        # Tagline 宣传词
        et.SubElement(root_node, "tagline").text = ", ".join(metadata["tags"])

        # Overview 内容概述
        if "description" in metadata:
            description += metadata["description"]
        et.SubElement(root_node, "plot").text = description

        # Release date 发行日期
        et.SubElement(root_node, "releasedate").text = upload_date

        # Year 年份
        et.SubElement(root_node, "year").text = metadata["upload_date"][:4]

        # Poster 封面
        art_node = et.SubElement(root_node, "art")
        et.SubElement(art_node, "poster").text = metadata["thumbnail"]
        # raw_file.replace(".info.json", ".jpg")  # local thumb image

        # Genres 风格
        # 为了准确度 应该手动编辑
        # et.SubElement(root_node, "genre").text = "未识别风格"

        # People 人物
        actor_node = et.SubElement(root_node, "actor")
        et.SubElement(actor_node, "name").text = metadata["uploader"]
        et.SubElement(actor_node, "type").text = "Actor"
        et.SubElement(actor_node, "role").text = "UP主"

        # Tags 标签
        # 强迫症无法接受 标签库被源视频站(为了传播率/推广)乱打的*关键词*污染
        # for tag in metadata["tags"]:
        #     tag_node = et.SubElement(root_node, 'tag')
        #     tag_node.text = tag

        # format xml
        reparsed = minidom.parseString(et.tostring(root_node, 'utf-8'))
        new_str = reparsed.toprettyxml(indent='\t')

        # write to .nfo file
        try:
            filename: str = raw_file[raw_file.rfind('\\')+1:]
            filename = filename[:filename.rfind(".info")]
            with open(raw_file.replace(".info.json", ".nfo"),
                      'w', encoding="utf8") as f:
                f.write(new_str)
            return True
        except Exception as e:
            logger.error(f"Failed to write metadata xml (*.nfo): {e}")

        return False

    @classmethod
    def map_to_nfo(cls, force_reflush: bool = False) -> bool:
        md_raw_file_list: list = cls._get_metadata_raw_file_list(force_reflush)
        if len(md_raw_file_list) > 0:
            logger.info("Found {} metadata file (*.info.json) to process",
                        len(md_raw_file_list))
            for index, json_file in enumerate(md_raw_file_list):
                logger.info(
                    f"Process [{index+1}/{len(md_raw_file_list)}] {json_file}")
                if not cls._gen_metadata_xml(json_file):
                    return False
        return True
