plugin_uid = str("plugin")

class Plugin():
    @staticmethod
    def get_uid() -> str:
        return plugin_uid

    def run(self, data: dict) -> dict:
        print(f'''Plugin test {plugin_uid}''')
        return {}