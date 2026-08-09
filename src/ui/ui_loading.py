"""
初始化UI的各种界面绘制行为与逻辑行为, 也包含一些动态加载逻辑
"""

from typing import Union, Literal
from enum import Enum
from qfluentwidgets import Theme, theme, setTheme, qconfig
from PySide2.QtWidgets import QWidget
from app_config import AppConfig, AppEnums
from app_const_var import AssetsPathTXT


# 加载配置文件
cfg = AppConfig()
qconfig.load(AssetsPathTXT.APP_CONFIG, cfg)


def apply_theme_from_config(app_detailed_image, mode: Union[Enum, None] = None) -> None:
    """根据配置文件中的 dark_light 或提供的模式设置应用全局主题"""

    if mode == None:
        mode = cfg.DarkLight.value

    if mode == AppEnums.DarkLightEnum.LIGHT:
        setTheme(Theme.LIGHT)
        app_detailed_image.setPixmap(AssetsPathTXT.APP_DETAILEDIMAGE_LIGHT_PATH)

    elif mode == AppEnums.DarkLightEnum.DARK:
        setTheme(Theme.DARK)
        app_detailed_image.setPixmap(AssetsPathTXT.APP_DETAILEDIMAGE_DARK_PATH)

    elif mode == AppEnums.DarkLightEnum.AUTO:
        setTheme(Theme.AUTO)

        # 判断具体主题
        if theme() == Theme.DARK:
            app_detailed_image.setPixmap(AssetsPathTXT.APP_DETAILEDIMAGE_DARK_PATH)
        else:
            app_detailed_image.setPixmap(AssetsPathTXT.APP_DETAILEDIMAGE_LIGHT_PATH)

    else:
        # 默认深色主题
        setTheme(Theme.DARK)
        app_detailed_image.setPixmap(AssetsPathTXT.APP_DETAILEDIMAGE_DARK_PATH)


def get_theme_from_config() -> Literal["LIGHT", "DARK"]:
    """根据配置文件中的 dark_light 获取应用全局主题"""

    mode = cfg.DarkLight.value

    if mode == AppEnums.DarkLightEnum.LIGHT:
        return "LIGHT"

    elif mode == AppEnums.DarkLightEnum.DARK:
        return "DARK"

    elif mode == AppEnums.DarkLightEnum.AUTO:
        # 判断具体主题
        if theme() == Theme.DARK:
            return "DARK"
        else:
            return "LIGHT"

    else:
        # 默认深色主题
        return "DARK"
