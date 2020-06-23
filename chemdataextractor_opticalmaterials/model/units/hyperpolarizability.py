# -*- coding: utf-8 -*-
"""
chemdataextractor.units.hyperpolarizability.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Units and models for hyperpolarizability


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .quantity_model import QuantityModel
from .unit import Unit
from .dimension import Dimension
from ...parse.elements import R,I
from .charge import Charge
from .energy import Energy
from .length import Length
import logging

log = logging.getLogger(__name__)


class Hyperpolarizability(Dimension):
    """
    Dimension subclass for hyperpolarizability
    """
    constituent_dimensions =  (Charge() **3  * Length() **3 * Energy() ** -2)
    #pass




class HyperpolarizabilityUnit(Unit):
    """
    Base class for units with dimensions of hyperpolarizability
    The standard value for current is defined to be an esu, implemented in the esu class.
    """

    def __init__(self, magnitude=0.0, powers=None):
        super(HyperpolarizabilityUnit, self).__init__(Hyperpolarizability(), magnitude, powers)


class esu(HyperpolarizabilityUnit):
    """
    class for esu.
    """

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error

class au(HyperpolarizabilityUnit):
    """
    class for esu.
    """

    def convert_value_to_standard(self, value):
        return value * 8.641e-33

    def convert_value_from_standard(self, value):
        return value / 8.641e-33

    def convert_error_to_standard(self, error):
        return error * 8.641e-33

    def convert_error_from_standard(self, error):
        return error / 8.641e-33


class esu1(HyperpolarizabilityUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error

units_dict = {R(r'^esu$', group=0): esu,
              R(r'^a(\.)?u(\.)?$'): au}
Hyperpolarizability.units_dict.update(units_dict)
#print('original:', Hyperpolarizability.units_dict)
Hyperpolarizability.standard_units = esu()


class HyperpolarizabilityModel(QuantityModel):
    """
    Model for electrical hyperpolarizability
    """
    dimensions = Hyperpolarizability()

