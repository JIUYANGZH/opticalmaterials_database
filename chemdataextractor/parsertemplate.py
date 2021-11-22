
from chemdataextractor.parse.cem import cem,lenient_chemical_label
from chemdataextractor.utils import first
from chemdataextractor.parse.cem import chemical_name,chemical_label
from chemdataextractor.model import Compound
from chemdataextractor.parse import R, I, W, Optional, merge
from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.model import Compound
from chemdataextractor.parse.common import lbrct, dt, rbrct
from chemdataextractor.parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore, SkipTo
import re
from chemdataextractor.parse.auto import BaseAutoParser,construct_unit_element,Group,match_dimensions_of,value_element
from chemdataextractor.parse.actions import merge, join
from lxml import etree


delim = R('^[:;\.,]$')

class PropertyParserTemplate(BaseAutoParser, BaseSentenceParser):
    """Template parser for QuantityModel-type structures

    Finds Cem, Specifier, Value and Units from single sentences

    Other entities are merged contextually

    Returns:
        [type] -- [description]
    """

    @property
    def specifier_phrase(self):
        return self.model.specifier.parse_expression('specifier')

    # @property
    # def value_phrase(self):
    #     unit_element = Group(construct_unit_element(self.model.dimensions).with_condition(
    #         match_dimensions_of(self.model))('raw_units'))
    #     return value_element(unit_element)
    @property
    def value_phrase(self):
        number = R('^[\+\-–−]?\d+(\.\d+)?$')
        joined_range = R('^[\+\-–−]?\d+(\.\d+)?[\-–−~∼˜]\d+(\.\d+)?$')('raw_value').add_action(merge)
        spaced_range = (number + (R('^[\-–−~∼˜]$') + number | number))('raw_value').add_action(
            merge)
        to_range = (number + I('to') + number)('raw_value').add_action(join)
        plusminus_range = (number + R('±') + number)('value').add_action(join)
        value_range = (Optional(R('^[\-–−]$')) + (plusminus_range | joined_range | spaced_range | to_range))(
            'raw_value').add_action(merge)
        value_single = (Optional(R('^[~∼˜\<\>]$')) + Optional(R('^[\-–−]$')) + number)('raw_value').add_action(merge)
        value = Optional(lbrct).hide() + (value_range | value_single)('raw_value') + Optional(rbrct).hide()
        return value


    @property
    def cem_phrase(self):
        return Group(cem | chemical_label | Group(chemical_name)('compound'))

    @property
    def prefix(self):
        return (self.specifier_phrase
                + Optional(I('values')).hide()
                + Optional(delim).hide()
                + Optional((I('varies') + I('from')) |
                           R('^increase(s|d)?') | I('falls') | I('reaches')).hide()
                + Optional(I('steeply')).hide()
                + Optional(I('recorded') | I('reported')).hide()
                + Optional(I('of') | I('was') | I('is') | I('at') | I('near') |
                           I('above') | I('below') | I('with') | I('to') | I('were') | I('a')).hide()
                + Optional(I('reported') | I('determined') |
                           I('estimated') | I('found') | I('occurs')).hide()
                + Optional(I('temperatures')).hide()
                + Optional(I('as') | (I('to') + I('be'))).hide()
                + Optional(I('in') + I('the') + I('range')).hide()
                + Optional(I('as') + I('high') + I('as'))
                + Optional(I('ranging') + I('from')).hide()
                + Optional(I('of')).hide()
                + Optional(I('rather') | I('quite')).hide()
                + Optional(I('high') | I('low') | I('maximum') | I('minimum')).hide()
                + Optional(I('the')).hide()
                + Optional(delim | lbrct | rbrct)
                + Optional(
                    I('of') | I('about') | I('approximately') | I('typically') | I('ca.') | I('around') | I('at') | I(
                        'above') | I('below') | I('high') | I('low')
                    | ((I('higher') | I('lower') | I('more') | I('less')) + I('than')) | I('order') | (
                                I('for') + I('instance')) | (I('up') + I('to')) | I('reaching') | I('value')).hide()
                + Optional(I('a') | I('an') | I('as')).hide()
                + Optional(I('maximum')).hide()
                + Optional(I('of')).hide()
                + ZeroOrMore(lbrct | delim | rbrct)
                + Optional(self.specifier_phrase)
                + Optional(I('of')).hide()
                + Optional(I('the')).hide()
                + Optional(I('order')).hide()
                + Optional((I('up') | I('equal')) + I('to')).hide()
                + Optional(I('of')).hide()
                + ZeroOrMore(lbrct | delim | rbrct)
                + Optional(W('=') | W('~') | W('≈') |
                           W('≃') | W('>') | W('<')).hide()
                + ZeroOrMore(lbrct | delim | rbrct).hide()).add_action(join)

    @property
    def specifier_and_value(self):
        return Group(self.prefix + self.value_phrase)

    @property
    def cem_before_specifier_and_value_phrase(self):
        return (
                self.cem_phrase
                + OneOrMore(Not(self.cem_phrase | self.specifier_phrase | self.specifier_and_value) + Any().hide())
                + self.specifier_and_value)('root_phrase')

    @property
    def specifier_before_cem_and_value_phrase(self):
        return (
                self.specifier_phrase
                + OneOrMore(Not(self.cem_phrase | self.specifier_phrase | self.value_phrase) + Any().hide())
                + self.cem_phrase
                + OneOrMore(Not(self.cem_phrase | self.specifier_phrase | self.value_phrase) + Any().hide())
                + Optional(self.prefix)
                + self.value_phrase)('root_phrase')

    @property
    def cem_after_specifier_and_value_phrase(self):
        return (
                self.specifier_and_value
                + OneOrMore(Not(self.cem_phrase | self.specifier_phrase | self.value_phrase) + Any().hide())
                + self.cem_phrase)('root_phrase')

    @property
    def value_specifier_cem_phrase(self):
        return (self.value_phrase
                + Optional(delim | lbrct | rbrct)
                + Optional(I('which') | I('there')).hide()
                + Optional(I('likely') | I('close') |
                           (I('can') + I('be'))).hide()
                + Optional(I('corresponds') |
                           I('associated') | I('corresponding')).hide()
                + Optional(I('to') | I('with') | I('is')).hide()
                + Optional(I('the') | I('a')).hide()
                + Optional(I('transition')).hide()
                + Optional(I('to').hide())
                + Optional(I('a')).hide()
                + self.specifier_phrase
                + Not(I('='))
                + Not(self.value_phrase)
                + Optional(I('of') | I('in')).hide()
                + self.cem_phrase)('root_phrase')

    @property
    def root(self):
        root_phrase = Group(
            self.specifier_before_cem_and_value_phrase | self.cem_after_specifier_and_value_phrase | self.value_specifier_cem_phrase | self.cem_before_specifier_and_value_phrase | Group(
                self.specifier_and_value)('root_phrase'))
        return root_phrase