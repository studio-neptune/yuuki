from bs4 import BeautifulSoup

class Yuuki_WebDataReader:
    def __init__(self, Yuuki_Data):
        self.handle = Yuuki_Data

    def get_log(self, name):
        if name not in self.handle.LogType:
            return {"status": 404}
        with open(
                self.handle.LogPath
                +
                self.handle.LogName.format(name)
        ) as file:
            html_doc = file.read()
        parser = BeautifulSoup(html_doc, 'html.parser')
        events = parser.find_all('li')
        return {name: [result.string for result in events]}

    def get_all_logs(self):
        logs = {}

        for name in self.handle.LogType:
            with open(
                    self.handle.LogPath
                    +
                    self.handle.LogName.format(name)
            ) as file:
                html_doc = file.read()
            parser = BeautifulSoup(html_doc, 'html.parser')
            events = parser.find_all('li')
            logs[name] = [result.string for result in events]

        return logs
