"""
常变量文件
本文件是储存项目常量与变量标准值的文件, 不包括ui的字符串
"""

"""
====================
相对路径常量
====================
"""


class AssetsPathTXT:
    """资源相对路径纯文本类"""

    # 图片
    # 图标
    APP_ICON_DARK_PATH = "assets/icons/app_icon_dark.png"
    APP_ICON_LIGHT_PATH = "assets/icons/app_icon_light.png"

    # 项目详细图
    APP_DETAILEDIMAGE_DARK_PATH = "assets/images/app_detailed_image_dark.png"
    APP_DETAILEDIMAGE_LIGHT_PATH = "assets/images/app_detailed_image_light.png"

    # 配置文件
    APP_CONFIG = "config/app_config.json"

    # 音频
    # 默认音乐
    APP_DEFAULT_MUSIC_PATH = ""

    # 默认音效
    APP_DEFAULT_SOUND_PATH = "assets/sounds/notice.wav"

    # 文本文件
    # 名单
    APP_NAMELISTS_FOLDER = "namelists/"

    # 文档
    APP_DOCS_FOLDER = "docs/"


class AssetsPath:
    """资源相对路径类"""

    from pathlib import Path

    # 音频
    # 默认音乐
    APP_DEFAULT_MUSIC_PATH = Path(AssetsPathTXT.APP_DEFAULT_MUSIC_PATH)

    # 默认音效
    APP_DEFAULT_SOUND_PATH = Path(AssetsPathTXT.APP_DEFAULT_SOUND_PATH)


"""
====================
Web地址常量
====================
"""


class WebUrl:
    """网址类"""

    # 一言API接口
    HITOKOTO_API_URL = "https://v1.hitokoto.cn/"
    HITOKOTO_API_URL_WITH_FORMAT = "https://v1.hitokoto.cn/?c=i&encode=text"

    # 加入翻译计划( 语言 子页面)
    JOIN_TRANSLATION_LINK = ""


"""
====================
字符串常量
====================
"""


class AppConfigString:
    """应用配置类 的字符串, 仅包含 app_config.py 相关字符串"""

    # 语言 类字符串
    LANGUAGE_GROUP = "Language"
    LANGUAGE_NAME = "Language"

    # 基本 类字符串
    BASIC_GROUP = "Basic"
    BASIC_NAMELISTS_NAME = "NameLists"
    BASIC_CARTON_BEAUTY_LEVEL_NAME = "CartonBeautyLevel"
    BASIC_SHOW_RESULT_WAY_NAME = "ShowResultWay"

    # 视听 类字符串
    AV_GROUP = "Av"
    AV_MUSIC_SWITCH_NAME = "MusicSwitch"
    AV_MUSIC_PATH_NAME = "MusicPath"
    AV_MUSIC_VOLUME_NAME = "MusicVolume"
    AV_MUSIC_PLAY_SMOOTHLY_NAME = "MusicPlaySmoothly"
    AV_MUSIC_PAUSE_SMOOTHLY_NAME = "MusicPauseSmoothly"
    AV_SOUND_SWITCH_NAME = "SoundSwitch"
    AV_SOUND_PATH_NAME = "SoundPath"
    AV_SOUND_PLAY_TIME_NAME = "SoundPlayTime"
    AV_READ_SWITCH_NAME = "ReadSwitch"
    AV_READ_TIME_NAME = "ReadTime"
    AV_DARK_LIGHT_NAME = "DarkLight"
    AV_WINDOW_EFFORT_NAME = "WindowEffort"
    AV_HITOKOTO_API_NAME = "HitokotoApi"
    AV_HITOKOTO_RENEW_NAME = "HitokotoRenewTime"


class LogicFilesString:
    """逻辑文件的字符串"""

    # add_import_export_namelist.py
    AIENAMELIST_HEADER_EXIST = "Exist?"
    AIENAMELIST_HEADER_NO = "No."
    AIENAMELIST_HEADER_NAME = "Name"
    AIENAMELIST_HEADER_GENDER = "Gender"
    AIENAMELIST_HEADER_GROUP = "Group"
    AIENAMELIST_HEADER_TIP = "Tip"
    AIENAMELIST_HEADER = [
        AIENAMELIST_HEADER_EXIST,
        AIENAMELIST_HEADER_NO,
        AIENAMELIST_HEADER_NAME,
        AIENAMELIST_HEADER_GENDER,
        AIENAMELIST_HEADER_GROUP,
        AIENAMELIST_HEADER_TIP,
    ]

    # ui_str.py
    # gettext 键名
    LANG_DOMAIN = "messages"
    LANG_LOCALEDIR = "locales"

    # json 键名
    LANG_JSON_1 = "Language"
    LANG_JSON_2 = "Language"
