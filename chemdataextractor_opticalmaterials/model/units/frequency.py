# -*- coding: utf-8 -*-
"""
chemdataextractor.units.frequency.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Units and models for frequency


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .quantity_model import QuantityModel
from .unit import Unit
from .dimension import Dimension
from ...parse.elements import R
from .time import Time
import logging

log = logging.getLogger(__name__)


class Frequency(Dimension):
    """
    Dimension subclass for electrical current.
    """
    constituent_dimensions =  Time() ** -1
    #pass


class FrequencyModel(QuantityModel):
    """
    Model for electrical current.
    """
    dimensions = Frequency()


class FrequencyUnit(Unit):
    """
    Base class for units with dimensions of electrical current.
    The standard value for current is defined to be an ampere, implemented in the Ampere class.
    """

    def __init__(self, magnitude=0.0, powers=None):
        super(FrequencyUnit, self).__init__(Frequency(), magnitude, powers)


class Hertz(FrequencyUnit):
    """
    class for amps.
    """

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('Hz', group=0): Hertz}
Frequency.units_dict.update(units_dict)
Frequency.standard_units = Hertz()
