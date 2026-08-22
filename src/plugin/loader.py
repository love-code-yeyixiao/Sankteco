"""
插件动态加载器
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Tuple, cast
from types import ModuleType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginLoader")

class PluginLoader:
    """
    插件加载器：负责动态导入插件的 main.py 文件，并提取 register 函数
    """

    def __init__(self):
        # 存储已加载的插件：{ plugin_id: (module, register_func) }
        self._loaded_plugins: Dict[str, Tuple[ModuleType, Callable]] = {}

    def load_from_info(self, plugin_info: Dict[str, Any]) -> bool:
        """
        根据扫描器返回的插件信息加载一个插件
        :param plugin_info: 包含 _plugin_dir 和 id 等字段的字典
        :return: True 表示加载成功，False 表示加载失败
        """
        plugin_id = plugin_info.get("id")
        plugin_dir = Path(plugin_info.get("_plugin_dir", ""))
        entry_file = plugin_info.get("entry", "main.py")

        if not plugin_id or not plugin_dir.exists():
            logger.error(f"插件信息无效: {plugin_info}")
            return False

        # 检查是否已经加载过
        if plugin_id in self._loaded_plugins:
            logger.debug(f"插件 {plugin_id} 已加载，跳过")
            return True

        main_path = plugin_dir / entry_file
        if not main_path.exists():
            logger.error(f"插件 {plugin_id} 的入口文件不存在: {main_path}")
            return False

        # 动态加载模块
        module_name = f"plugin_{plugin_id.replace('.', '_')}"  # 将 id 中的点替换为下划线

        try:
            # 如果模块已经在 sys.modules 中，先移除（确保重新加载）
            if module_name in sys.modules:
                del sys.modules[module_name]

            spec = importlib.util.spec_from_file_location(module_name, main_path)
            if spec is None or spec.loader is None:
                logger.error(f"无法为 {main_path} 创建 spec")
                return False

            module = importlib.util.module_from_spec(spec)
            # 执行模块代码
            spec.loader.exec_module(module)

            # 检查模块中是否有 register 函数
            if not hasattr(module, "register"):
                logger.error(f"插件 {plugin_id} 缺少 register 函数")
                return False

            register_func = getattr(module, "register")
            if not callable(register_func):
                logger.error(f"插件 {plugin_id} 的 register 不是可调用对象")
                return False

            # 缓存
            self._loaded_plugins[plugin_id] = (module, register_func)
            logger.info(f"✅ 插件 {plugin_id} 加载成功")
            return True

        except Exception as e:
            logger.error(f"加载插件 {plugin_id} 时发生异常: {e}")
            return False

    def load_all(self, plugin_infos: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        批量加载多个插件
        :param plugin_infos: 扫描器返回的插件信息列表
        :return: { plugin_id: 是否加载成功 }
        """
        results = {}
        for info in plugin_infos:
            plugin_id = info.get("id")
            if not plugin_id:
                continue
            results[plugin_id] = self.load_from_info(info)
        return results

    def get_register_func(self, plugin_id: str) -> Optional[Callable]:
        """
        获取已加载插件的 register 函数
        :return: 如果插件未加载，返回 None
        """
        if plugin_id in self._loaded_plugins:
            module_and_func = self._loaded_plugins[plugin_id]
            # ✅ 显式告诉 Pylance：这是一个 Callable
            return cast(Callable, module_and_func[1])
        return None

    def get_module(self, plugin_id: str) -> Optional[ModuleType]:
        """获取已加载插件的模块对象（用于调试或热重载）"""
        if plugin_id in self._loaded_plugins:
            module, _ = self._loaded_plugins[plugin_id]
            # ✅ 显式告诉 Pylance：这是一个 ModuleType
            return cast(ModuleType, module)
        return None

    def unload(self, plugin_id: str) -> bool:
        """
        卸载一个插件（从缓存中移除，并从 sys.modules 中清理）
        :return: True 表示卸载成功
        """
        if plugin_id not in self._loaded_plugins:
            logger.warning(f"插件 {plugin_id} 未加载，无需卸载")
            return False

        # 获取模块名
        module, _ = self._loaded_plugins.pop(plugin_id)
        module_name = module.__name__

        # 从 sys.modules 中移除
        if module_name in sys.modules:
            del sys.modules[module_name]
            logger.info(f"✅ 插件 {plugin_id} 已从 Python 缓存中移除")
        else:
            logger.warning(f"模块 {module_name} 不在 sys.modules 中")

        return True

    def reload(self, plugin_info: Dict[str, Any]) -> bool:
        """
        热重载一个插件（先卸载再加载）
        """
        plugin_id = plugin_info.get("id")
        if not plugin_id:
            return False

        # 先卸载
        self.unload(plugin_id)

        # 再加载
        return self.load_from_info(plugin_info)


# ---------- 自测入口 ----------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 先扫描，再加载
    from scanner import PluginScanner

    project_root = Path(__file__).parent.parent.parent
    plugins_path = project_root / "plugins"

    scanner = PluginScanner(plugins_path)
    plugins = scanner.scan()

    loader = PluginLoader()
    for info in plugins:
        success = loader.load_from_info(info)
        print(f"加载 {info.get('name')}: {'成功' if success else '失败'}")

        # 如果有 register 函数，可以演示调用（但暂时不创建 QWidget）
        plugin_id = info.get("id")
        if not plugin_id:  # 防御性编程
            continue
        success = loader.load_from_info(info)
        print(f"加载 {info.get('name')}: {'成功' if success else '失败'}")
        
        func = loader.get_register_func(plugin_id)  # 现在参数类型安全
        if func:
            print(f"  已获取 register 函数: {func}")
        if func:
            print(f"  已获取 register 函数: {func}")