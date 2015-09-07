# -*- coding: utf-8 -*-
import json
import codecs

class W3SchoolPipeline(object):
    def __init__(self):
      self.file = codecs.open('w3school_utf8.json', 'wb', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        # print line
        self.file.write(line.decode("unicode_escape"))
        return item
