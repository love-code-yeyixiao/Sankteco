"""
插件上下文：安全的API接口
"""
from typing import Optional, Any, Dict
from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QWidget
from qfluentwidgets import NavigationItemPosition, FluentIcon

# 这里使用字符串前向引用避免循环导入
class PluginContext(QObject):
    """
    插件安全上下文，只暴露必要的主程序功能
    """
    
    # 全局信号（插件可监听或发射）
    student_selected = Signal(str)  # 点名完成
    theme_changed = Signal(bool)    # 主题切换（True=暗色）
    
    def __init__(self, main_window: 'MainWindow', config: 'AppConfig'): # type: ignore
        super().__init__()
        self._main_window = main_window
        self._config = config
        self._plugin_data: Dict[str, Any] = {}  # 插件私有数据存储
    
    # ---------- 页面管理 API ----------
    def add_page(
        self, 
        widget: QWidget, 
        icon: str, 
        text: str, 
        position: str = "bottom", 
        parent_route: Optional[str] = None
    ):
        """
        添加插件页面到主窗口导航栏
        :param widget: 插件返回的 QWidget 实例
        :param icon: FluentIcon 名称（如 "MUSIC"）
        :param text: 导航栏显示文字
        :param position: "top" 或 "bottom"
        :param parent_route: 父页面的 objectName（孙页面时使用）
        """
        from qfluentwidgets import NavigationItemPosition
        
        # 确保 widget 有唯一的 objectName（用于路由）
        if not widget.objectName():
            widget.setObjectName(f"plugin_{id(widget)}")
        
        # 转换位置参数
        pos_map = {
            "top": NavigationItemPosition.TOP,
            "bottom": NavigationItemPosition.BOTTOM,
        }
        position_enum = pos_map.get(position, NavigationItemPosition.BOTTOM)
        
        # 尝试从 FluentIcon 获取图标
        try:
            icon_enum = getattr(FluentIcon, icon.upper(), FluentIcon.APPLICATION)
        except:
            icon_enum = FluentIcon.APPLICATION
        
        # 调用主窗口的 addSubInterface
        self._main_window.addSubInterface(
            widget, 
            icon_enum, 
            text, 
            position_enum, 
            parent_route
        )
    
    def switch_to(self, widget: QWidget):
        """切换到指定页面"""
        self._main_window.switchTo(widget)
    
    # ---------- 配置访问 API ----------
    def get_config_value(self, key: str):
        """安全地读取配置值（只读）"""
        # 例如：context.get_config_value("MusicPath")
        return getattr(self._config, key, None)
    
    # ---------- 日志 API ----------
    def log(self, message: str, level: str = "INFO"):
        """记录插件日志"""
        print(f"[Plugin] {level}: {message}")
    
    # ---------- 插件私有存储 ----------
    def set_data(self, key: str, value: Any):
        """存储插件私有数据（不会持久化）"""
        self._plugin_data[key] = value
    
    def get_data(self, key: str, default=None):
        """获取插件私有数据"""
        return self._plugin_data.get(key, default)
    