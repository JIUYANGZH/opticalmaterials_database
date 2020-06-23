#from chemdataextractor.doc import Sentence
from chemdataextractor.parse import R,I,W,Optional,merge,join
from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.utils import first


frequency_value = ((R("^\d+?\.\d+?$")|R("^\d+?$"))+ (W('kHz')|W('MHz')|W('GHz')|W('Hz')))('frequencyvalue').add_action(join)



class DielectricConstantFrequencyParser(BaseSentenceParser):
    root = frequency_value

    def interpret(self, result, start, end):
        raw_value = first(result.xpath('//frequencyvalue/text()'))
        #print (type(raw_value))
        frequency = self.model(frequency=raw_value)
        #print (frequency)
        yield frequency