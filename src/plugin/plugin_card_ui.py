"""
单个插件展示卡片
基于 QFluentWidgets 的 SettingCard 实现
"""

from __future__ import annotations

from typing import Optional
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget
from qfluentwidgets import (
    SettingCard,
    FluentIcon,
    PushButton,
    SwitchButton,
    ToolTipFilter,
)


class PluginCard(SettingCard):
    """
    插件信息卡片
    显示插件图标、名称、版本、描述，并提供启用/卸载操作
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
        # 尝试获取图标
        try:
            icon_enum = getattr(FluentIcon, icon.upper(), FluentIcon.APPLICATION)
        except:
            icon_enum = FluentIcon.APPLICATION

        super().__init__(icon_enum, name, description, parent)

        self.plugin_id = plugin_id
        self.is_active = is_active

        # 版本标签（显示在标题右侧）
        self.version_label = PushButton(f"v{version}", self)
        self.version_label.setEnabled(False)
        self.version_label.setFixedWidth(80)

        # 作者标签
        self.author_label = PushButton(author, self)
        self.author_label.setEnabled(False)
        self.author_label.setFixedWidth(100)

        # 启用/禁用开关
        self.toggle_btn = SwitchButton(self)
        self.toggle_btn.setChecked(is_active)
        self.toggle_btn.checkedChanged.connect(self._on_toggle)  # type: ignore

        # 卸载按钮
        self.uninstall_btn = PushButton(FluentIcon.DELETE, "卸载", self)
        self.uninstall_btn.clicked.connect(self._on_uninstall)  # type: ignore

        # 将控件添加到卡片的布局中
        self.hBoxLayout.addWidget(self.version_label)
        self.hBoxLayout.addWidget(self.author_label)
        self.hBoxLayout.addWidget(self.toggle_btn)
        self.hBoxLayout.addWidget(self.uninstall_btn)
        self.hBoxLayout.addSpacing(16)

        # 添加工具提示
        self.installEventFilter(ToolTipFilter(self))

    def _on_toggle(self, checked: bool):
        """开关切换时触发"""
        self.is_active = checked
        self.toggle_requested.emit(self.plugin_id, checked)  # type: ignore

    def _on_uninstall(self):
        """卸载按钮点击时触发"""
        self.uninstall_requested.emit(self.plugin_id)  # type: ignore

    def set_active(self, active: bool):
        """外部设置激活状态"""
        self.is_active = active
        self.toggle_btn.setChecked(active)
