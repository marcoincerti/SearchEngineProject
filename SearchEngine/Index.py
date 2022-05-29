import os
import time
import xml.etree.ElementTree as ET
import whoosh.index as ix
from whoosh import index
from whoosh.fields import SchemaClass, ID, TEXT, Schema
from SearchEngine.Preprocessing import CustomAnalyzer

N_PROC = 4
INDEX_DUMP = "src/dump_grande.xml"
Index_Name = 'index_dir/index_' + 'versione_1'


# class CustomSchema(Schema):
#     id = ID(stored=True)
#     url = ID(stored=True)
#     title = TEXT(stored=True, analyzer=CustomAnalyzer())
#     content = TEXT(stored=True, analyzer=CustomAnalyzer())


class CustomIndex:
    def __init__(self):
        self.schema = Schema(id=ID(stored=True),
                             url=ID(stored=True),
                             title=TEXT(stored=True, analyzer=CustomAnalyzer(), phrase=True),
                             content=TEXT(stored=True, analyzer=CustomAnalyzer(), phrase=True, spelling=True))
        self.dir_path = Index_Name
        self.index = None
        self.writer = None
        self.reader = None
        print(type(self.schema))

    @staticmethod
    def createReader(index):
        return index.reader()

    def create(self):
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)
            document_add = 0
            # creo indice

            self.index = index.create_in(self.dir_path, self.schema)
            if not self.index:
                raise FileNotFoundError("errore indice")
            self.writer = self.index.writer(limitmb=2048, procs=N_PROC, multisegment=True)
            #self.writer = self.index.writer()

            start_time = time.time()
            with open(INDEX_DUMP, 'r') as xml_file:
                tree = ET.parse(INDEX_DUMP)
            root = tree.getroot()
            document_total = len(list(root))
            for x in range(document_total):
                document_add += 1
                print("{} su {}".format(document_add, document_total))
                id = root[x][0].text
                url = root[x][1].text
                title = root[x][2].text
                content = root[x][3].text
                self.writer.add_document(id=id, url=url, title=title,
                                    content=content)
            print("eseguo il commit")
            self.writer.commit()
            print("--- %s seconds ---" % (time.time() - start_time))
            self.reader = self.createReader(self.index)
        else:
            print("Indice già esistente")
            self.index = ix.open_dir(self.dir_path)
            self.reader = self.createReader(self.index)

