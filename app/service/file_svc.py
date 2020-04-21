import json
import os
from app.utility.base_svc import BaseService


class FileService(BaseService):

    def __init__(self):
        self.log = self.add_service('file_svc', self)

    @staticmethod
    async def load_json_file(file):
        with open(file) as json_file:
            data = json.load(json_file)
        return data

    @staticmethod
    async def get_json_files(path):
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path)
                for f in filenames if os.path.splitext(f)[1] == '.json']
        return files

