import importlib.util
import os
import inspect


class CorePluginManager():
    def __init__(self, plugin_path: str):
        self.plugins = {}
        dir_path = os.path.abspath(plugin_path)
        for f in [x for x in os.listdir(dir_path) if x.endswith(".py")]:
            full_path = os.path.join(dir_path, f)
            if not os.path.isfile(full_path):
                continue
            uid = self.__get_plugin_uid__(full_path)
            if uid is not None:
                self.plugins[uid] = full_path

    def plugin_list(self) -> list:
        return list(self.plugins.keys())

    def plugin_check(self, plugin: str) -> bool:
        return plugin in self.plugins

    def plugin_load(self, plugin: str):
        if self.plugin_check(plugin):
            return self.__import_module_from_path__(self.plugins[plugin])
        else:
            return None

    def __get_plugin_uid__(self, path: str) -> str:
        plugin = self.__import_module_from_path__(path)
        for cls in inspect.getmembers(plugin, inspect.isclass):
            if cls[0] == 'Plugin':
                return plugin.Plugin().get_uid()
            else:
                return None

    def __import_module_from_path__(self, path: str):
        spec = importlib.util.spec_from_file_location("plugin", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module