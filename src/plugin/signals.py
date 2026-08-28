# src/plugin/signals.py

from PySide2.QtCore import QObject, Signal


class PluginSignals(QObject):
    """全局插件信号"""

    plugin_installed = Signal(str)
    plugin_uninstalled = Signal(str)
    plugin_enabled = Signal(str)
    plugin_disabled = Signal(str)
    plugin_updated = Signal(str)

    refresh_store_requested = Signal()

    install_progress = Signal(int)


plugin_signals = PluginSignals()
