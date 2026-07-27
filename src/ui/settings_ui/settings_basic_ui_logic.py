"""
孙页面:基本( 首选项 的子页面)的UI逻辑文件, 
引用时可作 SettBasicUILogic / settings_basic_ui_logic
"""

from pathlib import Path
import tablib
from PySide2.QtWidgets import QFileDialog
from ui.settings_ui.settings_basic_ui import (
    AskNewNamelistID,
    SettingsBasicUI,
    sett_basic_ui_cfg,
)
from logic.add_import_export_namelist import AIENamelist
from app_const_var import LogicFilesString, AssetsPathTXT


class SettingsBasicUILogic(SettingsBasicUI):
    """孙页面:基本( 首选项 的子页面)的UI基础逻辑类,
    引用时可作 SettBasicUILogic / subsubpage_setting_basic_ui_logic"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cfg = sett_basic_ui_cfg

        # 初始化信号连接函数
        self.singal_connection()

        # 初始化读取名单列表
        self.load_namelists_list()

    def load_namelists_list(self):
        ui = self.namelist_interface.now_namelist_card

        # 匹配 Sankteco 名单文件
        namelist_folder_path = Path(AssetsPathTXT.APP_NAMELISTS_FOLDER).glob("*.json")
        namelist_names_list = [p.name for p in namelist_folder_path]

        # 添加名单列表到下拉框
        for i in namelist_names_list:
            ui.now_namelist_card_list_item.append(i)
        ui.now_namelist_card_list.addItems(ui.now_namelist_card_list_item)

        # 默认选中第一项 (如果存在), 会触发 currentIndexChanged 信号 -> 自动加载
        if ui.now_namelist_card_list.count() > 0:
            ui.now_namelist_card_list.setCurrentIndex(0)

    def singal_connection(self):
        """信号连接函数"""

        now_namelist_card_list = (
            self.namelist_interface.now_namelist_card.now_namelist_card_list
        )
        namelist_setting_card = self.namelist_interface.namelist_setting_card

        # 当前名单下拉框
        now_namelist_card_list.currentIndexChanged.connect(  # type: ignore
            lambda: self.load_namelist_from_json(
                f"{AssetsPathTXT.APP_NAMELISTS_FOLDER}{now_namelist_card_list.currentText()}"
            )
        )

        # 刷新名单
        namelist_setting_card.refresh_namelist_button.clicked.connect(
            self.namelist_interface.name_table_widget.refresh_items
        )

        # 新建名单
        namelist_setting_card.add_new_namelist_button.clicked.connect(
            self.add_new_namelist
        )

        # 导入名单
        namelist_setting_card.import_namelist_button.clicked.connect(
            self.import_namelist
        )

    def add_new_namelist(self):
        """新建名单"""

        new_namelist_ID = None
        ui = self.namelist_interface.now_namelist_card

        # 调用新名单标识符对话框
        ask_ID_msg = AskNewNamelistID(self)
        if ask_ID_msg.exec_():
            new_namelist_ID = ask_ID_msg.input_lineedit.text()

            # 调用 AIENamelist.add_namelist 创建新名单
            new_namelist_path, new_namelist_data = AIENamelist.add_namelist(
                new_namelist_ID
            )

            # 添加名单标识符到 当前名单 下拉框
            ui.now_namelist_card_list_item.append(new_namelist_path)
            ui.now_namelist_card_list.clear()
            ui.now_namelist_card_list.addItems(ui.now_namelist_card_list_item)

            # 选中新添加的名单 (最后一项)
            ui.now_namelist_card_list.setCurrentIndex(ui.now_namelist_card_list.count() - 1)

            # 加载名单
            self.load_namelist_from_dataset(new_namelist_data)

    def import_namelist(self):
        """导入名单"""

        ui = self.namelist_interface.now_namelist_card

        # 创建对话框实例
        import_namelist_dialog = QFileDialog(self)
        import_namelist_dialog.setWindowTitle("选择一个名单文件")

        # 设置文件过滤器
        import_namelist_dialog.setNameFilters(
            [
                "文本文件 (*.txt)",
                "JSON (*.json)",
                "逗号分隔符文件 (*.csv)",
                "Excel电子表格文档 (*.xlsx *.xls)",
            ]
        )

        # 设置为 "打开" 模式
        import_namelist_dialog.setAcceptMode(QFileDialog.AcceptOpen)

        # 显示对话框并获取名单路径
        if import_namelist_dialog.exec_():
            selected_files = import_namelist_dialog.selectedFiles()
            if selected_files:
                namelist_path = selected_files[0]
                dataset, saved_path = AIENamelist.import_namelist(namelist_path)
                if dataset is not None:
                    # 类型保护
                    assert saved_path is not None

                    ui.now_namelist_card_list_item.append(Path(saved_path).name)
                    ui.now_namelist_card_list.clear()
                    ui.now_namelist_card_list.addItems(ui.now_namelist_card_list_item)
                    # 选中最后一项 (新导入的)
                    ui.now_namelist_card_list.setCurrentIndex(
                        ui.now_namelist_card_list.count() - 1
                    )
                    self.load_namelist_from_dataset(dataset)
                else:
                    print("导入失败：文件格式不支持或无有效表头")

    def load_namelist_from_dataset(self, namelist_data: tablib.Dataset):
        """从 tablib.Dataset 中加载名单"""

        ui = self.namelist_interface.name_table_widget

        # 先清空表格内容
        ui.name_table_widget.setRowCount(0)
        ui.name_table_widget_row = 0
        ui.name_table_widget_data = []

        # 循环获取并添加值进入UI
        namelist_names_num = len(
            namelist_data[LogicFilesString.AIENAMELIST_HEADER_EXIST]
        )
        ui.name_table_widget.setRowCount(namelist_names_num)
        for i in range(namelist_names_num):
            data_i = namelist_data[i]
            ui.add_item(
                data_i[1],
                data_i[2],
                data_i[3],
                data_i[4],
                data_i[5],
                data_i[0],
            )

    def load_namelist_from_json(self, namelist_path: str):
        """从 JSON 文件中加载名单"""
        ui = self.namelist_interface.name_table_widget

        # 先清空表格
        ui.name_table_widget.setRowCount(0)
        ui.name_table_widget_row = 0
        ui.name_table_widget_data = []

        # 导入数据，解包获得 Dataset
        dataset, _ = AIENamelist.import_namelist(namelist_path)
        if dataset is not None:
            try:
                # 获取有效行数（假设列 EXIST 存在）
                row_count = len(dataset[LogicFilesString.AIENAMELIST_HEADER_EXIST])
                ui.name_table_widget.setRowCount(row_count)
                for i in range(row_count):
                    row_data = dataset[i]
                    ui.add_item(
                        row_data[1],  # 编号
                        row_data[2],  # 姓名
                        row_data[3],  # 性别
                        row_data[4],  # 年龄
                        row_data[5],  # 备注
                        row_data[0],  # 是否启用
                    )
            except Exception as e:
                print(f"加载名单数据出错: {e}")
        else:
            print(f"无法加载文件: {namelist_path}")
