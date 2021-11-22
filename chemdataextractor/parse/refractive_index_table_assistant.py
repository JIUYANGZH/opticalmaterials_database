import logging

from chemdataextractor.model.units.quantity_model import QuantityModel,DimensionlessModel
from chemdataextractor.model.units.unit import Unit
from chemdataextractor.parse.cem import cem
from chemdataextractor.model.units.dimension import Dimension
from chemdataextractor.parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore,Group
from chemdataextractor.parse.actions import merge, join
from chemdataextractor.parse.cem import cem,chemical_name,chemical_label
from chemdataextractor.parse.auto import AutoTableParser, AutoSentenceParser
from chemdataextractor.model import Compound, ModelType, StringType
from chemdataextractor.doc import Document,Heading,Sentence,Paragraph
from rnparser import RnParser
from chemdataextractor.model.units import LengthModel
from rn_wavelength_parser import RefractiveIndexWavelengthParser
import json
import xml.etree.ElementTree as ET
import re
from parsertemplate import PropertyParserTemplate
from pandas.io.json import json_normalize

log = logging.getLogger(__name__)


# sent = Sentence('ZnO2-NNPN is good')
# print (sent.tagged_tokens)
#
# result = cem.scan(sent.tagged_tokens)
# for r in result:
#     text = r[0].xpath('//names/text()')
#     print (text)

from tabledataextractor import Table
import tabledataextractor
from chemdataextractor.parse import Any, I, OneOrMore, Optional, R, W, ZeroOrMore, join, merge
from chemdataextractor.doc import Sentence
from chemdataextractor.doc import Document
from lxml import etree
import json
from chemdataextractor.parse.cem import cem
import re
from tabledataextractor.output.print import print_table
from bs4 import BeautifulSoup
import csv
import pandas as pd
import numpy


# f = open('C:/Users/jiuya/Downloads/3.html','rb')
# html = f.read()
# soup = BeautifulSoup(html,features="lxml")
# table = soup.find_all("table")
#table = soup.find_all('table')

#url = 'https://pubs.rsc.org/en/content/articlehtml/2011/cp/c0cp02270e'
# parse_element = cem('name')
# sentence = Sentence('I SiO2 ok')
#
# tagged_sentence = sentence.tagged_tokens
#
# lst = ['I','S','ok']
# result = parse_element.scan(tagged_sentence)
# for n in result:
#     text_list = n[0].xpath('//' + 'name' + '/text()')
#     print (n[0])
#     print(etree.tostring(n[0]))
#     print (text_list)


specifier = (W('n') | I('nexp')| W('n1') | W('nlit') | W('nav')| W('ncal')| I('refractive') + I('index')| I('refraction') + I('indices')| I('refractive') + I('indices')| I('refraction') + I('index') | I('RIa')| I('RIb')| I('RIc') | I('R.I.')| I('RI') | I('R.I') | W('nF') | W('nC') | W('nE') | I('R') + I('I') | W('nD') | W('n2')| W('n3') | I('refraction') | I('index'))('specifier').add_action(join)
#specifier_2 = (W('nF')|W('nC')|I('R') + I('I')|W('nD')| I('n2')| I('refraction')| I('index'))('specifier').add_action(join)
#wavelength = (W('nm') | W('μm'))('wavelength')
value = R("^\d+?\.\d+?$")('value')
wavelength_value = (R("^\d+?\.\d+?$") + W('μm')| R("^\d+?\.\d+?$") + W('nm')| R("^\d+") + W('nm'))('wavelengthvalue').add_action(join)
wavelength = (I('wavelength')|I('wavelengths')|R('[\u03BB]')|W('λ')|W('λ'))('wavelength')
#wavelength_value = (R("^\d+?\.\d+?$") + W('nm'))('wavelengthvalue')

#s = Sentence('Fe3O4 and SiO2 is good')
chemical = Group(cem | chemical_label | Group(chemical_name)('compound'))
# result = chemical.scan(s.tagged_tokens)
#
# test = []
# for r in result:
#     print (r)
#     print(etree.tostring(r[0]))
#     text = r[0].xpath('//names/text()')
#     test.append(text)
#     #print (text)
# print (test)
# lst = ['Fe3O4', 'Si2E3']
# print (', '.join(lst))


def write_into_file(dic):
    #print(dic)
    with open(r'F:\mydata\rn_el_mylogic_table\table_el_refractive_index_mylogic_new.txt', 'a+', encoding='utf-8') as f1:
        f1.write(json.dumps(dic))
        f1.write('\n')

    with open(r"F:\mydata\rn_el_mylogic_table\table_el_refractive_index_mylogic_new.json", 'a', encoding='utf-8') as json_file:
        json.dump(dic, json_file, ensure_ascii=False)
        json_file.write('\n')

    df = json_normalize(dic)
    df.to_csv(r'F:\mydata\rn_el_mylogic_table\table_el_refractive_index_mylogic_new.csv', mode='a', header=False, encoding='utf-8')
    return

def clean_strip(table):
    for a in range(len(table)):
        for b in range(len(table[a])):
            table[a][b] = table[a][b].replace('\n', ' ')
    return table


def get_compound_fromany(sentence):
    compound = []
    text_list = None
    sentence_scan = Sentence(sentence).tagged_tokens
    compound_information = chemical.scan(sentence_scan)
    for result in compound_information:
        text_list = result[0].xpath('//' + 'names' + '/text()')
        compound.append(''.join(text_list))
    return compound

def get_wavelength_fromcaption(caption):
    caption_scan = Sentence(caption).tagged_tokens
    wavelength_information = wavelength_value.scan(caption_scan)
    for result in wavelength_information:
        #print (result[0])
        text_list = result[0].xpath('//' + 'wavelengthvalue' + '/text()')
        wavelength_fromcaption = text_list[0]
        return wavelength_fromcaption



def find_wavelength_specifier_index_firstlayer(table,caption,DOI,count):
    index_specifier = []
    index_wavelength = []
    for token in table[0]:
        specifier_result = specifier.scan(Sentence(token).tagged_tokens)
        for r in specifier_result:
            text = r[0].xpath('//specifier/text()')
            if text:
                index_specifier.append(table[0].index(token))
    for token in table[0]:
        wavelength_result = wavelength.scan(Sentence(token).tagged_tokens)
        for r in wavelength_result:
            text = r[0].xpath('//wavelength/text()')
            #print (text)
            if text:
                index_wavelength.append(table[0].index(token))
    #print (caption)
    #print (', '.join(get_compound_fromany(caption)))
    if index_specifier:
        for i in range(len(table)-1):
            for ind_spe in index_specifier:
                if index_wavelength:
                    for ind_wav in index_wavelength:
                        #print (table[0][0] +': ' +table[i+1][0]+ ', ' + table[0][1] +': ' +table[i+1][1])
                        dic = {'row_headers':table[0][0] +': ' +table[i+1][0]+ ', ' + table[0][1] +': ' +table[i+1][1],
                               'compound_from_row_headers': ', '.join(get_compound_fromany(', '.join(table[i+1]))),
                               'wavelength_information':table[0][ind_wav]+': ' + table[i+1][ind_wav],
                               'refractive_index':table[i+1][ind_spe],'specifier':table[0][ind_spe],'table_caption':caption,
                               'DOI':DOI,'wavelength_fromcaption':'wavelength_fromcaption_specifier, '+ str(get_wavelength_fromcaption(table[0][ind_spe])) + ',' + str(get_wavelength_fromcaption(caption)),'compound_fromcaption': ', '.join(get_compound_fromany(caption))}
                        if re.match("^\d+?\.\d+?$", dic['refractive_index'][:3]):
                            count += 1
                            write_into_file(dic)
                           # print (dic)
                else:
                    dic = {
                        'row_headers': table[0][0] + ': ' + table[i + 1][0] + ', ' + table[0][1] + ': ' + table[i + 1][1],
                        'compound_from_row_headers': ', '.join(
                            get_compound_fromany(', '.join(table[i+1]))),
                        'refractive_index': table[i + 1][ind_spe], 'specifier': table[0][ind_spe], 'table_caption': caption,
                        'DOI': DOI, 'wavelength_fromcaption': 'wavelength_fromcaption_specifier, '+ str(get_wavelength_fromcaption(table[0][ind_spe]))+ ',' +str(get_wavelength_fromcaption(caption)),
                        'compound_fromcaption': ', '.join(get_compound_fromany(caption))}
                    #dic = {'compound_information': table[0][0] + ': ' + table[i + 1][0]+ ', ' + table[0][1] +': ' +table[i+1][1],
                           #'refractive_index': table[i + 1][ind_spe], 'specifier': table[0][ind_spe],
                           #'table_caption': caption, 'DOI': DOI,'wavelength_fromcaption':get_wavelength_fromcaption(caption),'compound_fromcaption':get_compound_fromany(caption)}
                    if re.match("^\d+?\.\d+?$", dic['refractive_index'][:3]):
                        count += 1
                        write_into_file(dic)
                        #print(dic)
    return count

def find_wavelength_specifier_index_secondlayer(table,caption,DOI,count):
    index_specifier = []
    index_wavelength = []
    for token in table[1]:
        specifier_result = specifier.scan(Sentence(token).tagged_tokens)
        for r in specifier_result:
            text = r[0].xpath('//specifier/text()')
            if text:
                index_specifier.append(table[1].index(token))
    for token in table[1]:
        wavelength_result = wavelength.scan(Sentence(token).tagged_tokens)
        for r in wavelength_result:
            text = r[0].xpath('//wavelength/text()')
            if text:
                index_wavelength.append(table[1].index(token))
    if index_specifier:
        for i in range(len(table)-2):
            for ind_spe in index_specifier:
                if index_wavelength:
                    for ind_wav in index_wavelength:
                        #dic = {'compound_information':table[0][0] +': ' +table[i+1][0] + ', ' + table[0][1] +': ' +table[i+1][1],'wavelength_information':table[1][ind_wav]+': ' + table[i+2][ind_wav],'refractive_index':table[i+2][ind_spe],'specifier':table[1][ind_spe],'table_caption':caption,'DOI':DOI,'wavelength_fromcaption':get_wavelength_fromcaption(caption),'compound_fromcaption':get_compound_fromcaption(caption)}

                        dic = {'row_headers':table[0][0] +': ' +table[i+2][0]+ ', ' + table[0][1] +': ' +table[i+2][1],
                               'compound_from_row_headers': ', '.join(get_compound_fromany(', '.join(table[i+2]))),
                               'wavelength_information':table[0][ind_wav]+': ' + table[i+2][ind_wav],
                               'refractive_index':table[i+2][ind_spe],'specifier':table[0][ind_spe],'table_caption':caption,
                               'DOI':DOI,'wavelength_fromcaption':'wavelength_fromcaption, '+ str(get_wavelength_fromcaption(table[0][ind_spe]))+ ',' +str(get_wavelength_fromcaption(caption)),'compound_fromcaption': ', '.join(get_compound_fromany(caption))}
                        if re.match("^\d+?\.\d+?$", dic['refractive_index'][:3]):
                            count += 1
                            write_into_file(dic)
                            #print (dic)
                else:
                    dic = {'row_headers':table[1][0] +': ' +table[i+2][0]+ ', ' + table[1][1] +': ' +table[i+2][1],
                           'compound_from_row_headers': ', '.join(get_compound_fromany(', '.join(table[i+2]))),
                           'refractive_index': table[i + 2][ind_spe], 'specifier': table[1][ind_spe],
                           'table_caption': caption, 'DOI': DOI,'wavelength_fromcaption':'wavelength_fromcaption, '+ str(get_wavelength_fromcaption(table[0][ind_spe])) + ',' +str(get_wavelength_fromcaption(caption)),
                           'compound_fromcaption':get_compound_fromany(caption)}
                    if re.match("^\d+?\.\d+?$", dic['refractive_index'][:3]):
                        count += 1
                        write_into_file(dic)
                        # print (dic)
    return count


with open(r'F:\mydata\rn_el_mylogic_table\table_el_refractive_index_mylogic_new.csv', 'w',encoding='utf-8') as outcsv:
    writer = csv.writer(outcsv)
    writer.writerow(["number", "Source", "compound_from_rowheader",'compound_from_caption','refractive_index_value','row_headers','specifier','caption','wavelength_from_caption','wavelength_from_headers'])

s = 'the refractive index is measured at 485 nm'
#print (get_wavelength_fromcaption(s))

count = 0
if True:
    for i in range(0,168999):
        path = r'F:\el_refractive_index_volumn_2000-2020\{}.xml'.format(i)
        try:
            f = open(path, 'rb')
            d = Document.from_file(f)
            DOI = str(d.metadata.serialize())
            # f = open(path, 'rb')
            # f1 = open(path, 'rb').read()
            # d = Document.from_file(f)
            # root = ET.fromstring(f1)
            # Journal = 'None'
            # DOI = 'None'
            # for child in root:
            #     for cchild in child:
            #         if cchild.tag == '{http://prismstandard.org/namespaces/basic/2.0/}publicationName':
            #             Journal = cchild.text[:]
            #         elif cchild.tag == '{http://prismstandard.org/namespaces/basic/2.0/}doi':
            #             DOI = cchild.text[:]

            for t in d.tables:
                try:
                    table = t.tde_table.pre_cleaned_table.tolist()
                    table_transposed = t.tde_table.pre_cleaned_table.transpose().tolist()
                    #print (table)
                    #print (table_transposed)
                    caption = str(t.caption)
                    clean_strip(table)
                    clean_strip(table_transposed)
                    count = find_wavelength_specifier_index_firstlayer(table,caption,DOI,count)
                    count = find_wavelength_specifier_index_secondlayer(table, caption, DOI, count)
                    count = find_wavelength_specifier_index_firstlayer(table_transposed, caption, DOI, count)
                    count = find_wavelength_specifier_index_secondlayer(table_transposed, caption, DOI, count)
                except Exception as e:
                    print (e)
                    pass


        except Exception as e:
            print (e)
            pass
        print ('{} is done, count = {}'.format(i,count))

# #for i in range(10):
    #table = tabledataextractor.input.from_html.read_file(path,table_number = i)

    #print (table)
#
# for i in range(3,4):
#     f = open(r'F:\rsc_refractive_index\{}.html'.format(i),'rb')
#     doc = Document.from_file(f)
#     #doc.models = [RefractiveIndex]
#     for table in doc.tables:
#         print (table.tde_table)
#         for record in table.records:
#             print (record.serialize())