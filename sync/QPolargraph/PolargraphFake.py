# -*- coding: utf-8 -*-
import numpy as np
from time import (time, sleep)

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MotorsFake(object):

    """Control the pair of stepper motors driving a polargraph"""

    def __init__(self):
        self._indexes = (0, 0)
        self._target = (0, 0)
        self.motor_speed = 500
        self._tstart = 0.
        self._tstop = time()

    def goto(self, n1, n2):
        """Move to index (n1, n2)"""
        self._tstart = time()
        self._origin = self._indexes
        self._target = (n1, n2)
        delta = max(abs(self._target[0] - self._origin[0]),
                    abs(self._target[1] - self._origin[1]))
        if delta <= 0:
            self._tstop = -1.
        else:
            self._tstop = self._tstart + delta / self.motor_speed

    def home(self):
        """Move to home position"""
        self.goto(0, 0)

    def release(self):
        """Stop and release motors"""
        pass

    @property
    def indexes(self):
        sleep(0.05)
        try:
            f = (time() - self._tstart) / (self._tstop - self._tstart)
        except ZeroDivisionError:
            f = 1.
        if f >= 1.:
            self._indexes = self._target
        else:
            n1 = self._origin[0] + f * (self._target[0] - self._origin[0])
            n2 = self._origin[1] + f * (self._target[1] - self._origin[1])
            self._indexes = (n1, n2)
        return self._indexes

    def running(self):
        """Returns True if motors are running"""
        return self.indexes != self._target


class PolargraphFake(MotorsFake):

    """Control a polargraph

    The polargraph consists of two stepper motors with GT2 gears
    that translate a GT2 timing belt.  The motors are controlled
    by an Arduino microcontroller that is connected to the host
    computer by USB.  This class communicates with the Arduino to
    obtain programmed motion from the motors.
    """

    def __init__(self,
                 unit=2.,  # size of one timing belt tooth [mm]
                 circumference=25.,  # belt teeth per revolution
                 steps=200.,  # motor steps per revolution
                 ell=1.,  # separation between motors [m]
                 y0=0.1,  # rest displacement from motors' centerline [m]
                 width=0.6,  # width of scan area [m]
                 height=0.6,  # height of scan area [m]
                 dy=0.005):  # vertical displacement between scan lines [m]

        super(PolargraphFake, self).__init__()

        # Belt drive
        self.unit = float(unit)
        self.circumference = float(circumference)
        self.steps = float(steps)

        # Motor configuration
        self.ell = float(ell)
        self.y0 = float(y0)

        # Scan configuration
        self.x1 = 0.
        self.y1 = 0.
        self.width = float(width)
        self.height = float(height)
        self.dy = float(dy)

        # distance traveled per step [m]
        self.ds = 1e-3 * self.unit * self.circumference / self.steps
        # distance (length of belt) from motor to payload at home position [m]
        self.s0 = np.sqrt((self.ell / 2.)**2 + (self.y0)**2)

    def goto(self, x, y):
        """Move payload to position (x,y)"""
        s1 = np.sqrt((self.ell / 2. - x)**2 + y**2)
        s2 = np.sqrt((self.ell / 2. + x)**2 + y**2)
        n1 = np.rint((s1 - self.s0) / self.ds).astype(int)
        n2 = np.rint((self.s0 - s2) / self.ds).astype(int)
        super(PolargraphFake, self).goto(n1, n2)

    @property
    def position(self):
        """Current coordinates in meters"""
        n1, n2 = self.indexes
        s1 = self.s0 + n1 * self.ds
        s2 = self.s0 - n2 * self.ds
        x = (s2**2 - s1**2) / (2. * self.ell)
        y = np.sqrt((s1**2 + s2**2) / 2. - self.ell**2 / 4. - x**2)
        return x, y

    @property
    def speed(self):
        """Translation speed in mm/s"""
        return self.motor_speed * self.circumference * self.unit / self.steps

    @speed.setter
    def speed(self, value):
        self.motor_speed = value * (self.steps /
                                    (self.circumference * self.unit))

    def busy(self):
        return False
