import importlib.util
import os
import inspect
from types import ModuleType

from module.core_exception import CoreException
from module.config import plugin_path

class CorePlugin():
    def __init__(self) -> None:
        pass

    def __get_plugins__(self) -> dict:
        result = {}
        dir_path = os.path.abspath(plugin_path)
        for f in [x for x in os.listdir(dir_path) if x.endswith(".py")]:
            full_path = os.path.join(dir_path, f)
            if not os.path.isfile(full_path):
                continue
            uid = self.__get_plugin_uid__(full_path)
            if uid is not None:
                result[uid] = full_path
        return result

    def plugins(self):
        return list(self.__get_plugins__().keys())

    def load(self, uid: str) -> ModuleType:
        pl = self.__get_plugins__()
        if uid in pl:
            return self.__import_module_from_path__(pl[uid])
        else:
            return None

    def __get_plugin_uid__(self, path: str) -> str:
        plugin = self.__import_module_from_path__(path)
        for cls in inspect.getmembers(plugin, inspect.isclass):
            if cls[0] == 'Plugin':
                return plugin.Plugin().get_uid()
        return None

    def __import_module_from_path__(self, path: str) -> ModuleType:
        spec = importlib.util.spec_from_file_location("plugin", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module