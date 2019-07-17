import json
import logging
#from app.models import *

def report_reader():
    file_path = "E:/Git/PycharmProjects/reports/100.json"
    with open(file_path, "r+", encoding="utf-8") as f:
        try:
            content_json = json.loads(f.read())
            print(content_json['success'])
        except (KeyError, TypeError):
            logging.error("reader report faile: {}".format(file_path))
    return

if __name__ == '__main__':
    report_reader()

