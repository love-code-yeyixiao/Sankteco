"""
主页面, 
此页面是本项目的主要GUI界面, 包含与各子页面的交互逻辑, 控件响应等, 
引用时可作 MainUI
"""

import asyncio
from enum import Enum
from typing import Union
from qfluentwidgets import FluentWindow, qconfig
from qfluentwidgets import FluentIcon as FI
from app_const_var import AssetsPathTXT
from app_config import AppConfig
from ui.ui_str import MainUIString, BasicString
from ui.ui_loading import get_theme_from_config, apply_theme_from_config


class MainWindow(FluentWindow):
    """应用程序主窗口, 继承自FluentWindow"""

    def __init__(self):
        """初始化主窗口"""
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
        
        # 插件系统集成
        self._init_plugin_system()

    async def import_information_ui(self):
        """导入并重命名 信息 子页面的协程"""
        from ui.informations_ui.informations_ui_logic import InformationUILogic

        self.information_ui = InformationUILogic(self)
        self.information_ui.setObjectName(MainUIString.SUBPAGE_INFORMATION_OBJNAME)

        # 设置文档阅读页面图标
        if self.information_ui.docs_reader_ui != None:
            self.information_ui.docs_reader_ui.setWindowIconText(self.windowIconText())

    async def import_settings_ui(self):
        """导入并重命名 设置 子页面其及所有孙页面的协程"""
        from ui.settings_ui.settings_ui import SettingsUI
        from ui.settings_ui.settings_basic_ui_logic import SettingsBasicUILogic
        from ui.settings_ui.settings_audiovisual_ui_logic import (
            SettingsAudiovisualUILogic,
        )
        from ui.settings_ui.settings_language_ui import SettingsLanguageUI

        # 设置 子页面
        self.settings_ui = SettingsUI(self)
        self.settings_ui.setObjectName(MainUIString.SUBPAGE_SETTINGS_OBJNAME)

        # 基础 孙页面
        self.settings_basic_ui = SettingsBasicUILogic(self)
        self.settings_basic_ui.setObjectName(
            MainUIString.SUBSUBPAGE_SETTIING_BASIC_OBJNAME
        )

        # 视听 孙页面
        self.settings_audiovisual_ui = SettingsAudiovisualUILogic(self)
        self.settings_audiovisual_ui.setObjectName(
            MainUIString.SUBSUBPAGE_SETTIING_AUDIOVISUAL_OBJNAME
        )

        # 语言 孙页面
        self.settings_language_ui = SettingsLanguageUI(self)
        self.settings_language_ui.setObjectName(
            MainUIString.SUBSUBPAGE_SETTIING_LANGUAGE_OBJNAME
        )

    async def import_pray_ui(self):
        """导入并重命名 祈福 子页面的协程"""
        from ui.pray_ui.pray_ui import PrayUI

        # 祈福 子页面
        self.pray_ui = PrayUI(self)
        self.pray_ui.setObjectName(MainUIString.SUBPAGE_PRAY_OBJNAME)

    async def import_ui(self):
        """导入子页面的基础函数"""

        # 创建并发执行任务
        await asyncio.gather(
            self.import_pray_ui(),
            self.import_information_ui(),
            self.import_settings_ui(),
        )

    def init_navigation(self):
        """初始化导航栏, 添加各个子界面"""
        from qfluentwidgets import NavigationItemPosition

        # 添加子界面及各自的孙页面
        self.addSubInterface(
            self.pray_ui,
            FI.QUESTION,
            MainUIString.SUBPAGE_PRAY_NAVNAME,
            NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            self.settings_ui,
            FI.SETTING,
            MainUIString.SUBPAGE_SETTINGS_NAVNAME,
            NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(
            self.settings_basic_ui,
            FI.BRIGHTNESS,
            MainUIString.SUBSUBPAGE_SETTIING_BASIC_NAVNAME,
            parent=self.settings_ui,
        )
        self.addSubInterface(
            self.settings_audiovisual_ui,
            FI.MEDIA,
            MainUIString.SUBSUBPAGE_SETTIING_AUDIOVISUAL_NAVNAME,
            parent=self.settings_ui,
        )
        self.addSubInterface(
            self.settings_language_ui,
            FI.LANGUAGE,
            MainUIString.SUBSUBPAGE_SETTIING_LANGUAGE_NAVNAME,
            parent=self.settings_ui,
        )
        self.addSubInterface(
            self.information_ui,
            FI.INFO,
            MainUIString.SUBPAGE_INFORMATION_NAVNAME,
            NavigationItemPosition.BOTTOM,
        )

    def init_window(self):
        """初始化窗口设置"""

        # 初始化应用全局主题
        self._apply_theme()

        # 设置窗口大小
        self.resize(1080, 768)

        # 设置窗口标题
        self.setWindowTitle(BasicString.APP_MAINWINDOW_TITLE)

    def singal_connection(self):
        """信号连接函数"""

        # 连接设置子页面信号
        self.settings_ui.to_basic_card.clicked.connect(lambda: self.switchTo(self.settings_basic_ui))  # type: ignore
        self.settings_ui.to_audiovisual_card.clicked.connect(lambda: self.switchTo(self.settings_audiovisual_ui))  # type: ignore
        self.settings_ui.to_language_card.clicked.connect(lambda: self.switchTo(self.settings_language_ui))  # type: ignore

        # 连接视听孙页面主题更改信号
        self.cfg.DarkLight.valueChanged.connect(self._apply_theme)  # type: ignore

    def _apply_theme(self, mode: Union[Enum, None] = None):
        """设置应用全局主题"""
        from PySide2.QtGui import QIcon

        # 持久化写入配置文件
        qconfig.save()

        # 防止 mode 未被正确赋值
        if mode == None:
            mode = self.cfg.DarkLight.value

        # 变更图标主题
        theme_mode = get_theme_from_config()
        if theme_mode == "DARK":
            self.setWindowIcon(QIcon(AssetsPathTXT.APP_ICON_DARK_PATH))  # type: ignore
            # 变更文档阅读器图标主题
            if self.information_ui.docs_reader_ui != None:
                self.information_ui.docs_reader_ui.setWindowIcon(QIcon(AssetsPathTXT.APP_ICON_DARK_PATH))  # type: ignore
        else:
            self.setWindowIcon(QIcon(AssetsPathTXT.APP_ICON_LIGHT_PATH))  # type: ignore
            # 变更文档阅读器图标主题
            if self.information_ui.docs_reader_ui != None:
                self.information_ui.docs_reader_ui.setWindowIcon(QIcon(AssetsPathTXT.APP_ICON_LIGHT_PATH))  # type: ignore

        # 变更详细图主题
        app_detailed_image = (
            self.information_ui.information_board_card.app_detailed_image
        )
        apply_theme_from_config(app_detailed_image, mode)
        
    def _init_plugin_system(self):
        """初始化插件系统（扫描、加载、注册）"""
        from pathlib import Path
        from PySide2.QtWidgets import QWidget
        from plugin.scanner import PluginScanner
        from plugin.loader import PluginLoader
        from plugin.context import PluginContext
        
        # 1. 准备
        plugins_dir = Path(__file__).parent.parent.parent / "plugins"
        self.plugin_context = PluginContext(self, self.cfg)
        
        # 2. 扫描
        scanner = PluginScanner(plugins_dir)
        plugin_infos = scanner.scan()
        
        # 3. 加载
        loader = PluginLoader()
        loader.load_all(plugin_infos)
        
        # 4. 注册到主窗口（调用 register 获取 Widget）
        for info in plugin_infos:
            plugin_id = info.get("id")
            if not plugin_id:
                continue
            
            register_func = loader.get_register_func(plugin_id)
            if not register_func:
                continue
            
            try:
                # 调用插件的 register 函数，传入 context
                widget = register_func(self.plugin_context)
                
                # 如果插件返回了 QWidget，添加到导航栏
                if widget is not None and isinstance(widget, QWidget):
                    # 从 plugin.json 读取元数据
                    icon_name = info.get("icon", "APPLICATION")
                    plugin_name = info.get("name", "未命名插件")
                    parent_route = info.get("parent_route")  # 可能是 None
                    
                    # 使用 context 添加页面
                    self.plugin_context.add_page(
                        widget=widget,
                        icon=icon_name,
                        text=plugin_name,
                        position="bottom",
                        parent_route=parent_route
                    )
                    print(f"✅ 插件 {plugin_name} 已添加到导航栏")
                    
            except Exception as e:
                print(f"注册插件 {plugin_id} 时发生错误: {e}")
        
        # 保存 loader 供后续热重载使用
        self.plugin_loader = loader
