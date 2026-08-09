"""
孙页面:视听( 首选项 的子页面)的UI逻辑文件, 
引用时可作 SettAvUILogic / setting_audiovisual_ui_logic
"""

from ui.settings_ui.settings_audiovisual_ui import SettingsAudiovisualUI, sett_av_ui_cfg


class SettingsAudiovisualUILogic(SettingsAudiovisualUI):
    """孙页面:视听( 首选项 的子页面)的UI基础逻辑类,
    引用时可作 SettAvUILogic / setting_audiovisual_ui_logic"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cfg = sett_av_ui_cfg

        # 初始化信号连接函数
        self.singal_connection()

    def singal_connection(self):
        """信号连接函数"""

        pass
