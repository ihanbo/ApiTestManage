<<<<<<< HEAD
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

=======
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

>>>>>>> 927d0e2c43d7c990686937b22e7c3f12ab62fa67
