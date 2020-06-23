"""
Model classes for physical properties.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import six

from .base import BaseModel, StringType, ListType, ModelType
from .units.temperature import TemperatureModel
from .units.length import LengthModel
from ..parse.cem import CompoundParser, CompoundHeadingParser, ChemicalLabelParser, names_only, labels_only, roles_only
from ..parse.ir import IrParser
from ..parse.mp_new import MpParser
from ..parse.nmr import NmrParser
from ..parse.tg import TgParser
from ..parse.uvvis import UvvisParser
from ..parse.elements import R, I, Optional, W,Not,Any
from ..parse.actions import merge, join
from ..model.units.quantity_model import QuantityModel, DimensionlessModel
from ..parse.auto import AutoTableParser, AutoSentenceParser
from ..parse.apparatus import ApparatusParser
from chemdataextractor.model.parsertemplate1 import PropertyParserTemplate,MultiQuantityModelTemplateParser
from chemdataextractor.model.parsetemplate_unit import PropertyParserTemplate_unit,MultiQuantityModelTemplateParser_unit
from chemdataextractor.model.rn_wavelength_parser import RefractiveIndexWavelengthParser
from chemdataextractor.model.dc_frequency_parser import DielectricConstantFrequencyParser
from chemdataextractor.model.dielectricloss_parser import DielectricLossParser
from chemdataextractor.model.excited_state import DipoleMomentExcitedParser
from chemdataextractor.model.units.time import TimeModel
from chemdataextractor.model.units.frequency import FrequencyModel
from chemdataextractor.model.units.dipole_moment import Dipole_momentModel
from chemdataextractor.model.units.hyperpolarizability import HyperpolarizabilityModel
from chemdataextractor.model.units.energy import EnergyModel
from chemdataextractor.parse.quantity import value_element_plain
log = logging.getLogger(__name__)


class Compound(BaseModel):
    names = ListType(StringType(), parse_expression=names_only)
    labels = ListType(StringType(), parse_expression=labels_only)
    roles = ListType(StringType(), parse_expression=roles_only)
    parsers = [CompoundParser(), CompoundHeadingParser(), ChemicalLabelParser()]

    def merge(self, other):
        """Merge data from another Compound into this Compound."""
        log.debug('Merging: %s and %s' % (self.serialize(), other.serialize()))
        for k in self.keys():
            for new_item in other[k]:
                if new_item not in self[k]:
                    self[k].append(new_item)
        log.debug('Result: %s' % self.serialize())
        return self

    @property
    def is_unidentified(self):
        if not self.names and not self.labels:
            return True
        return False

    @property
    def is_id_only(self):
        """Return True if identifier information only."""
        for key, value in self.items():
            if key not in {'names', 'labels', 'roles'} and value:
                return False
        if self.names or self.labels:
            return True
        return False


class Apparatus(BaseModel):
    name = StringType()
    parsers = [ApparatusParser()]


class UvvisPeak(BaseModel):
    #: Peak value, i.e. wavelength
    value = StringType()
    #: Peak value units
    units = StringType(contextual=True)
    # Extinction value
    extinction = StringType()
    # Extinction units
    extinction_units = StringType(contextual=True)
    # Peak shape information (e.g. shoulder, broad)
    shape = StringType()


class UvvisSpectrum(BaseModel):
    solvent = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = ModelType(Apparatus, contextual=True)
    peaks = ListType(ModelType(UvvisPeak))
    compound = ModelType(Compound)
    parsers = [UvvisParser()]


class IrPeak(BaseModel):
    value = StringType()
    units = StringType(contextual=True)
    strength = StringType()
    bond = StringType()


class IrSpectrum(BaseModel):
    solvent = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = ModelType(Apparatus, contextual=True)
    peaks = ListType(ModelType(IrPeak))
    compound = ModelType(Compound)
    parsers = [IrParser()]


class NmrPeak(BaseModel):
    shift = StringType()
    intensity = StringType()
    multiplicity = StringType()
    coupling = StringType()
    coupling_units = StringType(contextual=True)
    number = StringType()
    assignment = StringType()


class NmrSpectrum(BaseModel):
    nucleus = StringType(contextual=True)
    solvent = StringType(contextual=True)
    frequency = StringType(contextual=True)
    frequency_units = StringType(contextual=True)
    standard = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = ModelType(Apparatus, contextual=True)
    peaks = ListType(ModelType(NmrPeak))
    compound = ModelType(Compound)
    parsers = [NmrParser()]

class RefractiveIndexWavelength(LengthModel):
    wavelength = StringType()
    parsers = [RefractiveIndexWavelengthParser()]

class DielectricConstantFrequency(TimeModel):
    frequency = StringType()
    parsers = [DielectricConstantFrequencyParser()]

class DielectricLost(DimensionlessModel):
    dielectricloss = StringType()
    parsers = [DielectricLossParser()]

class RefractiveIndex(DimensionlessModel):
    """
    Model for Refractive Index
    """
    specifier_expr = (I('refraction') + I('index') |I('index') +I('of')+ I('refraction') |I('refraction') + I('indices') |I('refractive') + I('indices') |I('refractive') + I('index') | W('n')| W('nD')| W('nF')| W('nC')| W('nexp')| W('nlit')| W('nav') | I('R.I.')| I('R.I')| I('RI')).add_action(join)
    specifier = StringType(parse_expression=specifier_expr, required=True, contextual=False)
    compound = ModelType(Compound, required=True, contextual=False)
    wavelength = ModelType(RefractiveIndexWavelength,required=False)
    parsers = [PropertyParserTemplate(),AutoSentenceParser(),AutoTableParser(),MultiQuantityModelTemplateParser()]

class ExcitedState(DimensionlessModel):
    state = StringType()
    parsers = [DipoleMomentExcitedParser()]

class Dipole_moment(Dipole_momentModel):
    parse_expression = (Optional(I('static')) + R('(D|d)(ipole?)?') + R('(M|m)(oment(s)?)')|I('μg')|I('μe')|I('μ')|I('Dipolmoment')).add_action(join)
    specifier = StringType(parse_expression=parse_expression, required=True)
    compound = ModelType(Compound, required=True, contextual=False)
    state = ModelType(ExcitedState, required=False)
    parsers = [AutoSentenceParser(),PropertyParserTemplate_unit(),MultiQuantityModelTemplateParser_unit(),AutoTableParser()]


class Hyperpolarizability(HyperpolarizabilityModel):
    parse_expression = (I('hyperpolarizability') | I('β0') | I('β') | (I('second') + I('order') + I('susceptibility')) | ((I('second') + W('-') + I('order')).add_action(merge) + I('susceptibility'))).add_action(join)
    specifier = StringType(parse_expression=parse_expression, required=True)
    compound = ModelType(Compound, required=True, contextual=False)
    #state = ModelType(ExcitedState, required=False)
    parsers = [PropertyParserTemplate_unit(),AutoTableParser(),AutoSentenceParser(),MultiQuantityModelTemplateParser_unit()]


class DielectricConstant(DimensionlessModel):
    """
    Model for Dielectric Constant
    """
    #specifier_expr = (I('refraction') + I('index') |I('index') +I('of')+ I('refraction') |I('refraction') + I('indices') |I('refractive') + I('indices') |I('refractive') + I('index') | W('n')| W('nD')| W('nF')| W('nC')| W('nexp')| W('nlit')| W('nav') | I('R.I.')| I('R.I')| I('RI')).add_action(join)
    specifier_expr = (Optional(I('static')) + I('dielectric') + I('constants')|Optional(I('static'))+I('dielectric') + I('constant')|Optional(I('static'))+I('relative') + I('permittivity')|Optional(I('static'))+I('dielectric')+I('permittivity')|Optional(I('static'))+I('relative') + I('permittivities')|Optional(I('static'))+I('dielectric')+I('permittivities')|I('εr')|I("ε'")|I('ε')|I("ε'r")).add_action(join)
    specifier = StringType(parse_expression=specifier_expr, required=True, contextual=False)
    compound = ModelType(Compound, required=True, contextual=False)
    frequency = ModelType(DielectricConstantFrequency,required=False)
    dielectricloss = ModelType(DielectricLost,required=False)
    parsers = [PropertyParserTemplate(),MultiQuantityModelTemplateParser(),AutoSentenceParser()]

# class MeltingPoint(BaseModel):
#     """A melting point measurement."""
#     value = StringType()
#     units = StringType(contextual=True)
#     solvent = StringType(contextual=True)
#     concentration = StringType(contextual=True)
#     concentration_units = StringType(contextual=True)
#     apparatus = StringType(contextual=True)


class MeltingPoint(TemperatureModel):
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = ModelType(Apparatus, contextual=True)
    compound = ModelType(Compound, contextual=True)
    parsers = [MpParser()]


class GlassTransition(BaseModel):
    """A glass transition temperature."""
    value = StringType()
    units = StringType(contextual=True)
    method = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    compound = ModelType(Compound)
    parsers = [TgParser()]


class QuantumYield(BaseModel):
    """A quantum yield measurement."""
    value = StringType()
    units = StringType(contextual=True)
    solvent = StringType(contextual=True)
    type = StringType(contextual=True)
    standard = StringType(contextual=True)
    standard_value = StringType(contextual=True)
    standard_solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = ModelType(Apparatus, contextual=True)


class FluorescenceLifetime(BaseModel):
    """A fluorescence lifetime measurement."""
    value = StringType()
    units = StringType(contextual=True)
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = ModelType(Apparatus, contextual=True)


class ElectrochemicalPotential(BaseModel):
    """An oxidation or reduction potential, from cyclic voltammetry."""
    value = StringType()
    units = StringType(contextual=True)
    type = StringType(contextual=True)
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = ModelType(Apparatus, contextual=True)


# TEST MODELS

class NeelTemperature(TemperatureModel):
    # expression = (I('T')+I('N')).add_action(merge)
    expression = I('TN')
    # specifier = I('TN')
    specifier = StringType(parse_expression=expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False)


class CurieTemperature(TemperatureModel):
    # expression = (I('T') + I('C')).add_action(merge)
    expression = I('TC')
    specifier = StringType(parse_expression=expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False)


class InteratomicDistance(LengthModel):
    specifier_expression = (R('^bond$') + R('^distance')).add_action(merge)
    specifier = StringType(parse_expression=specifier_expression, required=False, contextual=True)
    rij_label = R('^((X|Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Cn|Co|Cr|Cs|Cu|Db|Ds|Dy|Er|Es|Eu|F|Fe|Fl|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Lv|Mc|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Nh|Ni|No|Np|O|Og|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|Ts|U|V|W|Xe|Y|Yb|Zn|Zr)\-?(X|Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Cn|Co|Cr|Cs|Cu|Db|Ds|Dy|Er|Es|Eu|F|Fe|Fl|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Lv|Mc|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Nh|Ni|No|Np|O|Og|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|Ts|U|V|W|Xe|Y|Yb|Zn|Zr))$')
    species = StringType(parse_expression=rij_label, required=True, contextual=False)
    compound = ModelType(Compound, required=True, contextual=True)
    another_label = StringType(parse_expression=R('^adgahg$'), required=False, contextual=False)


class CoordinationNumber(DimensionlessModel):
    # something like NTi-O will not work with this, only work if there is space between the label and specifier
    coordination_number_label = R('^((X|Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Cn|Co|Cr|Cs|Cu|Db|Ds|Dy|Er|Es|Eu|F|Fe|Fl|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Lv|Mc|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Nh|Ni|No|Np|O|Og|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|Ts|U|V|W|Xe|Y|Yb|Zn|Zr)\-?(X|Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Cn|Co|Cr|Cs|Cu|Db|Ds|Dy|Er|Es|Eu|F|Fe|Fl|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Lv|Mc|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Nh|Ni|No|Np|O|Og|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|Ts|U|V|W|Xe|Y|Yb|Zn|Zr))$')
    # specifier = (R('^(N|n|k)$') | (I('Pair') + I('ij')).add_action(merge)
    specifier_expression = R('^(N|n|k)$')
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=True)

    cn_label = StringType(parse_expression=coordination_number_label, required=True, contextual=True)
    compound = ModelType(Compound, required=True, contextual=True)


class CNLabel(BaseModel):
    # separate model to test automated parsing for stuff that are not quantities
    coordination_number_label = R('^((X|Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Cn|Co|Cr|Cs|Cu|Db|Ds|Dy|Er|Es|Eu|F|Fe|Fl|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Lv|Mc|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Nh|Ni|No|Np|O|Og|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|Ts|U|V|W|Xe|Y|Yb|Zn|Zr)\-?(X|Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Cn|Co|Cr|Cs|Cu|Db|Ds|Dy|Er|Es|Eu|F|Fe|Fl|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Lv|Mc|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Nh|Ni|No|Np|O|Og|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|Ts|U|V|W|Xe|Y|Yb|Zn|Zr))$')
    specifier = (I('Pair') + I('ij')).add_action(merge)
    label_Juraj = StringType(parse_expression=coordination_number_label)
    compound = ModelType(Compound, required=False)
    parsers = [AutoSentenceParser(), AutoTableParser()]

