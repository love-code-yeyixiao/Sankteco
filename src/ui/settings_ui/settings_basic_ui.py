"""
孙页面:基本( 首选项 的子页面), 
此页面包含了本项目基本的可调整设置选项, 包含三个部分:名单, 普通抽选, 快速抽选, 
引用时可作 SettBasicUI / subsubpage_setting_basic
"""

from typing import Union, List
from PySide2.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTableWidgetItem,
    QHeaderView,
)
import qfluentwidgets as qfw
from qfluentwidgets import FluentIcon as FI
from app_const_var import AssetsPathTXT
from ui.ui_str import SettBasicUIString
from app_config import AppConfig


# 加载配置文件
sett_basic_ui_cfg = AppConfig()
qfw.qconfig.load(AssetsPathTXT.APP_CONFIG, sett_basic_ui_cfg)


class AskNewNamelistID(qfw.MessageBoxBase):
    """询问新名单的标识符, 继承自 对话框基类 MessageBoxBase,
    引用时可作 AskNewID"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 标题
        self.title_label = qfw.SubtitleLabel(
            SettBasicUIString.ASK_NEW_ID_MSG_TITLE, self
        )

        # 输入框
        self.input_lineedit = qfw.LineEdit(self)
        self.input_lineedit.setPlaceholderText(
            SettBasicUIString.ASK_NEW_ID_MSG_LINEEDIT_TEXT
        )
        self.input_lineedit.setClearButtonEnabled(True)

        # 添加控件进布局
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.input_lineedit)
        self.widget.setMinimumWidth(450)


class NowNamelistCard(qfw.SettingCard):
    """当前名单 卡片, 从属于 名单 部分,
    继承自 设置卡基类 SettingCard,
    引用时可作 NowNamelistCard"""

    def __init__(self, parent=None):
        super().__init__(
            FI.PEOPLE,
            SettBasicUIString.NOW_NAMELIST_CARD_TITLE,
            SettBasicUIString.NOW_NAMELIST_CARD_CONTEXT,
            parent,
        )

        # 下拉框
        self.now_namelist_card_list = qfw.ComboBox()
        self.now_namelist_card_list_item: List[str] = []
        self.now_namelist_card_list.addItems(self.now_namelist_card_list_item)

        # 调整布局边距、添加控件进布局
        self.hBoxLayout.setMargin(16)
        self.hBoxLayout.addWidget(self.now_namelist_card_list)


class NamelistSettingCard(qfw.SimpleCardWidget):
    """名单操作 卡片, 从属于 名单 部分,
    继承自 简单卡片组件 SimpleCardWidget,
    引用时可作 NamelistSettCard"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化布局
        self.hboxlayout = QHBoxLayout(self)

        # 初始化控件
        self.init_widgets()

        # 添加控件进布局
        self.hboxlayout.addStretch(1)
        self.hboxlayout.addWidget(self.refresh_namelist_button)
        self.hboxlayout.addWidget(self.add_new_namelist_button)
        self.hboxlayout.addWidget(self.rename_namelist_button)
        self.hboxlayout.addWidget(self.del_namelist_button)
        self.hboxlayout.addWidget(self.import_namelist_button)
        self.hboxlayout.addWidget(self.export_namelist_button)
        self.hboxlayout.addStretch(1)

    def init_widgets(self):
        """初始化控件"""

        # 刷新名单
        self.refresh_namelist_button = qfw.PushButton(
            FI.SYNC,
            SettBasicUIString.REFRESH_NAMELIST_BUTTON_TEXT,
        )

        # 新建名单
        self.add_new_namelist_button = qfw.PushButton(
            FI.ADD,
            SettBasicUIString.ADD_NEW_NAMELIST_BUTTON_TEXT,
        )

        # 重命名名单
        self.rename_namelist_button = qfw.PushButton(
            FI.PENCIL_INK,
            SettBasicUIString.RENAME_NAMELIST_BUTTON_TEXT,
        )

        # 删除名单
        self.del_namelist_button = qfw.PushButton(
            FI.DELETE,
            SettBasicUIString.DEL_NAMELIST_BUTTON_TEXT,
        )

        # 导入名单
        self.import_namelist_button = qfw.PrimaryPushButton(
            FI.SEARCH,
            SettBasicUIString.IMPORT_NAMELIST_BUTTON_TEXT,
        )

        # 导出名单
        self.export_namelist_button = qfw.PrimaryPushButton(
            FI.SAVE_AS,
            SettBasicUIString.EXPORT_NAMELIST_BUTTON_TEXT,
        )


class NameTableWidget(QWidget):
    """名单表格, 从属于 名单 部分,
    引用时可作 NameTableWidget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化控件
        self.init_widgets()

        # 初始化布局
        self.hboxlayout = QHBoxLayout(self)

        # 添加控件进布局
        self.hboxlayout.addWidget(self.name_table_widget)

    def init_widgets(self):
        """初始化控件"""

        # 初始化表格、起用边框、设置圆角、禁止换行、右键响应
        self.name_table_widget = qfw.TableWidget(self)
        self.name_table_widget.setBorderVisible(True)
        self.name_table_widget.setBorderRadius(8)
        self.name_table_widget.setWordWrap(False)
        self.name_table_widget.setSelectRightClickedRow(True)

        # 设置列数与初始行数
        self.name_table_widget_row = 0
        self.name_table_widget_column = 6
        self.name_table_widget.setRowCount(self.name_table_widget_row)
        self.name_table_widget.setColumnCount(self.name_table_widget_column)

        # 设置水平表头并隐藏垂直表头
        self.name_table_widget.setHorizontalHeaderLabels(
            [
                SettBasicUIString.NAMETABLE_HEADER_LABEL_EXIST,
                SettBasicUIString.NAMETABLE_HEADER_LABEL_NO,
                SettBasicUIString.NAMETABLE_HEADER_LABEL_NAME,
                SettBasicUIString.NAMETABLE_HEADER_LABEL_GENDER,
                SettBasicUIString.NAMETABLE_HEADER_LABEL_GROUP,
                SettBasicUIString.NAMETABLE_HEADER_LABEL_TIP,
            ]
        )
        self.name_table_widget.verticalHeader().hide()

        # 表格数据
        self.name_table_widget_data = []

    def add_item(
        self,
        no: Union[str, int],
        name: str,
        gender: str,
        group: Union[str, int],
        tip: str,
        is_exist: bool = True,
    ):
        """添加单项数据"""

        # 判断数据并转为文本
        exist = "True" if is_exist else "False"
        no = str(no)
        group = str(group)

        self.name_table_widget_row += 1
        self.name_table_widget_data.append([exist, no, name, gender, group, tip])

        self.refresh_items()

    def refresh_items(self):
        """刷新表格数据"""

        # 先清除表格行数以清空数据, 再设置新行数
        self.name_table_widget.setRowCount(0)
        self.name_table_widget.setRowCount(self.name_table_widget_row)

        # 添加数据到表格
        for i, data in enumerate(self.name_table_widget_data):
            for j in range(self.name_table_widget_column):
                self.name_table_widget.setItem(i, j, QTableWidgetItem(data[j]))

        self.refresh_table_column_width()

    def refresh_table_column_width(self):
        """刷新表格列宽"""

        # 获取表格列宽模式
        header = self.name_table_widget.horizontalHeader()

        # 设置所有列先根据内容调整宽度
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        # 开启 "拉伸最后一列" 功能
        header.setStretchLastSection(True)

        # 重新计算第3列
        self.name_table_widget.resizeColumnToContents(2)


class NamelistSettingGroup(QWidget):
    """名单 部分, 继承自 QWidget,
    引用时可作 NamelistSettGr"""

    def __init__(self):
        super().__init__()

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)

        # 初始化各控件
        self.now_namelist_card = NowNamelistCard(self)
        self.namelist_setting_card = NamelistSettingCard(self)
        self.name_table_widget = NameTableWidget(self)

        # 添加控件进布局
        self.vboxlayout.addWidget(self.now_namelist_card)
        self.vboxlayout.addWidget(self.namelist_setting_card)
        self.vboxlayout.addWidget(self.name_table_widget)
        self.setLayout(self.vboxlayout)


class BasicChooseSettingGroup(QWidget):
    """普通抽选 部分, 继承自 QWidget,
    引用时可作 BChooseSettGr"""

    def __init__(self):
        super().__init__()

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)

        # 动画精美度
        self.carton_beauty_level_card = qfw.ComboBoxSettingCard(
            sett_basic_ui_cfg.CartonBeautyLevel,
            FI.CLOUD,
            SettBasicUIString.CARTON_BEAUTY_LEVEL_CARD_TITLE,
            SettBasicUIString.CARTON_BEAUTY_LEVEL_CARD_CONTEXT,
            [
                SettBasicUIString.CARTON_BEAUTY_LEVEL_CARD_TEXTS_AMAZED,
                SettBasicUIString.CARTON_BEAUTY_LEVEL_CARD_TEXTS_BEAUTY,
                SettBasicUIString.CARTON_BEAUTY_LEVEL_CARD_TEXTS_BASIC,
                SettBasicUIString.CARTON_BEAUTY_LEVEL_CARD_TEXTS_FAST,
            ],
        )

        # 设置布局
        self.vboxlayout.addWidget(self.carton_beauty_level_card)
        self.setLayout(self.vboxlayout)


class FastChooseSettingGroup(QWidget):
    """快速抽选 部分, 继承自 QWidget,
    引用时可作 FChooseSettGr"""

    def __init__(self):
        super().__init__()

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)

        # 结果推送
        self.show_result_way = qfw.OptionsSettingCard(
            sett_basic_ui_cfg.ShowResultWay,
            FI.INFO,
            SettBasicUIString.SHOW_RESULT_WAY_CARD_TITLE,
            SettBasicUIString.SHOW_RESULT_WAY_CARD_CONTEXT,
            [
                SettBasicUIString.SHOW_RESULT_WAY_CARD_TEXTS_CI,
                SettBasicUIString.SHOW_RESULT_WAY_CARD_TEXTS_CW,
                SettBasicUIString.SHOW_RESULT_WAY_CARD_TEXTS_DIALOG,
            ],
        )

        # 设置布局
        self.vboxlayout.addWidget(self.show_result_way)
        self.setLayout(self.vboxlayout)


class SettingsBasicUI(QFrame):
    """孙页面:基本( 首选项 的子页面)的基础UI类,
    此页面包含了本项目基本的可调整设置选项, 包含三个部分:名单, 普通抽选, 快速抽选,
    引用时可作 SettBasicUI / settings_basic"""

    def __init__(self, parent=None):
        super().__init__(parent)

        from PySide2.QtCore import Qt, QMargins
        from PySide2.QtWidgets import QStackedWidget

        # 初始化顶部导航栏与多页面, 初始化布局
        self.pivot = qfw.Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vboxlayout = QVBoxLayout(self)

        # 添加各项的卡片组
        self.namelist_interface = NamelistSettingGroup()
        self.basic_choose_interface = BasicChooseSettingGroup()
        self.fast_choose_interface = FastChooseSettingGroup()

        # 添加标签页
        self.add_sub_interface(
            self.namelist_interface,
            SettBasicUIString.NAMELIST_SETT_GR_OBJNAME,
            SettBasicUIString.NAMELIST_SETT_GR_NAVNAME,
        )
        self.add_sub_interface(
            self.basic_choose_interface,
            SettBasicUIString.B_CHOOSE_SETT_GR_OBJNAME,
            SettBasicUIString.B_CHOOSE_SETT_GR_NAVNAME,
        )
        self.add_sub_interface(
            self.fast_choose_interface,
            SettBasicUIString.F_CHOOSE_SETT_GR_OBJNAME,
            SettBasicUIString.F_CHOOSE_SETT_GR_NAVNAME,
        )

        # 连接信号并初始化当前标签页
        self.stackedWidget.currentChanged.connect(self.on_current_index_changed)
        self.stackedWidget.setCurrentWidget(self.namelist_interface)
        self.pivot.setCurrentItem(self.namelist_interface.objectName())

        # 调整布局
        self.vboxlayout.setContentsMargins(QMargins(30, 30, 30, 30))
        self.vboxlayout.addWidget(self.pivot)
        self.vboxlayout.setAlignment(self.pivot, Qt.AlignCenter)
        self.vboxlayout.addWidget(self.stackedWidget)

    def add_sub_interface(self, widget: QWidget, objectName: str, text: str):
        """添加子页面"""

        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)

        # 使用全局唯一的 objectName 作为路由键
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
        )

    def on_current_index_changed(self, index):
        """将多页面的切换信号连接到顶部导航栏显示"""

        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
