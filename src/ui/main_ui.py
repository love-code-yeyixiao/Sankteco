"""
主页面, 
此页面是本项目的主要GUI界面, 包含与各子页面的交互逻辑, 控件响应等, 
引用时可作 MainUI
"""

import asyncio
from enum import Enum
from typing import Union
from PySide2.QtWidgets import QWidget
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

        # 声明插件相关属性（告诉类型检查器这些属性存在）
        self.plugin_context = None
        self.plugin_loader = None

        # 运行导入子页面的asyncio程序
        asyncio.run(self.import_ui())

        # 初始化窗口设置
        self.init_window()

        # 插件系统集成(包含初始化侧边栏)
        self._init_plugin_system()

        # 初始化信号连接函数
        self.singal_connection()

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
            self.plugin_store_page,
            FI.APPLICATION,
            "插件商店",
            NavigationItemPosition.BOTTOM,
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

        if hasattr(self, "plugin_store_page") and self.plugin_store_page is not None:
            self.plugin_store_page.plugin_toggle_requested.connect(self._on_plugin_toggle)  # type: ignore
            self.plugin_store_page.plugin_uninstall_requested.connect(self._on_plugin_uninstall)  # type: ignore
            print("插件信号已连接")

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
        """初始化插件系统（使用 Stevedore）"""
        from plugin.loader import PluginLoader
        from plugin.context import PluginContext
        from plugin.store_ui import PluginStorePage

        # 1. 初始化上下文
        self.plugin_context = PluginContext(self, self.cfg)

        # 2. 加载所有插件
        loader = PluginLoader()
        loaded_count = loader.load_all_plugins()
        self.plugin_loader = loader

        if loaded_count == 0:
            print("没有发现任何插件")
            return
        
        # 3. 添加插件商店页面到导航栏并调用侧边栏加载
        self.plugin_store_page = PluginStorePage(loader, self)
        self.plugin_store_page.setObjectName("plugin_store_page")
        self.init_navigation()

        # 4. 注册每个插件到主窗口
        self.plugin_widgets = {}

        # 注意：loader.load_all_plugins() 会自动跳过 .disabled 的插件
    
        # 注册每个插件到主窗口（只注册已启用的）
        for plugin_id in loader.get_all_plugin_ids():
            # 只有加载成功的插件才会在 get_all_plugin_ids() 中
            # 被禁用的插件已被跳过
            register_func = loader.get_register_func(plugin_id)
            if not register_func:
                continue

            self.plugin_context.set_plugin_id(plugin_id)

            try:
                widget = register_func(self.plugin_context)
                if widget is not None and isinstance(widget, QWidget):
                    meta = loader.get_plugin_meta(plugin_id)
                    icon = meta.get("icon", "APPLICATION")
                    name = meta.get("name", plugin_id)

                    widget.setObjectName(f"plugin_page_{plugin_id}")
                    self.plugin_context.add_page(widget, icon, name)
                    self.plugin_widgets[plugin_id] = widget
                    print(f"插件 '{name}' 已添加到导航栏")
                else:
                    print(f"插件 {plugin_id} 未返回有效的 QWidget（可能为后台插件）")
            except Exception as e:
                print(f"注册插件 {plugin_id} 时发生错误: {e}")
                import traceback

                traceback.print_exc()

        # 启动后强制同步卡片状态
        self.plugin_store_page._sync_all_card_states()

    def remove_plugin_page(self, plugin_id: str) -> bool:
        """
        从导航栏和堆叠中移除插件页面
        :param plugin_id: 插件ID
        :return: True 表示移除成功
        """
        widget = self.plugin_widgets.pop(plugin_id, None)
        if not widget:
            # 尝试通过 objectName 查找
            target_name = f"plugin_page_{plugin_id}"
            for child in self.children():
                if hasattr(child, "objectName") and child.objectName() == target_name:
                    widget = child
                    break

        if not widget:
            print(f"未找到插件 {plugin_id} 的页面")
            return False

        # 方法1：使用 QFluentWidgets 的 removeInterface（推荐）
        if hasattr(self, "removeInterface"):
            self.removeInterface(widget, isDelete=True)
            print(f"已移除插件页面: {plugin_id}")
            return True

        # 方法2：手动移除（兼容旧版本）
        # 从堆叠中移除
        if hasattr(self, "stackedWidget"):
            stacked = self.stackedWidget
        else:
            # 查找 QStackedWidget
            from PySide2.QtWidgets import QStackedWidget

            stacked = None
            for child in self.children():
                if isinstance(child, QStackedWidget):
                    stacked = child
                    break

        if stacked:
            idx = stacked.indexOf(widget)
            if idx != -1:
                stacked.removeWidget(widget)
                widget.deleteLater()
                print(f"已从堆叠中移除插件页面: {plugin_id}")
                return True

        return False

    """def add_plugin_page(self, plugin_id: str, widget: QWidget, icon: str, name: str):
        ""
        添加插件页面到导航栏（由插件商店调用）
        ""
        widget.setObjectName(f"plugin_page_{plugin_id}")
        self.plugin_widgets[plugin_id] = widget

        from qfluentwidgets import NavigationItemPosition
        from qfluentwidgets import FluentIcon

        # 转换图标
        try:
            icon_enum = getattr(FluentIcon, icon.upper(), FluentIcon.APPLICATION)
        except:
            icon_enum = FluentIcon.APPLICATION

        # 添加到导航栏（默认放在底部）
        
        self.addSubInterface(widget, icon_enum, name, NavigationItemPosition.TOP)
        print(f"插件页面已添加: {name}")"""

    # ===== 信号槽：启用/禁用 =====
    def _on_plugin_toggle(self, plugin_id: str, enable: bool):
        """
        处理插件启用/禁用请求（由 PluginStorePage 发出）
        """
        meta = self.plugin_loader.get_plugin_meta(plugin_id)  # type: ignore
        plugin_name = meta.get("name", plugin_id)

        if enable:
            self._enable_plugin(plugin_id, plugin_name)
        else:
            self._disable_plugin(plugin_id, plugin_name)

    def _enable_plugin(self, plugin_id: str, plugin_name: str):
        """启用插件：加载并添加到导航栏"""
        try:
            register_func = self.plugin_loader.enable_plugin(plugin_id, self.plugin_context)  # type: ignore
            if not register_func:
                self._show_plugin_info(f"插件「{plugin_name}」加载失败", "error")
                self._update_card_state(plugin_id, False)
                return

            self.plugin_context.set_plugin_id(plugin_id)  # type: ignore
            widget = register_func(self.plugin_context)

            if widget is not None and isinstance(widget, QWidget):
                meta = self.plugin_loader.get_plugin_meta(plugin_id)  # type: ignore
                icon = meta.get("icon", "APPLICATION")
                name = meta.get("name", plugin_id)

                # 添加到导航栏
                widget.setObjectName(f"plugin_page_{plugin_id}")
                self.plugin_widgets[plugin_id] = widget  # 存储引用

                from qfluentwidgets import NavigationItemPosition, FluentIcon

                try:
                    icon_enum = getattr(
                        FluentIcon, icon.upper(), FluentIcon.APPLICATION
                    )
                except:
                    icon_enum = FluentIcon.APPLICATION

                self.addSubInterface(
                    widget, icon_enum, name, NavigationItemPosition.TOP
                )
                self._show_plugin_info(f"插件「{plugin_name}」已启用", "success")
            else:
                self._show_plugin_info(
                    f"插件「{plugin_name}」已启用（后台插件）", "info"
                )

        except Exception as e:
            self._show_plugin_info(f"启用插件出错: {e}", "error")
            import traceback

            traceback.print_exc()
            self._update_card_state(plugin_id, False)

    def _disable_plugin(self, plugin_id: str, plugin_name: str):
        """禁用插件：从导航栏移除"""
        try:
            # 从导航栏移除
            self._remove_plugin_page(plugin_id)

            # 从数据层禁用
            self.plugin_loader.disable_plugin(plugin_id)  # type: ignore

            self._show_plugin_info(f"插件「{plugin_name}」已禁用", "success")
        except Exception as e:
            self._show_plugin_info(f"禁用插件出错: {e}", "error")
            self._update_card_state(plugin_id, True)

    # ===== 信号槽：卸载 =====
    def _on_plugin_uninstall(self, plugin_id: str):
        """
        处理插件卸载请求（由 PluginStorePage 发出）
        """
        meta = self.plugin_loader.get_plugin_meta(plugin_id)  # type: ignore
        plugin_name = meta.get("name", plugin_id)

        # 弹出确认对话框
        from qfluentwidgets import MessageBox

        msg_box = MessageBox(
            title="确认卸载",
            content=f"确定要卸载插件「{plugin_name}」吗？\n\n卸载后将删除插件文件，此操作不可恢复。",
            parent=self,
        )
        # 注意：MessageBox 的 exec_ 返回值需要根据版本确认
        if not msg_box.exec_():
            return

        try:
            # 1. 从导航栏移除
            self._remove_plugin_page(plugin_id)

            # 2. 从数据层卸载（删除文件）
            success = self.plugin_loader.uninstall_plugin(plugin_id)  # type: ignore

            if success:
                self._show_plugin_info(f"插件「{plugin_name}」已卸载", "success")
                # 刷新插件商店列表
                self.plugin_store_page._refresh_plugin_list()
            else:
                self._show_plugin_info(f"无法卸载插件「{plugin_name}」", "error")
        except Exception as e:
            self._show_plugin_info(f"卸载插件出错: {e}", "error")
            import traceback

            traceback.print_exc()

    # ===== UI 辅助方法 =====
    def _remove_plugin_page(self, plugin_id: str):
        """从导航栏和堆叠中移除插件页面"""
        widget = self.plugin_widgets.pop(plugin_id, None)
        if not widget:
            # 尝试通过 objectName 查找
            target_name = f"plugin_page_{plugin_id}"
            for child in self.children():
                if hasattr(child, "objectName") and child.objectName() == target_name:
                    widget = child
                    break

        if not widget:
            print(f"未找到插件 {plugin_id} 的页面")
            return False

        # 方法1：尝试使用 removeInterface（QFluentWidgets 官方 API）
        if hasattr(self, "removeInterface"):
            self.removeInterface(widget, isDelete=True)
            print(f"已移除插件页面: {plugin_id}")
            return True

        # 方法2：手动移除（兼容方案）
        from PySide2.QtWidgets import QStackedWidget

        # 从堆叠中移除
        stacked = None
        for child in self.children():
            if isinstance(child, QStackedWidget):
                stacked = child
                break

        if stacked:
            idx = stacked.indexOf(widget)
            if idx != -1:
                stacked.removeWidget(widget)
                widget.deleteLater()
                print(f"已从堆叠中移除插件页面: {plugin_id}")
                return True

        return False

    def _update_card_state(self, plugin_id: str, is_active: bool):
        """更新插件商店中对应卡片的状态"""
        if hasattr(self, "plugin_store_page"):
            self.plugin_store_page._update_card_state(plugin_id, is_active)  # type: ignore

    def _show_plugin_info(self, message: str, level: str = "info"):
        """显示插件通知（使用 InfoBar）"""
        from qfluentwidgets import InfoBar

        if level == "success":
            InfoBar.success(title="提示", content=message, parent=self, duration=2000)
        elif level == "error":
            InfoBar.error(title="错误", content=message, parent=self, duration=3000)
        else:
            InfoBar.info(title="提示", content=message, parent=self, duration=2000)
