# -*- coding: utf-8 -*-
"""
chemdataextractor.units.dipole_moment.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Units and models for dipole_moment


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .quantity_model import QuantityModel
from .unit import Unit
from .dimension import Dimension
from ...parse.elements import R
from .charge import Charge
from .length import Length
import logging

log = logging.getLogger(__name__)


class Dipole_moment(Dimension):
    """
    Dimension subclass for dipole_moment
    """
    constituent_dimensions =  Charge() * Length()
    #pass




class Dipole_momentUnit(Unit):
    """
    Base class for units with dimensions of dipole_moment
    The standard value for current is defined to be an Debye, implemented in the Debye class.
    """

    def __init__(self, magnitude=0.0, powers=None):
        super(Dipole_momentUnit, self).__init__(Dipole_moment(), magnitude, powers)


class Debye(Dipole_momentUnit):
    """
    class for Debye
    """

    def convert_value_to_standard(self, value):
        return value * 3.033564e29

    def convert_value_from_standard(self, value):
        return value / 3.033564e29

    def convert_error_to_standard(self, error):
        return error * 3.033564e29

    def convert_error_from_standard(self, error):
        return error / 3.033564e29


units_dict = {R('(D|d)(ebye(s)?)?', group=0): Debye}
Dipole_moment.units_dict.update(units_dict)
Dipole_moment.standard_units = Debye()


class Dipole_momentModel(QuantityModel):
    """
    Model for dipole_moment
    """
    dimensions = Dipole_moment()