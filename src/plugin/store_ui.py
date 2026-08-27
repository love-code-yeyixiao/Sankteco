"""
插件商店页面 - 显示已安装的插件列表
"""

from __future__ import annotations

from typing import Optional
from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import Qt, Signal
from qfluentwidgets import (
    FluentIcon,
    TitleLabel,
    SubtitleLabel,
    PrimaryPushButton,
    InfoBar,
    ScrollArea,
    MessageBox,
)

from .loader import PluginLoader
from .plugin_card_ui import PluginCard


class PluginStorePage(QWidget):
    """
    插件商店页面
    展示已安装的插件列表，并提供管理入口
    """

    # 定义信号
    # 启用/禁用请求：plugin_id, enable (True=启用, False=禁用)
    plugin_toggle_requested = Signal(str, bool)
    # 卸载请求：plugin_id
    plugin_uninstall_requested = Signal(str)

    def __init__(self, loader: PluginLoader, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.loader = loader
        self._cards: dict[str, PluginCard] = {}
        self._setup_ui()
        self._refresh_plugin_list()

    def _setup_ui(self):
        """初始化 UI 布局"""
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(20)

        # 标题区域
        self.title_label = TitleLabel("插件商店", self)
        self.title_label.setObjectName("store_title")
        self.main_layout.addWidget(self.title_label)

        # 副标题/统计信息
        self.subtitle_label = SubtitleLabel("已安装的插件", self)
        self.main_layout.addWidget(self.subtitle_label)

        # 滚动区域（用于容纳插件卡片列表）
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setObjectName("plugin_store_scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea{background: transparent; border: none}"
        )

        # 滚动区域的内容容器
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("plugin_store_scroll_content")
        self.scroll_content.setStyleSheet("QWidget{background: transparent}")

        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setContentsMargins(0, 10, 0, 20)
        self.scroll_layout.addStretch()  # 底部弹簧，让卡片靠上排列

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # 底部操作栏
        self._setup_action_bar()

    def _setup_action_bar(self):
        """底部操作栏：刷新按钮等"""
        from PySide2.QtWidgets import QHBoxLayout

        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.refresh_btn = PrimaryPushButton(FluentIcon.UPDATE, "刷新列表", self)
        self.refresh_btn.clicked.connect(self._refresh_plugin_list)  # type: ignore
        action_layout.addWidget(self.refresh_btn)

        self.main_layout.addLayout(action_layout)

    def _refresh_plugin_list(self):
        """刷新插件列表"""
        # 清除旧的卡片
        self._cards.clear()
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        plugin_ids = self.loader.get_all_plugin_ids()

        if not plugin_ids:
            empty_label = SubtitleLabel("暂无已安装的插件", self)
            empty_label.setAlignment(Qt.AlignCenter)  # type: ignore
            empty_label.setObjectName("empty_label")
            self.scroll_layout.insertWidget(0, empty_label)
            self.subtitle_label.setText("已安装的插件 (0)")
            return

        self.subtitle_label.setText(f"已安装的插件 ({len(plugin_ids)})")

        for plugin_id in plugin_ids:
            meta = self.loader.get_plugin_meta(plugin_id)
            # 关键：直接从 loader 读取启用状态
            is_enabled = self.loader.is_plugin_enabled(plugin_id)

            # 如果 loader 中不存在 enabled 字段，默认为 True（因为已加载到侧边栏）
            if is_enabled is None:
                is_enabled = True

            card = PluginCard(
                plugin_id=plugin_id,
                name=meta.get("name", plugin_id),
                version=meta.get("version", "1.0.0"),
                description=meta.get("description", ""),
                author=meta.get("author", "未知"),
                icon=meta.get("icon", "APPLICATION"),
                is_active=is_enabled,
                parent=self,
            )
            card.uninstall_requested.connect(self._on_uninstall_requested)  # type: ignore
            card.toggle_requested.connect(self._on_toggle_requested)  # type: ignore

            self._cards[plugin_id] = card
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)

        # 强制更新所有卡片状态
        self._sync_all_card_states()

    def _sync_all_card_states(self):
        """强制同步所有卡片状态（由主窗口在启动后调用）"""
        for plugin_id, card in self._cards.items():
            is_enabled = self.loader.is_plugin_enabled(plugin_id)
            if is_enabled is None:
                is_enabled = True
            card.set_active(is_enabled)

    def _on_toggle_requested(self, plugin_id: str, enable: bool):
        """
        处理启用/禁用切换请求
        只发送信号，由主窗口统一处理
        """
        self.plugin_toggle_requested.emit(plugin_id, enable)  # type: ignore

    def _on_uninstall_requested(self, plugin_id: str):
        """卸载请求 → 发送信号，由主窗口处理 UI 更新"""
        # 只发送信号，不直接操作主窗口
        self.plugin_uninstall_requested.emit(plugin_id)  # type: ignore
            
    def _update_card_state(self, plugin_id: str, is_active: bool):
        """更新卡片状态（由主窗口调用）"""
        card = self._cards.get(plugin_id)
        if card:
            card.set_active(is_active)
