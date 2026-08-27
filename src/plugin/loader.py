# src/plugin/loader.py
import logging, sys, shutil
from typing import Dict, Callable, Optional, Any, List
from pathlib import Path
from stevedore import ExtensionManager
from PySide2.QtCore import QStandardPaths

logger = logging.getLogger("PluginLoader")


class PluginLoader:
    """基于 Stevedore 的插件加载器 + 本地开发模式回退"""

    def __init__(self, namespace: str = "sankteco.plugin"):
        self.namespace = namespace
        # 存储已加载的插件信息：{ plugin_id: { 'register': func, 'meta': {}, 'module': module, 'enabled': bool } }
        self._plugins: Dict[str, Dict[str, Any]] = {}
        # 本地插件目录（用于开发模式）
        self._local_plugins_dir = Path(__file__).parent.parent.parent / "plugins"
        # 数据目录
        self._data_dir = self._get_data_dir()

    def _get_data_dir(self) -> Path:
        """获取插件数据存储根目录"""
        data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)  # type: ignore
        plugin_data_dir = Path(data_dir) / "plugins" / "data"
        plugin_data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"插件数据目录: {plugin_data_dir}")
        return plugin_data_dir

    def _get_plugins_dir(self) -> Path:
        """获取本地插件目录"""
        return self._local_plugins_dir

    def get_plugin_data_dir(self, plugin_id: str) -> Path:
        """获取指定插件的数据存储子目录"""
        plugin_data_dir = self._data_dir / plugin_id
        plugin_data_dir.mkdir(parents=True, exist_ok=True)
        return plugin_data_dir

    def load_all_plugins(self) -> int:
        # 1. 先尝试 Stevedore
        loaded_count = self._load_from_stevedore()

        if loaded_count > 0:
            return loaded_count

        # 2. 回退到本地目录扫描（开发模式）
        logger.info("Stevedore 未发现插件，回退到扫描本地 plugins/ 目录...")
        return self._load_from_local_plugins()

    def _load_from_stevedore(self) -> int:
        """从 Stevedore 加载插件"""
        logger.info(f"尝试从 Stevedore 加载命名空间 '{self.namespace}'...")

        try:
            mgr = ExtensionManager(
                namespace=self.namespace,
                invoke_on_load=False,
            )
        except Exception as e:
            logger.error(f"加载 ExtensionManager 失败: {e}")
            return 0

        loaded_count = 0
        for ext in mgr.extensions:
            plugin_id = ext.name
            register_func = ext.plugin

            if not callable(register_func):
                logger.warning(f"插件 {plugin_id} 的入口点不是可调用对象")
                continue

            meta = self._extract_metadata(ext.module)

            self._plugins[plugin_id] = {
                "register": register_func,
                "meta": meta,
                "module": ext.module,
            }
            loaded_count += 1
            logger.info(
                f"[Stevedore] 加载插件: {plugin_id} (v{meta.get('version', 'unknown')})"
            )

        return loaded_count

    def _extract_metadata(self, module) -> Dict[str, Any]:
        """
        从插件模块中提取元数据
        约定插件在模块中定义 __plugin_meta__ 字典
        """
        default_meta = {
            "name": module.__name__,
            "version": "1.0.0",
            "description": "",
            "author": "",
            "icon": "APPLICATION",
        }

        if hasattr(module, "__plugin_meta__"):
            meta = getattr(module, "__plugin_meta__")
            if isinstance(meta, dict):
                default_meta.update(meta)
        return default_meta

    def get_register_func(self, plugin_id: str) -> Optional[Callable]:
        """获取已加载插件的 register 函数"""
        plugin_info = self._plugins.get(plugin_id)
        if plugin_info:
            return plugin_info.get("register")
        return None

    def get_plugin_meta(self, plugin_id: str) -> Dict[str, Any]:
        """获取已加载插件的元数据"""
        plugin_info = self._plugins.get(plugin_id)
        if plugin_info:
            return plugin_info.get("meta", {})
        return {}

    def get_all_plugin_ids(self) -> List[str]:
        """获取所有已加载插件的 ID 列表"""
        return list(self._plugins.keys())

    def get_all_plugin_info(self) -> List[Dict[str, Any]]:
        """
        获取所有已加载插件的完整信息（用于 UI 展示）
        """
        result = []
        for plugin_id, info in self._plugins.items():
            result.append(
                {
                    "id": plugin_id,
                    "meta": info.get("meta", {}),
                    "has_register": info.get("register") is not None,
                }
            )
        return result

    def reload_all_plugins(self) -> int:
        """
        热重载所有插件（简单实现：重新加载）
        """
        logger.info("热重载所有插件...")
        self._plugins.clear()
        return self.load_all_plugins()

    def reload_plugin(self, plugin_id: str) -> bool:
        """
        热重载指定插件（需要插件支持）
        注意：Stevedore 本身不支持单个插件重载，这里需要配合 importlib.reload
        """
        # 这需要更复杂的实现，建议暂时只支持全量重载
        logger.warning(f"单个插件热重载暂不支持，请使用 reload_all_plugins()")
        return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """
        从内存中卸载插件（不删除文件）
        :return: True 表示卸载成功
        """
        if plugin_id not in self._plugins:
            logger.warning(f"插件 {plugin_id} 未加载，无法卸载")
            return False

        plugin_info = self._plugins[plugin_id]
        module = plugin_info.get("module")

        # 1. 从 sys.modules 中移除模块
        if module and hasattr(module, "__name__"):
            module_name = module.__name__
            if module_name in sys.modules:
                # 找到所有相关模块并移除
                to_remove = [
                    name for name in sys.modules if name.startswith(module_name)
                ]
                for name in to_remove:
                    del sys.modules[name]
                logger.debug(f"已从 sys.modules 移除: {to_remove}")

        # 2. 从 _plugins 中移除
        del self._plugins[plugin_id]
        logger.info(f"插件 {plugin_id} 已从内存中卸载")
        return True

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """卸载插件：删除插件文件夹（无论是否禁用）"""
        # 1. 从内存中移除
        self.unload_plugin(plugin_id)

        # 2. 查找插件目录（包括 .disabled 的）
        plugin_dir = self._get_plugin_dir_by_id(plugin_id)
        if plugin_dir and plugin_dir.exists():
            try:
                shutil.rmtree(plugin_dir)
                logger.info(f"已删除插件: {plugin_dir}")
                return True
            except Exception as e:
                logger.error(f"删除失败: {e}")
                return False

        return False

    def _get_plugin_dir_by_id(self, plugin_id: str) -> Optional[Path]:
        """根据 plugin_id 查找对应的插件目录（无论是否被禁用）"""
        plugins_root = self._local_plugins_dir

        # 遍历所有文件夹（包括 .disabled 后缀的）
        for item in plugins_root.iterdir():
            if not item.is_dir():
                continue
            # 检查是否是目标插件（去除 .disabled 后缀后匹配）
            name = item.name
            if name.endswith(".disabled"):
                name = name[:-9]  # 移除 .disabled 后缀

            # 检查这个目录是否包含 plugin.json 且 id 匹配
            meta_file = item / "plugin.json"
            if meta_file.exists():
                try:
                    import json

                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    if meta.get("id") == plugin_id:
                        return item
                except:
                    pass
        return None

    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """
        通过文件系统判断插件是否启用
        - 如果插件目录存在且没有 .disabled 后缀 → 启用
        - 如果插件目录存在且有 .disabled 后缀 → 禁用
        - 如果插件不存在 → 返回 False
        """
        plugin_dir = self._get_plugin_dir_by_id(plugin_id)
        if not plugin_dir:
            return False

        # 如果目录名以 .disabled 结尾，表示禁用
        if plugin_dir.name.endswith(".disabled"):
            return False
        return True

    def enable_plugin(self, plugin_id: str, context) -> Optional[Callable]:
        """
        启用插件：
        1. 如果存在 .disabled 文件夹，重命名为正常名称
        2. 重新加载插件
        """
        plugins_root = self._local_plugins_dir
        if not plugins_root.exists():
            return None

        # 查找 .disabled 文件夹
        disabled_dir = None
        for item in plugins_root.iterdir():
            if not item.is_dir():
                continue
            if item.name.endswith(".disabled"):
                # 检查这个文件夹内的 plugin.json 是否匹配
                meta_file = item / "plugin.json"
                if meta_file.exists():
                    try:
                        import json

                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        if meta.get("id") == plugin_id:
                            disabled_dir = item
                            break
                    except:
                        pass

        if disabled_dir:
            # 重命名：移除 .disabled 后缀
            new_name = disabled_dir.name[:-9]  # 去除 .disabled
            new_path = disabled_dir.parent / new_name
            disabled_dir.rename(new_path)
            logger.info(f"已启用插件: {plugin_id} ({new_path})")

        # 重新加载插件（调用现有的加载逻辑）
        return self._load_single_plugin(plugin_id)  # type: ignore

    def disable_plugin(self, plugin_id: str) -> bool:
        """
        禁用插件：
        1. 从内存中卸载
        2. 将插件文件夹重命名为 .disabled
        """
        # 1. 先卸载（从内存中移除）
        self.unload_plugin(plugin_id)

        # 2. 查找插件目录
        plugin_dir = self._get_plugin_dir_by_id(plugin_id)
        if not plugin_dir:
            logger.warning(f"找不到插件目录: {plugin_id}")
            return False

        # 3. 重命名为 .disabled
        new_name = plugin_dir.name + ".disabled"
        new_path = plugin_dir.parent / new_name
        plugin_dir.rename(new_path)
        logger.info(f"已禁用插件: {plugin_id} ({new_path})")

        # 4. 从 _plugins 字典中移除（因为目录名变了，下次扫描不会加载）
        if plugin_id in self._plugins:
            del self._plugins[plugin_id]

        return True

    def _load_from_local_plugins(self) -> int:
        """扫描本地 plugins/ 文件夹，只加载非 .disabled 的插件"""
        plugins_dir = self._local_plugins_dir
        if not plugins_dir.exists():
            return 0

        count = 0
        for plugin_dir in plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            if plugin_dir.name.startswith("_") or plugin_dir.name.startswith("."):
                continue

            # 跳过被禁用的插件（.disabled 后缀）
            if plugin_dir.name.endswith(".disabled"):
                logger.debug(f"跳过已禁用的插件: {plugin_dir.name}")
                continue

            # 读取 plugin.json
            meta_path = plugin_dir / "plugin.json"
            if not meta_path.exists():
                continue

            try:
                import json

                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception as e:
                logger.warning(f"解析 {meta_path} 失败: {e}")
                continue

            plugin_id = meta.get("id")
            if not plugin_id:
                continue

            entry = meta.get("entry", "main.py")
            main_path = plugin_dir / entry
            if not main_path.exists():
                logger.warning(f"入口文件不存在: {main_path}")
                continue

            # 动态加载
            import importlib.util

            module_name = f"local_plugin_{plugin_id.replace('.', '_')}"

            if module_name in sys.modules:
                del sys.modules[module_name]

            try:
                spec = importlib.util.spec_from_file_location(module_name, main_path)
                if not spec or not spec.loader:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:
                logger.error(f"加载 {main_path} 失败: {e}")
                continue

            meta_data = getattr(module, "__plugin_meta__", {})
            register_func = getattr(module, "register", None)

            if not callable(register_func):
                logger.warning(f"插件 {plugin_id} 缺少 register 函数")
                continue

            if "name" not in meta_data:
                meta_data["name"] = meta.get("name", plugin_id)
            if "icon" not in meta_data:
                meta_data["icon"] = meta.get("icon", "APPLICATION")

            # 存储插件信息
            self._plugins[plugin_id] = {
                "register": register_func,
                "meta": meta_data,
                "module": module,
                "enabled": True,
                "is_local": True,
                "_plugin_dir": str(plugin_dir.absolute()),  # 存储真实路径
            }
            count += 1
            logger.info(
                f"[本地] 加载插件: {plugin_id} (v{meta_data.get('version', 'unknown')})"
            )

        return count

    def _load_single_plugin(self, plugin_id: str) -> Optional[Callable]:
        """
        加载单个插件（用于启用时重新加载）
        返回 register 函数，失败返回 None
        """
        # 先检查是否已经在 _plugins 中（已加载）
        if plugin_id in self._plugins:
            plugin_info = self._plugins[plugin_id]
            register_func = plugin_info.get("register")
            if register_func and callable(register_func):
                return register_func

        # 查找插件目录
        plugin_dir = self._get_plugin_dir_by_id(plugin_id)
        if not plugin_dir or not plugin_dir.exists():
            logger.error(f"找不到插件目录: {plugin_id}")
            return None

        meta_path = plugin_dir / "plugin.json"
        if not meta_path.exists():
            logger.error(f"插件 {plugin_id} 缺少 plugin.json")
            return None

        try:
            import json

            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as e:
            logger.error(f"读取 plugin.json 失败: {e}")
            return None

        entry = meta.get("entry", "main.py")
        main_path = plugin_dir / entry
        if not main_path.exists():
            logger.error(f"入口文件不存在: {main_path}")
            return None

        import importlib.util

        module_name = f"local_plugin_{plugin_id.replace('.', '_')}"

        if module_name in sys.modules:
            del sys.modules[module_name]

        try:
            spec = importlib.util.spec_from_file_location(module_name, main_path)
            if not spec or not spec.loader:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            logger.error(f"加载模块失败: {e}")
            return None

        register_func = getattr(module, "register", None)
        if not callable(register_func):
            logger.error(f"插件 {plugin_id} 缺少 register 函数")
            return None

        meta_data = getattr(module, "__plugin_meta__", {})
        if "name" not in meta_data:
            meta_data["name"] = meta.get("name", plugin_id)
        if "icon" not in meta_data:
            meta_data["icon"] = meta.get("icon", "APPLICATION")

        # 更新 _plugins 中的信息
        if plugin_id in self._plugins:
            self._plugins[plugin_id]["register"] = register_func
            self._plugins[plugin_id]["meta"] = meta_data
            self._plugins[plugin_id]["module"] = module
            self._plugins[plugin_id]["enabled"] = True
        else:
            self._plugins[plugin_id] = {
                "register": register_func,
                "meta": meta_data,
                "module": module,
                "enabled": True,
                "is_local": True,
                "_plugin_dir": str(plugin_dir.absolute()),
            }

        logger.info(f"插件 {plugin_id} 已重新加载")
        return register_func
