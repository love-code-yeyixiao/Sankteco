"""
插件卡片组件

提供两种卡片：
1. PluginCard - 已安装插件的管理卡片
2. OnlinePluginCard - 在线插件的安装卡片
"""

from __future__ import annotations

from typing import Optional, Dict
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel
from qfluentwidgets import (
    SettingCard,
    FluentIcon,
    PushButton,
    SwitchButton,
    ToolTipFilter,
    PrimaryPushButton,
)


class PluginCard(SettingCard):
    """
    已安装插件信息卡片
    参考 ClassIsland 风格，信息层级清晰
    """

    uninstall_requested = Signal(str)  # plugin_id
    toggle_requested = Signal(str, bool)  # plugin_id, enable

    def __init__(
        self,
        plugin_id: str,
        name: str,
        version: str,
        description: str,
        author: str,
        icon: str,
        is_active: bool = True,
        parent: Optional[QWidget] = None,
    ):
        # 获取图标
        try:
            icon_enum = getattr(FluentIcon, icon.upper(), FluentIcon.APPLICATION)
        except:
            icon_enum = FluentIcon.APPLICATION

        super().__init__(icon_enum, name, description, parent)

        self.plugin_id = plugin_id
        self.is_active = is_active

        # ---- 右侧操作区 ----
        # 使用水平布局容纳多个控件
        self._action_layout = QHBoxLayout()
        self._action_layout.setSpacing(8)
        self._action_layout.setContentsMargins(0, 0, 0, 0)

        # 版本标签（小字，灰色）
        self.version_label = QLabel(f"v{version}")
        self.version_label.setStyleSheet(
            "QLabel{color: rgba(128, 128, 128, 0.8); font-size: 12px;}"
        )
        self._action_layout.addWidget(self.version_label)

        # 作者标签（小字，灰色）
        self.author_label = QLabel(author)
        self.author_label.setStyleSheet(
            "QLabel{color: rgba(128, 128, 128, 0.6); font-size: 12px;}"
        )
        self._action_layout.addWidget(self.author_label)

        # 分隔线（视觉占位）
        spacer = QLabel("|")
        spacer.setStyleSheet(
            "QLabel{color: rgba(128, 128, 128, 0.3); font-size: 12px;}"
        )
        self._action_layout.addWidget(spacer)

        # 启用/禁用开关
        self.toggle_btn = SwitchButton(self)
        self.toggle_btn.setChecked(is_active)
        self.toggle_btn.checkedChanged.connect(self._on_toggle)
        self._action_layout.addWidget(self.toggle_btn)

        # 卸载按钮
        self.uninstall_btn = PushButton(FluentIcon.DELETE, "卸载", self)
        self.uninstall_btn.setFixedWidth(70)
        self.uninstall_btn.clicked.connect(self._on_uninstall)
        self._action_layout.addWidget(self.uninstall_btn)

        # 将操作布局添加到卡片的水平布局中
        self.hBoxLayout.addLayout(self._action_layout)
        self.hBoxLayout.addSpacing(16)

        # 工具提示
        self.installEventFilter(ToolTipFilter(self))

    def _on_toggle(self, checked: bool) -> None:
        """开关切换时触发"""
        self.is_active = checked
        self.toggle_requested.emit(self.plugin_id, checked)

    def _on_uninstall(self) -> None:
        """卸载按钮点击时触发"""
        self.uninstall_requested.emit(self.plugin_id)

    def set_active(self, active: bool) -> None:
        """外部设置激活状态"""
        self.is_active = active
        self.toggle_btn.setChecked(active)


class OnlinePluginCard(SettingCard):
    """
    在线插件信息卡片
    显示远程插件信息，提供安装/更新操作
    """

    install_requested = Signal(str)  # plugin_id
    update_requested = Signal(str)  # plugin_id

    def __init__(
        self,
        plugin_info: Dict,
        is_installed: bool,
        has_update: bool,
        parent: Optional[QWidget] = None,
    ):
        plugin_id = plugin_info.get("id", "")
        name = plugin_info.get("name", "未命名插件")
        description = plugin_info.get("description", "")
        author = plugin_info.get("author", "未知")
        icon = plugin_info.get("icon", "APPLICATION")
        version = plugin_info.get("version", "1.0.0")

        try:
            icon_enum = getattr(FluentIcon, icon.upper(), FluentIcon.APPLICATION)
        except:
            icon_enum = FluentIcon.APPLICATION

        super().__init__(icon_enum, name, description, parent)

        self.plugin_id = plugin_id
        self.plugin_info = plugin_info
        self.is_installed = is_installed
        self.has_update = has_update

        # ---- 右侧操作区 ----
        self._action_layout = QHBoxLayout()
        self._action_layout.setSpacing(8)
        self._action_layout.setContentsMargins(0, 0, 0, 0)

        # 版本标签
        self.version_label = QLabel(f"v{version}")
        self.version_label.setStyleSheet(
            "QLabel{color: rgba(128, 128, 128, 0.8); font-size: 12px;}"
        )
        self._action_layout.addWidget(self.version_label)

        # 作者标签
        self.author_label = QLabel(author)
        self.author_label.setStyleSheet(
            "QLabel{color: rgba(128, 128, 128, 0.6); font-size: 12px;}"
        )
        self._action_layout.addWidget(self.author_label)

        # 分隔线
        spacer = QLabel("|")
        spacer.setStyleSheet(
            "QLabel{color: rgba(128, 128, 128, 0.3); font-size: 12px;}"
        )
        self._action_layout.addWidget(spacer)

        # 操作按钮
        if has_update:
            self.action_btn = PrimaryPushButton("更新", self)
            self.action_btn.setFixedWidth(70)
            self.action_btn.clicked.connect(self._on_update)
        elif is_installed:
            self.action_btn = PushButton("已安装", self)
            self.action_btn.setFixedWidth(70)
            self.action_btn.setEnabled(False)
        else:
            self.action_btn = PrimaryPushButton("安装", self)
            self.action_btn.setFixedWidth(70)
            self.action_btn.clicked.connect(self._on_install)

        self._action_layout.addWidget(self.action_btn)

        # 添加到卡片
        self.hBoxLayout.addLayout(self._action_layout)
        self.hBoxLayout.addSpacing(16)

        self.installEventFilter(ToolTipFilter(self))

    def _on_install(self) -> None:
        """安装按钮点击时触发"""
        self.install_requested.emit(self.plugin_id)

    def _on_update(self) -> None:
        """更新按钮点击时触发"""
        self.update_requested.emit(self.plugin_id)
