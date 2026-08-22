# src/plugin/scanner.py
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# 配置一个简单的日志记录器（后续可替换为 QFluentWidgets 的日志组件）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginScanner")

class PluginScanner:
    """
    插件扫描器：负责扫描指定目录下的插件文件夹，读取并验证 plugin.json
    """

    # 定义 plugin.json 中必须存在的字段
    REQUIRED_FIELDS = {"id", "name", "version", "entry"}

    def __init__(self, plugins_root: Path):
        """
        :param plugins_root: 插件根目录的 Path 对象，例如 Path("plugins/")
        """
        self.plugins_root = plugins_root
        self._valid_plugins: List[Dict] = []

    def scan(self) -> List[Dict]:
        """
        执行扫描操作
        :return: 每个合法插件的信息字典列表
        """
        self._valid_plugins = []

        if not self.plugins_root.exists():
            logger.warning(f"插件目录不存在: {self.plugins_root}")
            return []

        for plugin_dir in self.plugins_root.iterdir():
            if not plugin_dir.is_dir():
                continue  # 跳过文件

            # 处理文件夹名字带有下划线或点的情况（如 __pycache__）
            if plugin_dir.name.startswith(".") or plugin_dir.name.startswith("__"):
                continue

            meta_path = plugin_dir / "plugin.json"
            if not meta_path.exists():
                logger.debug(f"跳过 {plugin_dir.name}：没有 plugin.json")
                continue

            # 尝试解析并验证 JSON
            plugin_info = self._parse_and_validate(meta_path, plugin_dir)
            if plugin_info:
                self._valid_plugins.append(plugin_info)

        # 打印摘要信息
        if self._valid_plugins:
            logger.info(f"发现 {len(self._valid_plugins)} 个有效插件：")
            for p in self._valid_plugins:
                logger.info(f"  - {p['name']} (v{p['version']}) id: {p['id']}")
        else:
            logger.info("未发现任何有效插件")

        return self._valid_plugins

    def _parse_and_validate(self, meta_path: Path, plugin_dir: Path) -> Optional[Dict]:
        """
        解析单个 plugin.json 文件并验证字段完整性
        :return: 如果验证通过，返回包含插件信息的 dict；否则返回 None
        """
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 检查必要字段
            missing = self.REQUIRED_FIELDS - set(data.keys())
            if missing:
                logger.warning(
                    f"插件 {plugin_dir.name} 缺少必要字段: {missing}"
                )
                return None

            # 额外类型校验（可选）
            if not isinstance(data.get("id"), str) or not data["id"].strip():
                logger.warning(f"插件 {plugin_dir.name} 的 'id' 无效")
                return None

            # 记录插件所在的绝对路径，方便后续加载
            data["_plugin_dir"] = str(plugin_dir.absolute())

            return data

        except json.JSONDecodeError as e:
            logger.error(f"解析 {meta_path} 失败: {e}")
            return None
        except Exception as e:
            logger.error(f"读取 {meta_path} 时发生错误: {e}")
            return None


# ---------- 一个简单的自测入口（放在文件末尾，方便调试）----------
if __name__ == "__main__":
    # 配置日志输出级别
    logging.basicConfig(level=logging.INFO)

    # 假设当前脚本位于 src/plugin/ 下，插件目录在项目根目录的 plugins/
    project_root = Path(__file__).parent.parent.parent
    plugins_path = project_root / "plugins"

    scanner = PluginScanner(plugins_path)
    result = scanner.scan()

    print("\n扫描结果（原始数据）：")
    for item in result:
        print(item)