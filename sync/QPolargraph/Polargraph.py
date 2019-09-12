# -*- coding: utf-8 -*-

from common.QSerialDevice import QSerialDevice
import numpy as np
from time import sleep

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Motors(QSerialDevice):

    '''
    Abstraction of stepper moters controlled by Arduino

    ...

    Attributes
    ----------
    indexes : tuple of integers
        (n1, n2) Step indexes of two stepper motors.
        Setting this property causes the motors to move to (n1, n2).
    motor_speed : float
        maximum stepper motor speed in steps/second.

    Methods
    -------
    goto(n1, n2)
        Set target indexes for stepper motors.  This causes the
        motors to move from their present indexes to the new values.
    home()
        Equivalent to goto(0, 0)
    release()
        Stop motors and turn off current to windings.
    running() : bool
        Returns True if motors are running.
    '''

    def __init__(self):
        super(Motors, self).__init__(eol='\n',
                                     manufacturer='Arduino',
                                     timeout=1000)

    def identify(self):
        logger.info(' Waiting for Arduino serial port')
        sleep(2)
        res = self.handshake('Q')
        logger.debug(' Received: {}'.format(res))
        acam = 'acam2' in res
        logger.info(' Arduino running acam2: {}'.format(acam))
        return acam

    def process(self, data):
        logger.debug(' received: {}'.format(data))

    def goto(self, n1, n2):
        '''Move to index (n1, n2)

        Parameters
        ----------
        n1 : int
            Index of motor 1
        n2 : int
            Index of motor 2
        '''
        logger.debug(' goto {} {}'.format(n1, n2))
        self.send('G:%d:%d' % (n1, n2))

    def home(self):
        '''Move to home position'''
        self.goto(0, 0)

    def release(self):
        '''Stop and release motors'''
        self.send('S')

    def running(self):
        '''Returns True if motors are running'''
        try:
            res = self.handshake('R')
            header, running = res.split(':')
        except Exception as ex:
            logger.warning('Could not read running status: {}'.format(ex))
            running = 0
        return bool(int(running))

    @property
    def indexes(self):
        '''Current step numbers for motors'''
        try:
            res = self.handshake('P')
            header, n1, n2 = res.split(':')
            n1 = int(n1)
            n2 = int(n2)
        except Exception as ex:
            logger.warning('Did not read position: {}'.format(ex))
            n1 = 0
            n2 = 0
        return n1, n2

    @indexes.setter
    def indexes(self, n1, n2):
        self.send('P:%d:%d' % (n1, n2))

    @property
    def motor_speed(self):
        '''Maximum motor speed in steps/sec'''
        try:
            res = self.handshake('V')
            header, speed = res.split(':')
        except Exception as ex:
            logger.warning('Could not read maximum speed: {}'.format(ex))
            speed = 0
        return float(speed)

    @motor_speed.setter
    def motor_speed(self, speed):
        res = self.handshake('V:%f' % speed)
        logger.debug('speed: {}'.format(res))


class Polargraph(Motors):

    '''
    Abstraction of a polargraph

    The polargraph consists of two stepper motors with GT2 gears
    that translate a GT2 timing belt.  The motors are controlled
    by an Arduino microcontroller that is connected to the host
    computer by USB.  This class communicates with the Arduino to
    obtain programmed motion from the motors.

    ...

    Attributes
    ----------
    unit : float
        Separation between teeth on timing belt [mm]
        Default: 2.
    circumference : float
        Number of gear teeth per revolution.
        Default: 25.
    steps : float
        Number of motor steps per revolution.
        Default: 200.
    ell : float
        Separation between motors [m]
    y0 : float
        Vertical displacement of home position [m]
    y1 : float
        Vertical position of scan start [m]
    width : float
        Width of scan area [m]
    height : float
        Height of scan area [m]
    dy : float
        Vertical displacement between scan lines [m]
    ds : float
        Distance traveled per motor step [m]
    s0 : float
        Length of belt from motor to payload at home position [m]
    position : (x, y)
       Report current coordinates of payload measured in
       meters from home position.
    speed : float
       Translation speed [mm/s]

    Methods
    -------
    goto(x, y)
       Move payload to coordinates (x, y), measured in meters
       from home position.
    '''

    def __init__(self,
                 unit=2.,  # size of one timing belt tooth [mm]
                 circumference=25.,  # belt teeth per revolution
                 steps=200.,  # motor steps per revolution
                 ell=1.,  # separation between motors [m]
                 y0=0.1,  # rest displacement from motors' centerline [m]
                 width=0.6,  # width of scan area [m]
                 height=0.6,  # height of scan area [m]
                 dy=0.005):  # vertical displacement between scan lines [m]

        super(Polargraph, self).__init__()

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
        self.busy = self.running

    @property
    def ds(self):
        '''Distance traveled per step [m]'''
        return 1e-3 * self.unit * self.circumference / self.steps

    @property
    def s0(self):
        '''Distance from motor to payload at home position [m]'''
        return np.sqrt((self.ell / 2.)**2 + (self.y0)**2)

    def goto(self, x, y):
        '''Move payload to position (x,y)'''
        s1 = np.sqrt((self.ell / 2. - x)**2 + y**2)
        s2 = np.sqrt((self.ell / 2. + x)**2 + y**2)
        n1 = np.rint((s1 - self.s0) / self.ds).astype(int)
        n2 = np.rint((self.s0 - s2) / self.ds).astype(int)
        super(Polargraph, self).goto(n1, n2)

    @property
    def position(self):
        '''Current coordinates in meters'''
        n1, n2 = self.indexes
        s1 = self.s0 + n1 * self.ds
        s2 = self.s0 - n2 * self.ds
        x = (s2**2 - s1**2) / (2. * self.ell)
        ysq = (s1**2 + s2**2) / 2. - self.ell**2 / 4. - x**2
        if ysq < 0:
            logger.error('unphysical result: {} {} {} {} {} {}'.format(
                n1, n2, self.s0, s1, s2, ysq))
            y = self.y0
        else:
            y = np.sqrt(ysq)
        return x, y

    @property
    def speed(self):
        '''Translation speed in mm/s'''
        return self.motor_speed * self.circumference * self.unit / self.steps

    @speed.setter
    def speed(self, value):
        self.motor_speed = value * (self.steps /
                                    (self.circumference * self.unit))


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QWidget
    import sys

    app = QApplication(sys.argv)
    motors = Polargraph()
    print('Current position: {}'.format(motors.indexes))
    motors.goto(0.01, -0.01)
    w = QWidget()
    w.show()
    while (motors.running):
        print('.')
    motors.close()
    sys.exit(app.exec_())
