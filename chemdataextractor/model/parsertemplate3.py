
from chemdataextractor.parse.cem import cem,lenient_chemical_label
from chemdataextractor.utils import first
from chemdataextractor.parse.cem import chemical_name,chemical_label
#from chemdataextractor.model import Compound
from chemdataextractor.parse import R, I, W, Optional, merge
from chemdataextractor.parse.base import BaseSentenceParser
#from chemdataextractor.model import Compound
from chemdataextractor.parse.common import lbrct, dt, rbrct
from chemdataextractor.parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore, SkipTo
import re
from chemdataextractor.parse.auto import BaseAutoParser,construct_unit_element,Group,match_dimensions_of,value_element,value_element_plain
from chemdataextractor.parse.actions import merge, join
from lxml import etree
import logging
log = logging.getLogger(__name__)



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
        inumber = (R('\d*\.?\d*[i]$')).add_action(join)
        # inumber = R('^([-+]?(\d+\.?\d*|\d*\.?\d+)([Ee][-+]?[0-2]?\d{1,2})?[r]?|[-+]?((\d+\.?\d*|\d*\.?\d+)([Ee][-+]?[0-2]?\d{1,2})?)?[i]|[-+]?(\d+\.?\d*|\d*\.?\d+)([Ee][-+]?[0-2]?\d{1,2})?[r]?[-+]((\d+\.?\d*|\d*\.?\d+)([Ee][-+]?[0-2]?\d{1,2})?)?[i])$')
        ivalue = (R('\d*\.?\d*$') + R('^[\+\-–−]?') + inumber).add_action(join)
        value = Optional(lbrct).hide() + (ivalue | value_range | value_single)('raw_value') + Not(I('wt%')|I('vol%')|I('K')|I('times')|I('GPa')|I('wt')|I('vol')|I('%')|I('nm')|I('zF')|W('°')|W('KV')|W('kV')|W('MV')|I('kHz')|I('Hz')|I('GHz')|W('V')|W('J')|W('eV')|I('MHz')) + Optional(rbrct).hide()
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
    def article(self):
        return (I('a')|I('an')|I('the'))

    @property
    def have(self):
        return (I('own')|I('owns')|I('have')|I('has')|I('process')|I('processes')|I('holds')|I('experiences')|I('retains')|I('hold')|I('experience')|I('retain')|I('carry')|I('carries')|I('admits')|I('admit')|I('take')|I('takes'))

    @property
    def passive_had(self):
        return (I('found') | I('determined') | I('estimated') | I('measured') | I('afforded') | I('obtained') | I('yielded'))

    @property
    def passive_be(self):
        return (I('was')|I('is')|I('are')|I('were')|I('been'))
    @property
    def between_cem_specifier(self):
        return ( self.passive_be +
         + self.passive_had
        (I('to')|I('that')|I('which')) + self.have + self.article | self.have + self.article)


    @property
    def between_value_cem(self):
        return (self.passive_be + self.passive_had + (I('to')|I('that')|I('which')) + self.have |self.connection)

    @property
    def connection(self):
        return (I('of')|I('about')|I('for')|I('as') + I('regards')|I('attributed') + I('to')|I('concerning'))

    @property
    def specifier_and_value(self):
        return Group(self.prefix + self.value_phrase)


    '''-jz my parser'''

    @property
    def cem_specifier_value(self):
        return ((Optional(self.cem_phrase)
            + Optional(delim).hide() + Optional(I('samples') | I('system') | I('systems') | I('sample'))
            + Optional(I('that') | I('which') | I('was') | I('since') | I('the')).hide()
            + Optional(I('typically')).hide()
            + Optional(I('exhibits') | I('exhibiting') | R('^show[s]*$') | I('demonstrates') | I('undergoes') | I('has') | I('having') | I('determined') | I('with') | I('where') | I('orders') | (I('is') + Optional(I('classified') + I('as')))).hide()
            + Optional(I('reported') + I('to') + I('have')).hide()
            + Optional(lbrct).hide() + self.specifier_and_value + Optional(rbrct))('root_phrase'))

    @property
    def specifier_cem_value(self):
        return (Optional(I('the') | I('a') | I('an') | I('its') | I('with')).hide() \
                + self.specifier_phrase \
                + Optional(I('of') | I('in') | I('for')).hide() \
                + Optional(
                I('bulk') | I('powdered') | I('doped') | I('the') | I('a') | I('an') | I('these') | I('those') | I('this') | I('that')).hide() \
                + Optional(self.cem_phrase) \
                + Optional(I('is') | I('was') | I('were') | I('occurs') | I('of') | (
                I('can') + I('be') + I('assigned') + Optional(I('at') | I('to')))).hide() \
                + Optional(I('observed') | I('determined') | I('measured') | I('calculated') | I('found')).hide() \
                + Optional(I('in') + I('the') + I('range') + I('of') | I('ranging') + I('from') | I('as') | I('to') + I('be')
                | I('about') | I('over') | (I('higher') | I('lower')) + I('than') | I('above')).hide() \
                + Optional(W('=') | W('~') | W('≈') | W('≃') | I('of') | I('was') | I('is') | I('at') | I('as') | I('near') | I('above') | I('below')).hide()
                + Optional(lbrct).hide() \
                + (self.value_phrase)
                + Optional(rbrct))('root_phrase')


    # Phrases where the CEM is given after both the specifier and the value
    @property
    def specifier_value_cem(self):
        return (Optional(I('below') | I('at')) \
                + self.specifier_and_value \
                + Optional((I('has') + I('been') + I('found') + I('for')) | (
                I('was') + (I('observed') | I('determined') | I('measured') | I('calculated')))).hide() \
                + Optional(I('in') | I('for') | I('of')).hide() \
                + Optional(I('the')).hide() \
                + Optional(R('^[:;,]$')).hide() \
                + Optional(I('bulk') | I('powdered') | I('doped') | (I('thin') + I('film'))).hide()
                + Optional(rbrct) \
                + Optional(self.cem_phrase))('root_phrase')
    @property
    def value_specifier_cem(self):
        return (Optional(I('of')) \
                + self.value_phrase \
                + Optional(delim) \
                + Optional(I('which') | I('that')).hide()
                + Optional(I('has') + I('been') | I('was') | I('is') | I('were')).hide() \
                + Optional(I('found') | I('observed') | I('measured') | I('calculated') | I('determined')).hide()
                + Optional(I('likely') | I('close') | (I('can') + I('be'))).hide() \
                + Optional(I('corresponds') | I('associated')).hide() \
                + Optional(I('to') + I('be') | I('with') | I('is') | I('as')).hide() \
                + Optional(I('the')).hide() \
                + self.specifier_phrase \
                + Optional(I('of') | I('in')).hide() \
                + (self.cem_phrase))('root_phrase')

    @property
    def cem_value_specifier(self):
        return ((self.cem_phrase)
                + Optional((I('is') | I('was') | I('were')) + Optional(I('reported') | I('found') | I('calculate') | I('measured') | I('shown') | I('found'))
                + Optional(I('to'))).hide() \
                + Optional((I('exhibit') | I('exhibits') | I('exhibiting') | R('^show[s]*$') | I('demonstrates') | I('undergoes') | I('have') | I('has') | I('having') | I('determined') | I('with'))).hide() \
                + Optional(I('the') | I('a') | I('an')).hide() \
                + Optional(I('value') | I('values')).hide() \
                + Optional(I('varies') + I('from')).hide() \
                + Optional(W('=') | W('~') | W('≈') | W('≃') | I('was') | I('is') | I('at') | I('as') | I('near') | I('above') | I('below')).hide() \
                + Optional(I('in') + I('the') + I('range') | I('ranging')).hide() \
                + Optional(I('of') | I('about') | I('from') | I('approximately') | I('around') | (I('high') + I('as')) | (I('higher') | I('lower') + I('than'))).hide() \
                + self.value_phrase \
                + Optional(I('as') | I('of') | I('for')).hide() \
                + Optional(I('its') | I('their') | I('the')).hide() + self.specifier_phrase)('root_phrase')


    '''parser template'''

    @property
    def cem_before_specifier_and_value_phrase(self):
        return (
                self.cem_phrase
                + OneOrMore(Not(self.cem_phrase | self.specifier_phrase | self.specifier_and_value) + Any().hide()) #+ self.between_cem_specifier)
                + self.specifier_and_value)('root_phrase')

    @property
    def specifier_before_cem_and_value_phrase(self):
        return (
                self.specifier_phrase
                + OneOrMore(Not(self.cem_phrase | self.specifier_phrase | self.value_phrase) + Any().hide())#+ self.connection + Optional(self.article))
                + self.cem_phrase
                + OneOrMore(Not(self.cem_phrase | self.specifier_phrase | I('dielectric') + I('constant')| self.value_phrase | I('not')) + Any().hide())
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
        root_phrase = (self.cem_specifier_value|self.specifier_cem_value|self.specifier_value_cem|self.value_specifier_cem|self.cem_value_specifier)('root_phrase')
        return root_phrase


class MultiQuantityModelTemplateParser(BaseAutoParser, BaseSentenceParser):
    """Template for parsing sentences that contain nested or chained entities
        MULTIPLE ENTITY PHRASES
        1) Single compound, multiple specifiers, multiple phase transitions e.g. BiFeO3 has TC = 1093 K and TN = 640 K
        2) single compound, single specifier, multiple transitions e.g. BiFeO3 shows magnetic transitions at 1093 and 640 K
        3) multiple compounds, single specifier, multiple transitions e.g. TC in BiFeO3 and LaFeO3 of 640 and 750 K
        4) multiple compounds, single specifier, single transition e.g. TC of 640 K in BifEO3, LaFeO3 and MnO
        5) multiple compounds, multiple specifiers, multiple transitions e.g. BiFeO3 and LaFeO3 have Tc = 640 K and TN = 750 K respectively
    Arguments:
        BaseAutoParser {[type]} -- [description]
        BaseSentenceParser {[type]} -- [description]
    """

    @property
    def specifier_phrase(self):
        """Specifier Phrase"""
        return self.model.specifier.parse_expression('specifier')

    @property
    def prefix(self):
        """Specifier and prefix"""
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
    def pure_prefix(self):

        return (Optional((I('varies') + I('from')) |I('from')|
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
                    + (Optional(I('ranging') + I('from')).hide()|Optional(I('the') + I('range') + I('from')).hide())
                    + Optional(I('of')).hide()
                    + Optional(I('rather') | I('quite')).hide()
                    + Optional(I('high') | I('low') | I('maximum') | I('minimum')).hide()
                    + Optional(I('the')).hide()
                    + Optional(delim | lbrct | rbrct)
                    + Optional(
                        I('of') | I('about') | I('approximately') | I('typically') | I('ca.') | I('around') | I(
                            'at') | I(
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
    def single_cem(self):
        """Any cem"""
        return Group(cem | chemical_label | Group(chemical_name)('compound'))

    @property
    def unit(self):
        """Unit element"""
        return Group(construct_unit_element(self.model.dimensions).with_condition(
            match_dimensions_of(self.model))('raw_units'))

    @property
    def value_with_optional_unit(self):
        """Value possibly followed by a unit"""
        value = value_element_plain()
        #return Group(value + Optional(self.unit))
        return value_element_plain()

    @property
    def value_phrase(self):
        """Value with unit"""
        #return value_element(self.unit)
        return value_element_plain()

    @property
    def list_of_values(self):
        """List of values with either multiple units or one at the end"""
        # option 1: single unit at the end
        option_1 = (self.value_with_optional_unit
                         #+ Optional(OneOrMore(delim.hide() + self.value_with_optional_unit))
                         #+ Optional(delim).hide()
                         + I('and').hide()
                         #+ Optional(delim).hide()
                         + self.value_phrase)('value_list')
        # option 2: Multiple units
        option_2 = (self.value_phrase
                    + Optional(OneOrMore(delim.hide() + self.value_phrase))
                    + Optional(delim).hide()
                    + (I('and') | I('or') | delim).hide()
                    + self.value_phrase)('value_list')
        return option_1

    @property
    def list_of_cems(self):
        """List of cems e.g. cem, cem, cem and cem"""
        return Group(self.single_cem
                     + Optional(lbrct + R('^\d+$') + rbrct).hide()
                     + ZeroOrMore(delim.hide() | self.single_cem | R('^\d+$'))
                     + (I('and') | I('or')| I('to')).hide()
                     + self.single_cem
                     + Optional(lbrct + R('^\d+$') + rbrct).hide()
                     + Optional(I('compounds') | I('samples'))
                     )('cem_list')


    @property
    def single_specifier_and_value_with_optional_unit(self):
        """Specifier plus value and possible unit"""
        return Group(self.prefix + self.value_with_optional_unit)('property')

    @property
    def single_specifier_and_value(self):
        """Specifier value and unit"""
        return Group(self.prefix + self.value_phrase)('property')

    @property
    def list_of_properties(self):
        """List of specifiers and units"""
        return Group(Optional(lbrct).hide()
                     + self.single_specifier_and_value_with_optional_unit
                     + (I('and') |I('or') |delim | (I('that') + I('exhibits'))).hide()
                     + self.single_specifier_and_value
                     + Optional(rbrct).hide())('property_list')

    @property
    def value_and_cem(self):
        return Group(self.value_phrase + I('in') +  self.single_cem)('value_and_cem')

    @property
    def multi_entity_phrase_1(self):
        """Single compound, multiple specifiers, values
         e.g. BiFeO3 has TC1 = 1093 K and Tc2 = 640 K
        """
        return Group(self.single_cem
                     + OneOrMore(Not(self.single_cem | self.specifier_phrase | self.value_phrase) + Any().hide())
                     + self.list_of_properties)('multi_entity_phrase_1')

    @property
    def multi_entity_phrase_2(self):
        """single compound, single specifier, multiple transitions
        e.g. BiFeO3 shows magnetic transitions at 1093 and 640 K
        """
        return Group(self.single_cem
                     + OneOrMore(Not(self.single_cem | self.specifier_phrase | self.value_phrase) + Any().hide())
                     + self.specifier_phrase
                     + OneOrMore(Not(self.single_cem | self.specifier_phrase | self.value_phrase) + Any().hide())
                     + self.list_of_values
                     + Optional(delim).hide()
                     + Optional(I('respectively')))('multi_entity_phrase_2')

    @property
    def multi_entity_phrase_3a(self):
        """multiple compounds, single specifier, multiple transitions cems first
        e.g. TC in BiFeO3 and LaFeO3 of 640 and 750 K
        """
        return Group(Optional(self.specifier_phrase)
                     + Optional(I('in') | I('for')).hide()
                     + self.list_of_cems
                     + OneOrMore(Not(self.single_cem | self.specifier_phrase | self.value_phrase) + Any().hide())
                     + self.pure_prefix
                     + self.list_of_values
                     + Optional(delim.hide() + I('respectively').hide()))('multi_entity_phrase_3')

    @property
    def multi_entity_phrase_3b(self):
        """multiple compounds, single specifier, multiple transitions cems last
        e.g. Tc = 750 and 640 K in LaFeO3 and BiFeO3, respectivel
        """
        return Group(self.prefix
                     + self.list_of_values
                     + Optional(I('in') | I('for'))
                     + self.list_of_cems
                     + Optional(delim + I('respectively')))('multi_entity_phrase_3')

    @property
    def multi_entity_phrase_3c(self):
        """multiple compounds, single specifier, multiple transitions cems last
        e.g. curie temperatures from 100 K in MnO to 300 K in NiO
        """
        return Group(self.specifier_phrase + self.pure_prefix + self.value_phrase('value1') + (I('for')|I('in')|I('of'))
                     +  self.single_cem('cem1') + (Optional(I('up')) + I('to')|I('to')).hide()
                     + self.value_phrase('value2') + (I('for')|I('in')|I('of')) +  self.single_cem('cem2'))('multi_entity_phrase_3c')

    @property
    def multi_entity_phrase_3(self):
        """Combined phrases of type 3"""
        return Group(self.multi_entity_phrase_3a | self.multi_entity_phrase_3b)# | self.multi_entity_phrase_3c)


    @property
    def multi_entity_phrase_4a(self):
        """multiple compounds, single specifier, single transition
        e.g. TC of 640 K in BifEO3, LaFeO3 and MnO
        """
        return Group(self.single_specifier_and_value
                     + OneOrMore(Not(self.single_cem | self.specifier_phrase | self.value_phrase) + Any().hide())
                     + self.list_of_cems)('multi_entity_phrase_4')

    @property
    def multi_entity_phrase_4b(self):
        """Cems first"""
        return Group(self.list_of_cems
                     + OneOrMore(Not(self.single_cem | self.specifier_phrase | self.value_phrase) + Any().hide())
                     + self.single_specifier_and_value)('multi_entity_phrase_4')

    @property
    def multi_entity_phrase_4(self):
        return Group(self.multi_entity_phrase_4a | self.multi_entity_phrase_4b)

    @property
    def root(self):
        return (
            self.multi_entity_phrase_1 | self.multi_entity_phrase_2 | self.multi_entity_phrase_3 | self.multi_entity_phrase_3c | self.multi_entity_phrase_4)

    def interpret(self, result, start, end):
        if result.tag == 'multi_entity_phrase_1':
            for model in self.interpret_multi_entity_1(result, start, end):
                yield model
        elif result.tag == 'multi_entity_phrase_2':
            for model in self.interpret_multi_entity_2(result, start, end):
                yield model
        elif result.tag == 'multi_entity_phrase_3':
            for model in self.interpret_multi_entity_3(result, start, end):
                yield model
        elif result.tag == 'multi_entity_phrase_3c':
            #print (1)
            for model in self.interpret_multi_entity_3c(result, start, end):
                yield model
        elif result.tag == 'multi_entity_phrase_4':
            for model in self.interpret_multi_entity_4(result, start, end):
                yield model
        else:
            yield None

    def interpret_multi_entity_1(self, result, start, end):
        """Interpret phrases that have a single CEM and multiple values with multiple specifiers
        """
        if result is None:
            return

        cem_el = first(result.xpath('./compound'))
        if cem_el is None:
            yield None

        property_list = first(result.xpath('./property_list'))
        if property_list is None:
            yield None

        c = self.model.compound.model_class()
        # add names and labels
        c.names = cem_el.xpath('./names/text()')
        c.labels = cem_el.xpath('./labels/text()')

        properties = property_list.xpath('./property')
        last_unit = None
        for pt in properties[::-1]:  # Reverse order to make sure we get a unit
            requirements = True
            specifier = first(pt.xpath('./specifier/text()'))
            raw_value = first(pt.xpath('./raw_value/text()'))
            raw_units = first(pt.xpath('./raw_units/text()'))
            if not raw_units:
                raw_units = last_unit
            else:
                last_unit = raw_units

            value = self.extract_value(raw_value)
            error = self.extract_error(raw_value)
            units = None
            try:
                units = self.extract_units(raw_units, strict=True)
            except TypeError as e:
                #requirements = False
                log.debug(e)

            property_entities = {
                'specifier': specifier,
                'raw_value': raw_value,
                'raw_units': raw_units,
                'error': error,
                'value': value,
                'units': units,
                'compound': c}

            model_instance = self.model(**property_entities)
            if requirements:
                yield model_instance

    def interpret_multi_entity_2(self, result, start, end):
        """single compound, single specifier, multiple transitions e.g. BiFeO3 shows magnetic transitions at 1093 and 640 K
        """
        if result is None:
            return
        cem_el = first(result.xpath('./compound'))

        if cem_el is None:
            yield None
        specifier = first(result.xpath('./specifier/text()'))
        if specifier is None:
            yield None

        value_list = first(result.xpath('./value_list'))

        if value_list is None:
            yield None

        c = self.model.compound.model_class()
        # add names and labels
        c.names = cem_el.xpath('./names/text()')
        c.labels = cem_el.xpath('./labels/text()')

        raw_values_list = value_list.xpath('./raw_value')
        raw_units_list = value_list.xpath('./raw_units')

        last_unit = None
        for i, v in enumerate(raw_values_list[::-1]):  # Reverse order to make sure we get a unit
            raw_value = first(v.xpath('./text()'))
            requirements = True
            raw_units = None
            try:
                raw_units = first(raw_units_list[::-1][i].xpath('./text()'))
                last_unit = raw_units
            except IndexError:
                if last_unit:
                    raw_units = last_unit
                #else:
                    #requirements = False

            value = self.extract_value(raw_value)
            error = self.extract_error(raw_value)
            units = None
            try:
                units = self.extract_units(raw_units, strict=True)
            except Exception as e:
                #requirements = False
                log.debug(e)
                pass

            property_entities = {
                'specifier': specifier,
                'raw_value': raw_value,
                'raw_units': raw_units,
                'error': error,
                'value': value,
                'units': units,
                'compound': c}

            model_instance = self.model(**property_entities)
            if requirements:
                yield model_instance




    def interpret_multi_entity_3(self, result, start, end):
        """interpret multiple compounds, single specifier, multiple transitions"""
        if result is None:
            return
        cem_list = first(result.xpath('./cem_list'))
        #print (cem_list)
        if cem_list is None:
            yield None

        specifier = first(result.xpath('//multi_entity_phrase_3/specifier/text()'))
        #print (specifier)
        if specifier is None:
            yield None

        value_list = first(result.xpath('//multi_entity_phrase_3/value_list'))
        #print (value_list)



        if value_list is None:
            yield None

        raw_values_list = value_list.xpath('./raw_value')
        raw_units_list = value_list.xpath('./raw_units')

        #value_cem_list = first(result.xpath('//multi_entity_phrase_3/value_and_cem'))
        #print(value_cem_list.xpath('./raw_value'))


        last_unit = None
        for i, v in enumerate(raw_values_list[::-1]):  # Reverse order to make sure we get a unit
            raw_value = first(v.xpath('./text()'))
            #print (raw_value)
            requirements = True
            raw_units = None
            try:
                raw_units = first(raw_units_list[::-1][i].xpath('./text()'))
                last_unit = raw_units
            except IndexError:
                if last_unit:
                    raw_units = last_unit
                # else:
                #     requirements = False
            c = None
            try:
                compound = cem_list[::-1][i]
                c = self.model.compound.model_class(
                    names=compound.xpath('./names/text()'),
                    labels=compound.xpath('./labels/text()'))
                #print (compound.xpath('//names/text()'))
            except Exception:
                requirements = False

            value = self.extract_value(raw_value)
            error = self.extract_error(raw_value)
            units = None
            try:
                units = self.extract_units(raw_units, strict=True)
            except TypeError as e:
                #requirements = False
                log.debug(e)
            property_entities = {
                'specifier': specifier,
                'raw_value': raw_value,
                'raw_units': raw_units,
                'error': error,
                'value': value,
                'units': units,
                'compound': c}

            model_instance = self.model(**property_entities)
            if requirements:
                yield model_instance

    def interpret_multi_entity_3c(self, result, start, end):
        """interpret multiple compounds, single specifier, multiple transitions"""
        if result is None:
            return
        specifier = first(result.xpath('//multi_entity_phrase_3c/specifier/text()'))
        if specifier is None:
            yield None

        values = [first(result.xpath('//multi_entity_phrase_3c/value1/raw_value/text()')),first(result.xpath('//multi_entity_phrase_3c/value2/raw_value/text()'))]
        compounds = [first(result.xpath('//multi_entity_phrase_3c/cem1/compound/names/text()')),first(result.xpath('//multi_entity_phrase_3c/cem2/compound/names/text()'))]
        if values is None:
            yield None
        if compounds is None:
            yield None
        requirements = True

        last_unit = None
        for i in range(2):
            raw_value = values[i]
            raw_units = None
            c = self.model.compound.model_class(
                names=[compounds[i]])
            value = self.extract_value(raw_value)
            error = self.extract_error(raw_value)
            units = None
            try:
                units = self.extract_units(raw_units, strict=True)
            except TypeError as e:
                #requirements = False
                log.debug(e)
            #print (specifier,raw_value,raw_units,error,value,units,c)
            property_entities = {
                'specifier': specifier,
                'raw_value': raw_value,
                'raw_units': raw_units,
                'error': error,
                'value': value,
                'units': units,
                'compound': c}

            model_instance = self.model(**property_entities)
            if requirements:
                yield model_instance



    def interpret_multi_entity_4(self, result, start, end):
        """interpret multiple compounds, single specifier, single transition"""
        if result is None:
            return
        requirements = True

        cem_list = first(result.xpath('./cem_list'))

        if cem_list is None:
            yield None
        raw_units = None
        specifier = first(result.xpath('./property/specifier/text()'))
        raw_value = first(result.xpath('./property/raw_value/text()'))
        raw_units = first(result.xpath('./property/raw_units/text()'))

        if specifier is None:
            yield None

        value = self.extract_value(raw_value)
        error = self.extract_error(raw_value)
        units = None
        try:
            units = self.extract_units(raw_units, strict=True)
        except TypeError as e:
            #requirements = False
            log.debug(e)

        for cem in cem_list:  # Reverse order to make sure we get a unit
            c = None
            try:
                c = self.model.compound.model_class(
                    names=cem.xpath('./names/text()',
                                    labels=cem.xpath('./labels/text()')))
            except Exception:
                requirements = False

            property_entities = {
                'specifier': specifier,
                'raw_value': raw_value,
                'raw_units': raw_units,
                'error': error,
                'value': value,
                'units': units,
                'compound': c}

            model_instance = self.model(**property_entities)
            if requirements:
                yield model_instance