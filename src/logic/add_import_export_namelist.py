"""
添加与保存名单的逻辑文件,
包含Sankteco风格名单文件的创建接口、导入及导出名单文件的接口,
引用时可作 AIENamelist / add_import_export_namelist
"""

from pathlib import Path
from PySide2.QtWidgets import QFileDialog
import tablib


class AIENamelist:
    """添加与保存名单的逻辑文件类,
    包含Sankteco风格名单文件的创建接口、导入及导出名单文件的接口,
    引用时可作 AIENamelist / add_import_export_namelist"""

    @staticmethod
    def add_namelist(namelist_id: str):
        """添加新名单"""

        # 创建一个空的 Dataset，并指定表头(headers)
        namelist_data = tablib.Dataset(
            headers=["存在?", "学号", "姓名", "性别", "小组", "标签"]
        )

        # 用 .append() 添加初始行(数据需与表头顺序对应)
        namelist_data.append([True, 1, "", "", "", ""])

        # 导出为 JSON 格式
        with open(f"namelists/{namelist_id}.json", "w", encoding='utf-8') as f:
            f.write(namelist_data.export('json'))

        return f"namelists/{namelist_id}.json"

    
