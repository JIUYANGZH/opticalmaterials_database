import logging

from chemdataextractor.model.units.quantity_model import QuantityModel, DimensionlessModel
from chemdataextractor.model.units.unit import Unit
from chemdataextractor.parse.cem import cem
from chemdataextractor.model.units.dimension import Dimension
from chemdataextractor.parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore, Group
from chemdataextractor.parse.actions import merge, join
from chemdataextractor.parse.cem import cem, chemical_name, chemical_label
from chemdataextractor.parse.auto import AutoTableParser, AutoSentenceParser
from chemdataextractor.model import Compound, ModelType, StringType
from chemdataextractor.doc import Document, Heading, Sentence, Paragraph
from rnparser import RnParser
from chemdataextractor.model.units import LengthModel
from rn_wavelength_parser import RefractiveIndexWavelengthParser
import json
import xml.etree.ElementTree as ET
import re
from parsertemplate import PropertyParserTemplate
from pandas.io.json import json_normalize

log = logging.getLogger(__name__)

# for year in range(2000,2001):
#     for i in range(15,100):
#         try:
#             f = open(r'F:\el_papers_refractiveindex\{}_{}.xml'.format(year,i),'rb')
#             #f1 = open(r'F:\el_papers_refractiveindex\{}_{}.xml'.format(year,i),'rb').read()
#             d = Document.from_file(f)
#             for table in d.tables:
#                 #print(table.caption)
#                 #print (table.tde_table)
#
#                 table_tde = table.tde_table
#                 print (table_tde.pre_cleaned_table)
#                 print (table_tde.pre_cleaned_table.tolist())
#                 print(table.caption)
#
#                 #print ("Data:          \n", table.data)
#                 title_header = table_tde.title_row
#                 stub_header = table_tde.stub_header.tolist()
#                 #print ('stub',stub_header)
#                 #print (dir(table_tde))
#                 row_header = table_tde.row_header.tolist()
#                 col_header = table_tde.col_header.tolist()
#                 #print ('row',row_header)
#                 #print ('col',col_header)
#                 #print (table.caption)
#                 data = table_tde.data.tolist()
#                 #print ('specifier_index: ',get_specifier_index(col_header))
#                 index = get_specifier_index(col_header)
#                 #print (get_data(index,row_header,data,col_header))
#
#         except:
#             pass
#         print ('{} is done'.format(i))

from tabledataextractor import Table
import tabledataextractor
from chemdataextractor.parse import Any, I, OneOrMore, Optional, R, W, ZeroOrMore, join, merge
from chemdataextractor.doc import Sentence
from chemdataextractor.doc import Document
from lxml import etree
import json
from chemdataextractor.model.model import DielectricConstant
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
# table = soup.find_all('table')

# url = 'https://pubs.rsc.org/en/content/articlehtml/2011/cp/c0cp02270e'
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


specifier = (I('dielectric') + I('constants')|I('dielectric') + I('constant')|I('relative') + I('permittivity')
             |I('relative') + I('permittivities')|I('εr')|I("ε'")|I('ε')|I("ε'r")|I('κ'))('specifier').add_action(join)

# specifier_2 = (W('nF')|W('nC')|I('R') + I('I')|W('nD')| I('n2')| I('refraction')| I('index'))('specifier').add_action(join)
# wavelength = (W('nm') | W('μm'))('wavelength')
value = R("^\d+?\.\d+?$")('value')
wavelength_value = (R("^\d+?\.\d+?$") + W('μm') | R("^\d+?\.\d+?$") + W('nm') | R("^\d+") + W('nm'))(
    'wavelengthvalue').add_action(join)

frequency_value = ((R("^\d+?\.\d+?$")|R("^\d+?$"))+ (W('kHz')|W('MHz')|W('GHz')|W('Hz')))('frequencyvalue').add_action(join)
frequency = (I('frequency') | I('frequencies') | I('f') | I('ν')| I('Hz')| I('kHz')| I('MHz')| I('GHz')| I('THz'))('frequency')
wavelength = (I('wavelength') | I('wavelengths') | R('[\u03BB]') | W('λ') | W('λ'))('wavelength')
# wavelength_value = (R("^\d+?\.\d+?$") + W('nm'))('wavelengthvalue')

# s = Sentence('Fe3O4 and SiO2 is good')
chemical = Group(cem | chemical_label | Group(chemical_name)('compound'))

# sentence = 'Dielectric constant'
# specifier_result = specifier.scan(Sentence(sentence).tagged_tokens)
# for r in specifier_result:
#     text = r[0].xpath('//specifier/text()')
#     print (text)
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

def _extract_value(string):
    """
    Takes a string and returns a float or a list representing the string given.

    :param str string: A representation of the values as a string
    :returns: The string expressed as a float or a list of floats if it was a value range.
    :rtype: list(float)
    """
    string = string.replace("-", "-")
    string = string.replace("–", "-")
    string = string.replace("−", "-")
    string = string.replace(" ", "")
    string = string.split("±")[0]
    split_by_num = [r for r in re.split('(\d+\.?(?:\d+)?)', string) if r]
    if split_by_num[0] == "-":
        split_by_num[0] = "-" + split_by_num.pop(1)
    values = []
    for index, value in enumerate(split_by_num):
        try:
            float_val = float(value)
            values.append(float_val)
        except ValueError:
            pass

    return values
def extract_error(string):
    """Extract the error from a string

    :param str string: A representation of the values as a string
    :returns: The string expressed as a float or a list of floats if it was a value range.
    :rtype: list(float)
    """
    string = string.replace("-", "-")
    string = string.replace("–", "-")
    string = string.replace("−", "-")
    string = string.replace(" ", "")
    split_by_num_and_error = [r for r in re.split('(\d+\.?(?:\d+)?)|(±)', string) if r]
    error = None
    for index, value in enumerate(split_by_num_and_error):
        if value == '±':
            try:
                error = float(split_by_num_and_error[index + 1])
            except ValueError:
                pass

    return error

print (extract_error('125-135'))
def write_into_file(dic):
    # print(dic)
    # with open(r'F:\mydata\rn_el_mylogic_table\table_el_refractive_index_mylogic_new.txt', 'a+', encoding='utf-8') as f1:
    #     f1.write(json.dumps(dic))
    #     f1.write('\n')


    if len(dic['compound_from_row_headers']) >= 1:
        if len(dic['compound_from_row_headers'][0]) >= 2:
        #print (dic)
            dic['extracted_values'] = _extract_value(dic['dielectric_constant'])
            dic['extracted_value'] = (max(_extract_value(dic['dielectric_constant'])) + min(_extract_value(dic['dielectric_constant']))) / 2
            #print (dic)
            if extract_error(dic['dielectric_constant']):
                dic['extracted_error'] = extract_error(dic['dielectric_constant'])
            else:
                dic['extracted_error'] = (max(_extract_value(dic['dielectric_constant'])) - min(_extract_value(dic['dielectric_constant']))) / 2
            with open(r"F:\mydata\dielectric\table_mylogic\table_el_sd.json", 'a',
                      encoding='utf-8') as json_file:
                json.dump(dic, json_file, ensure_ascii=False)
                json_file.write('\n')

            # df = json_normalize(dic)
            # df.to_csv(r'F:\mydata\dielectric\table_mylogic\table_rsc_test.csv', mode='a', header=False,
            #           encoding='utf-8')
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


def get_frequency_fromany(caption):
    caption_scan = Sentence(caption).tagged_tokens
    frequency_information = frequency_value.scan(caption_scan)
    for result in frequency_information:
        # print (result[0])
        text_list = result[0].xpath('//' + 'wavelengthvalue' + '/text()')
        frequency_fromcaption = text_list[0]
        return frequency_fromcaption


def find_frequency_specifier_index_firstlayer(table, caption, DOI, count):
    index_specifier = []
    index_frequency = []
    for token in table[0]:
        specifier_result = specifier.scan(Sentence(token).tagged_tokens)
        for r in specifier_result:
            text = r[0].xpath('//specifier/text()')
            if text:
                index_specifier.append(table[0].index(token))
    for token in table[0]:
        frequency_result = frequency.scan(Sentence(token).tagged_tokens)
        for r in frequency_result:
            text = r[0].xpath('//frequency/text()')
            # print (text)
            if text:
                index_frequency.append(table[0].index(token))
    #print(index_frequency)

    # print (caption)
    # print (', '.join(get_compound_fromany(caption)))
    if index_specifier:
        for i in range(len(table) - 1):
            for ind_spe in index_specifier:
                if index_frequency:
                    for ind_freq in index_frequency:
                        # print (table[0][0] +': ' +table[i+1][0]+ ', ' + table[0][1] +': ' +table[i+1][1])
                        dic = {'row_headers': table[0][0] + ': ' + table[i + 1][0] + ', ' + table[0][1] + ': ' +
                                              table[i + 1][1],
                               'compound_from_row_headers': get_compound_fromany(table[i+1][0] + ', ' + table[i+1][1]),
                               'frequency_information': table[0][ind_freq] + ': ' + table[i + 1][ind_freq],
                               'dielectric_constant': table[i + 1][ind_spe], 'specifier': table[0][ind_spe],
                               'table_caption': caption,
                               'DOI': DOI, 'frequency_from_caption':
                                get_frequency_fromany(caption), 'frequency_from_specifier' :
                                get_frequency_fromany(table[0][ind_spe]),
                               'compound_fromcaption': ', '.join(get_compound_fromany(caption))}
                        if re.match("^[0-9](\.[0-9]+)?$", dic['dielectric_constant'][:1]):
                            count += 1
                            write_into_file(dic)
                            #print (dic)
                else:
                    dic = {
                        'row_headers': table[0][0] + ': ' + table[i + 1][0] + ', ' + table[0][1] + ': ' + table[i + 1][
                            1],
                        'compound_from_row_headers': get_compound_fromany(table[i+1][0] + ', ' + table[i+1][1]),
                        'dielectric_constant': table[i + 1][ind_spe], 'specifier': table[0][ind_spe],
                        'table_caption': caption,
                        'DOI': DOI, 'frequency_from_caption':
                                get_frequency_fromany(caption), 'frequency_from_specifier' :
                                get_frequency_fromany(table[0][ind_spe]),
                        'compound_fromcaption': ', '.join(get_compound_fromany(caption))}
                    # dic = {'compound_information': table[0][0] + ': ' + table[i + 1][0]+ ', ' + table[0][1] +': ' +table[i+1][1],
                    # 'refractive_index': table[i + 1][ind_spe], 'specifier': table[0][ind_spe],
                    # 'table_caption': caption, 'DOI': DOI,'wavelength_fromcaption':get_wavelength_fromcaption(caption),'compound_fromcaption':get_compound_fromany(caption)}
                    if re.match("^[0-9](\.[0-9]+)?$", dic['dielectric_constant'][:1]):
                        count += 1
                        write_into_file(dic)
                        #print(dic)
    return count


def find_frequency_specifier_index_secondlayer(table, caption, DOI, count):
    index_specifier = []
    index_frequency = []
    for token in table[1]:
        specifier_result = specifier.scan(Sentence(token).tagged_tokens)
        for r in specifier_result:
            text = r[0].xpath('//specifier/text()')
            if text:
                index_specifier.append(table[1].index(token))
    for token in table[1]:
        frequency_result = frequency.scan(Sentence(token).tagged_tokens)
        for r in frequency_result:
            text = r[0].xpath('//frequency/text()')
            if text:
                index_frequency.append(table[1].index(token))
    if index_specifier:
        for i in range(len(table) - 2):
            for ind_spe in index_specifier:
                if index_frequency:
                    for ind_freq in index_frequency:
                        # dic = {'compound_information':table[0][0] +': ' +table[i+1][0] + ', ' + table[0][1] +': ' +table[i+1][1],'wavelength_information':table[1][ind_wav]+': ' + table[i+2][ind_wav],'refractive_index':table[i+2][ind_spe],'specifier':table[1][ind_spe],'table_caption':caption,'DOI':DOI,'wavelength_fromcaption':get_wavelength_fromcaption(caption),'compound_fromcaption':get_compound_fromcaption(caption)}

                        dic = {'row_headers': table[0][0] + ': ' + table[i + 2][0] + ', ' + table[0][1] + ': ' +
                                              table[i + 2][1],
                               'compound_from_row_headers': get_compound_fromany(table[i+2][0] + ', ' + table[i+2][1]),
                               'frequency_information': table[1][ind_freq] + ': ' + table[i + 2][ind_freq],
                               'dielectric_constant': table[i + 2][ind_spe], 'specifier': table[1][ind_spe],
                               'table_caption': caption,
                               'DOI': DOI, 'frequency_from_caption':
                                get_frequency_fromany(caption), 'frequency_from_specifier' :
                                get_frequency_fromany(table[1][ind_spe]),
                               'compound_fromcaption': ', '.join(get_compound_fromany(caption))}
                        if re.match("^[0-9](\.[0-9]+)?$", dic['dielectric_constant'][:1]):
                            count += 1
                            write_into_file(dic)
                            # print (dic)
                else:
                    dic = {
                        'row_headers': table[1][0] + ': ' + table[i + 2][0] + ', ' + table[1][1] + ': ' + table[i + 2][
                            1],
                        'compound_from_row_headers': get_compound_fromany(table[i+2][0] + ', ' + table[i+2][1]),
                        'dielectric_constant': table[i + 2][ind_spe], 'specifier': table[1][ind_spe],
                        'table_caption': caption, 'DOI': DOI,
                        'frequency_from_caption':
                                get_frequency_fromany(caption), 'frequency_from_specifier' :
                                get_frequency_fromany(table[1][ind_spe]),
                        'compound_fromcaption': get_compound_fromany(caption)}
                    if re.match("^[0-9](\.[0-9]+)?$", dic['dielectric_constant'][:1]):
                        count += 1
                        write_into_file(dic)
                        # print (dic)
    return count


#with open(r'F:\mydata\dielectric\table_mylogic\table_rsc_test.csv', 'w',encoding='utf-8') as outcsv:
    #writer = csv.writer(outcsv)
    #writer.writerow(["number", "Source", "compound_from_rowheader",'compound_from_caption','dielectric_constant_value','frequency_from_caption','frequency_from_headers','row_headers','specifier','caption'])

s = 'the refractive index is measured at 485 nm'
# print (get_wavelength_fromcaption(s))

count = 0
# f = open(r'F:\rsc_dielectric_constant\{}.html'.format(1), 'rb')
# d = Document.from_file(f)
# for t in d.tables:
#     print (t.tde_table)


for i in range(1,15932,1):
    try:
        f = open(r'F:\papers\static_dielectric_constant\springer/{}.html'.format(i), 'rb')
        d = Document.from_file(f)
        #d.models = [DielectricConstant]
        #print (d.records.serialize())
        dielectric = ['dielectric', 'Dielectric', 'optical', 'Optical', 'Optics', 'optics', 'permittivity','Permittivity', 'εr', "ε'", "ε'r"]
        for t in d.tables:
            string = ''
            category_table = t.tde_table.category_table
            for k in category_table:
                for j in k:
                    if isinstance(j, str):
                        string += ', ' + j
                    else:
                        string += ', '.join(j)
            #print(string)
            if not any(x in string for x in dielectric) or any(x in t.caption for x in dielectric):
                continue
            try:
                DOI = d.metadata.serialize()['doi']
                table = t.tde_table.pre_cleaned_table.tolist()
                table_transposed = t.tde_table.pre_cleaned_table.transpose().tolist()
                caption = str(t.caption)
                clean_strip(table)
                clean_strip(table_transposed)
                count = find_frequency_specifier_index_firstlayer(table,caption,DOI,count)
                count = find_frequency_specifier_index_secondlayer(table, caption, DOI, count)
                count = find_frequency_specifier_index_firstlayer(table_transposed, caption, DOI, count)
                count = find_frequency_specifier_index_secondlayer(table_transposed, caption, DOI, count)
                #print (find_frequency_specifier_index_firstlayer(table,caption,DOI,count))
                #print(t.records.serialize())
            except:
                pass
    except Exception as e:
        print (e)
        pass
    print ('{} is done, count = {}'.format(i,count))

# if True:
#     for i in range(0,168999):
#         path = r'F:\el_refractive_index_volumn_2000-2020\{}.xml'.format(i)
#         try:
#             f = open(path, 'rb')
#             d = Document.from_file(f)
#             DOI = str(d.metadata.serialize())
#             # f = open(path, 'rb')
#             # f1 = open(path, 'rb').read()
#             # d = Document.from_file(f)
#             # root = ET.fromstring(f1)
#             # Journal = 'None'
#             # DOI = 'None'
#             # for child in root:
#             #     for cchild in child:
#             #         if cchild.tag == '{http://prismstandard.org/namespaces/basic/2.0/}publicationName':
#             #             Journal = cchild.text[:]
#             #         elif cchild.tag == '{http://prismstandard.org/namespaces/basic/2.0/}doi':
#             #             DOI = cchild.text[:]
#
#             for t in d.tables:
#                 try:
#                     table = t.tde_table.pre_cleaned_table.tolist()
#                     table_transposed = t.tde_table.pre_cleaned_table.transpose().tolist()
#                     #print (table)
#                     #print (table_transposed)
#                     caption = str(t.caption)
#                     clean_strip(table)
#                     clean_strip(table_transposed)
#                     count = find_wavelength_specifier_index_firstlayer(table,caption,DOI,count)
#                     count = find_wavelength_specifier_index_secondlayer(table, caption, DOI, count)
#                     count = find_wavelength_specifier_index_firstlayer(table_transposed, caption, DOI, count)
#                     count = find_wavelength_specifier_index_secondlayer(table_transposed, caption, DOI, count)
#                 except Exception as e:
#                     print (e)
#                     pass
#
#
#         except Exception as e:
#             print (e)
#             pass
#         print ('{} is done, count = {}'.format(i,count))

# #for i in range(10):
# table = tabledataextractor.input.from_html.read_file(path,table_number = i)

# print (table)
#
# for i in range(3,4):
#     f = open(r'F:\rsc_refractive_index\{}.html'.format(i),'rb')
#     doc = Document.from_file(f)
#     #doc.models = [RefractiveIndex]
#     for table in doc.tables:
#         print (table.tde_table)
#         for record in table.records:
#             print (record.serialize())