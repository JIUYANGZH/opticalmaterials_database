#from chemdataextractor.doc import Sentence
from chemdataextractor.parse import R,I,W,Optional,merge,join
from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.utils import first


frequency_value = (I('excited')|I('ground'))('excited')


class DipoleMomentExcitedParser(BaseSentenceParser):
    root = frequency_value

    def interpret(self, result, start, end):
        raw_value = first(result.xpath('//excited/text()'))
        #print (type(raw_value))
        frequency = self.model(state=raw_value)
        #print (frequency)
        yield frequency