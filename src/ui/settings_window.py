"""
首选项 页面,
现在作为独立窗口运行, 包含了所有可操控的设置项,
引用时可作 SettWindow
"""

import asyncio
from enum import Enum
from typing import Optional

from qfluentwidgets import FluentWindow, qconfig
from qfluentwidgets import FluentIcon as FI

from app_const_var import AssetsPathTXT
from app_config import AppConfig
from ui.ui_str import SettWindowString


class SettWindow(FluentWindow):
    """首选项窗口, 继承自FluentWindow"""

    def __init__(self) -> None:
        """初始化窗口"""
        super().__init__()

        # 加载配置文件
        self.cfg = AppConfig()
        qconfig.load(AssetsPathTXT.APP_CONFIG, self.cfg)

        # 运行导入子页面的asyncio程序
        asyncio.run(self.import_ui())

        # 初始化窗口设置
        self.init_window()

        # 初始化导航栏
        self.init_navigation()

        # 初始化信号连接函数
        self.singal_connection()

    # ========== 异步导入子页面 ==========

    async def import_namelists_ui(self) -> None:
        """导入并重命名 名单管理 子页面的协程"""
        from ui.settings_ui.settings_namelists_ui_logic import SettNLUILogic

        self.namelists_ui = SettNLUILogic(self)
        self.namelists_ui.setObjectName(SettWindowString.NAMELISTS_UI_OBJNAME)

    async def import_language_ui(self) -> None:
        """导入并重命名 语言 子页面的协程"""
        from ui.settings_ui.settings_language_ui import SettLangUI

        self.language_ui = SettLangUI(self)
        self.language_ui.setObjectName(SettWindowString.LANGUAGE_UI_OBJNAME)

    async def import_ui(self) -> None:
        """导入子页面的基础函数"""
        await asyncio.gather(self.import_namelists_ui(), self.import_language_ui())

    # ========== 导航栏初始化 ==========

    def init_navigation(self) -> None:
        """初始化导航栏, 添加各个子界面"""
        from qfluentwidgets import NavigationItemPosition

        # 名单管理
        self.addSubInterface(
            self.namelists_ui,
            FI.BRIGHTNESS,
            SettWindowString.NAMELISTS_UI_NAVNAME,
            NavigationItemPosition.TOP,
        )

        # 语言
        self.addSubInterface(
            self.language_ui,
            FI.LANGUAGE,
            SettWindowString.LANGUAGE_UI_NAVNAME,
            NavigationItemPosition.TOP,
        )

    def _apply_theme(self, mode: Optional[Enum] = None) -> None:
        """设置应用全局主题"""

        qconfig.save()

        if mode is None:
            mode = self.cfg.DarkLight.value

    # ========== 窗口设置 ==========

    def init_window(self) -> None:
        """初始化窗口设置"""
        self._apply_theme()
        self.resize(1080, 768)
        self.setWindowTitle(SettWindowString.SETTWINDOW_TITLE)

    # ========== 信号连接 ==========

    def singal_connection(self) -> None:
        """信号连接函数"""

        # 主题更改信号
        self.cfg.DarkLight.valueChanged.connect(self._apply_theme)
