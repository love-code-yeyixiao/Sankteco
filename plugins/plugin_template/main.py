"""
插件入口模板文件
"""

def register(context):
    """
    插件注册函数（必须实现）
    :param context: 主程序传递的 PluginContext 对象
    :return: 返回一个 QWidget 实例（作为页面），或者返回 None（纯后台插件）
    """
    from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout
    from PySide2.QtCore import Qt

    # 示例：创建一个简单的页面
    widget = QWidget()
    widget.setObjectName("demo_plugin_page")  # 重要：路由键必须唯一
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Hello from Plugin!"))

    # 可以在这里连接 context 提供的信号
    # context.student_selected.connect(lambda name: print(f"点名了: {name}"))

    return widget

# 可选：插件卸载前的清理函数（约定名称，非必须）
def unregister(context):
    print("插件正在卸载...")