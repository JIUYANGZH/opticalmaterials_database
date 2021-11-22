import chemdataextractor
from chemdataextractor import Document
from shutil import copyfile
import os


f = open(r'F:\papers\refractive_index\el_refractive_index_volumn_2000-2020\0.xml','rb')
d = Document.from_file(f)

print(type(d.paragraphs[-2].sentences[0].text))

c = 0
for file in os.listdir(r'F:\papers\static_dielectric_constant\elsevier/'):
    c += 1
    if c % 500 == 0:
        print(c)
    try:
        f = open(r'F:\papers\static_dielectric_constant\elsevier/'+file, 'rb')
        d = Document.from_file(f)
        name = d.metadata.serialize()['doi']
        name = name.replace('/','#')
        copyfile(r'F:\papers\static_dielectric_constant\elsevier/'+file,r'F:\papers\dielectric_constant\total/{}.xml'.format(name))
        #print(name)
    except:
        pass


c = 0
for file in os.listdir(r'F:\papers\static_dielectric_constant\rsc/'):
    c += 1
    if c % 500 == 0:
        print(c)
    try:
        f = open(r'F:\papers\static_dielectric_constant\rsc/'+file, 'rb')
        d = Document.from_file(f)
        name = d.metadata.serialize()['doi']
        name = name.replace('/','#')
        copyfile(r'F:\papers\static_dielectric_constant\rsc/'+file,r'F:\papers\dielectric_constant\total/{}.html'.format(name))
        #print(name)
    except:
        pass


c = 0
for file in os.listdir(r'F:\papers\static_dielectric_constant\springer/'):
    c += 1
    if c % 500 == 0:
        print(c)
    try:
        f = open(r'F:\papers\static_dielectric_constant\springer/'+file, 'rb')
        d = Document.from_file(f)
        name = d.metadata.serialize()['doi']
        name = name.replace('/','#')
        copyfile(r'F:\papers\static_dielectric_constant\springer/'+file,r'F:\papers\dielectric_constant\total/{}.html'.format(name))
        #print(name)
    except:
        pass