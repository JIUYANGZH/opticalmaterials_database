import logging
from chemdataextractor.model.units.quantity_model import QuantityModel,DimensionlessModel
from chemdataextractor.model.units.unit import Unit
from chemdataextractor.model.units.dimension import Dimension
from chemdataextractor.parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore
from chemdataextractor.parse.actions import merge, join
from chemdataextractor.relex.snowball import Snowball
from chemdataextractor.parse.auto import AutoTableParser, AutoSentenceParser
from chemdataextractor.model import Compound, ModelType, StringType
from chemdataextractor.doc import Document,Heading,Sentence,Paragraph
from chemdataextractor.model.units import LengthModel
from pandas.io.json import json_normalize
from chemdataextractor.model.model import RefractiveIndex,DielectricConstant
import pandas as pd
import json
import os
import re
import xml.etree.ElementTree as ET
import time

class RefractiveIndexDataBase():

    def __init__(self,paper_root,save_root,filename):
        self.dic = None
        self.filename = filename
        self.paper_root = paper_root
        self.count = 0
        self.save_root = save_root

    def write_into_file(self):

        #with open('{}/{}.txt'.format(self.save_root,self.filename), 'a+', encoding='utf-8') as f1:
            #f1.write(json.dumps(self.dic))
            #f1.write('\n')

        with open('{}/{}.json'.format(self.save_root,self.filename), 'a', encoding='utf-8') as json_file:
            json.dump(self.dic, json_file, ensure_ascii=False)
            json_file.write('\n')

        #df = json_normalize(self.dic)
        #df.to_csv('{}/{}.csv'.format(self.save_root,self.filename), mode='a', header=False, encoding='utf-8')

        return

    def extraction(self,file):
        #try:
            f = open(file,'rb')
            d = Document.from_file(f)
            a = Snowball.load(r'./chemdataextractor/relex/refractive_index.pkl')
            a.save_dir = r'./chemdataextractor/relex'
            #a.relations_save_path = self.save_root + 'test.json'
            a.save_file_name = 'test'
            RefractiveIndex.parsers.append(a)
            #print(RefractiveIndex.parsers)
            d.models = [RefractiveIndex]
            print ('parsing ' + file)
            #print(type(d.records))
            rough = d.records.serialize()
            for dic in rough:
                #print(dic)
                if 'RefractiveIndex' not in dic.keys():
                    continue
                if 'names' in dic['RefractiveIndex']['compound']['Compound'].keys():
                    try:
                        dic['metadata'] = str(d.metadata.serialize())
                    except:
                        dic['metadata'] = 'Not Found'
                    self.count += 1
                    self.dic = dic
                    print (dic)
                    self.write_into_file()
            print (str(self.count) + ' relations in total')
            print (file + ' is done')
            f.close()
        # except Exception as e:
        #     print ('Encounting error: ',e)
        #     pass


test = RefractiveIndexDataBase(paper_root=r'./demo/',save_root=r'./save/',filename='test_rn')
for paper in os.listdir(test.paper_root)[0:6]:
    test.extraction(test.paper_root+paper)
