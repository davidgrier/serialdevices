# -*- coding: utf-8 -*-

from numpy.random import (normal, uniform)


class SR830Fake(object):

    def __init__(self):
        self.identification = 'Fake SR830 Lockin Amplifier'
        self.phase = 0.
        self.source = 1
        self.frequency = 1.
        self.trigger = 0
        self.harmonic = 1
        self.ampltidue = 1.
        self.input = 0
        self.grounding = 0
        self.coupling = 0
        self.filter = 0
        self.sensitivity = 10
        self.reserve = 0
        self.timeConstant = 7
        self.slope = 0
        self.synchronous = 0

    def busy(self):
        return False

    # Auto functions
    def autoGain(self):
        pass

    def autoReserve(self):
        pass

    def autoPhase(self):
        pass

    def autoOffset(self, channel):
        pass

    # Data transfer commands
    def x(self):
        return normal(0., 1., 1)

    def y(self):
        return normal(0., 1., 1)

    def r(self):
        return normal(0., 1., 1)

    def theta(self):
        return uniform(-360, 720., 1)

    def channel1(self):
        return normal(0., 1., 1)

    def channel2(self):
        return normal(0., 1., 1)

    def snap(self, a, b):
        """Return multiple readings simultaneously:
           1: X
           2: Y
           3: R
           4: theta
           5: Aux In 1
           6: Aux In 2
           7: Aux In 3
           8: Aux In 4
           9: Reference frequency
           10: Channel 1 display
           11: Channel 2 display
        NOTE: can obtain up to 6 readings
        """
        return (self.r(), self.theta())

    @property
    def data(self):
        return self.snap(3, 4)

    # Status reporting commands
    def clearStatusRegisters(self):
        """Clear status registers except status enable registers"""
        pass

    def status(self):
        """Read status byte"""
        return 3

    def error(self):
        """Read error status byte"""
        return 0
