#from chemdataextractor.doc import Sentence
from chemdataextractor.parse import R,I,W,Optional,merge,join
from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.utils import first


dielectriclost = R('^[0]\.[0][0-9]+]?')('dielectricloss')



class DielectricLossParser(BaseSentenceParser):
    root = dielectriclost

    def interpret(self, result, start, end):
        raw_value = first(result.xpath('//dielectricloss/text()'))
        #print (type(raw_value))
        frequency = self.model(dielectricloss=raw_value)
        #print (frequency)
        yield frequency