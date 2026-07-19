"""
孙页面:基本( 首选项 的子页面)的UI逻辑文件, 
引用时可作 SettBasicUILogic / subsubpage_setting_basic_ui_logic
"""

from os import listdir
import tablib
from ui.settings_ui.settings_basic_ui import (
    AskNewNamelistID,
    SettingsBasicUI,
    sett_basic_ui_cfg,
)
from logic.add_import_export_namelist import AIENamelist


class SettingsBasicUILogic(SettingsBasicUI):
    """孙页面:基本( 首选项 的子页面)的UI基础逻辑类,
    引用时可作 SettBasicUILogic / subsubpage_setting_basic_ui_logic"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cfg = sett_basic_ui_cfg

        # 初始化读取名单列表
        # TODO: 获取指定目录下的指定文件名，要求后缀为指定格式，输出为列表

        # 初始化信号连接函数
        self.singal_connection()

    def singal_connection(self):
        """信号连接函数"""

        # 刷新名单
        self.namelist_interface.namelist_setting_card.refresh_namelist_button.clicked.connect(
            self.namelist_interface.name_table_widget.refresh_items
        )

        # 新建名单
        self.namelist_interface.namelist_setting_card.add_new_namelist_button.clicked.connect(
            self.add_new_namelist
        )

    def add_new_namelist(self):
        """新建名单"""

        new_namelist_ID = None
        ui = self.namelist_interface.now_namelist_card

        # 调用新名单标识符对话框
        ask_ID_msg = AskNewNamelistID(self)
        if ask_ID_msg.exec_():
            new_namelist_ID = ask_ID_msg.input_lineedit.text()
        else:
            print("用户拒绝了操作")

        # 调用 AIENamelist.add_namelist 创建新名单
        if new_namelist_ID != None:
            new_namelist_path = AIENamelist.add_namelist(new_namelist_ID)

            # 添加名单标识符到 当前名单 下拉框
            ui.now_namelist_card_list_item.append(new_namelist_ID)
            ui.now_namelist_card_list.addItems(ui.now_namelist_card_list_item)

            # 加载名单
            self.load_namelist(new_namelist_path)

    def load_namelist(self, namelist_path: str):
        """加载名单"""

        # 读取名单文件
        with open(namelist_path, "r", encoding="utf-8") as f:
            namelist_data = list(tablib.Dataset().load(f).export("json"))
            print(namelist_data)

        # 循环获取并添加值进入UI
        for i in namelist_data:
            self.namelist_interface.name_table_widget.add_item(
                i["学号"], i["姓名"], i["性别"], i["小组"], i["标签"], i["存在?"] # FIXME
            )
