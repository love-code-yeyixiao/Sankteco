"""
初始化UI的各种界面绘制行为与逻辑行为, 也包含一些动态加载逻辑
"""

from typing import Literal
from qfluentwidgets import Theme, theme, qconfig
from app_config import AppConfig, AppEnums
from app_const_var import AssetsPathTXT


# 加载配置文件
cfg = AppConfig()
qconfig.load(AssetsPathTXT.APP_CONFIG, cfg)


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
