from chemdataextractor.doc import Sentence
from chemdataextractor.parse import R,I,W,Optional,merge,join
from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.utils import first


wavelength_value = ((R("^\d+?$") + W('nm')) | (R("^\d+?\.\d+?$") + W('μm')) | (R("^\d+?\.\d+?$") + W('nm')))('wavelengthvalue').add_action(join)



class RefractiveIndexWavelengthParser(BaseSentenceParser):
    root = wavelength_value

    def interpret(self, result, start, end):
        raw_value = first(result.xpath('//wavelengthvalue/text()'))
        wavelength = self.model(wavelength=raw_value)
        yield wavelength