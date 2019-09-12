# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSlot
from common.QSerialDevice import QSerialDevice
import numpy as np

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SR830(QSerialDevice):
    '''Abstraction of Stanford Research SR830 Lockin Amplifier

    ...

    Attributes
    ----------
    phase : float
        Phase offset relative to reference [degrees]
    source : int
        Reference source
    frequency : float
        Reference frequency [Hz]
    trigger : int
        Trigger mode for external reference
    harmonic : int
        Detection harmonic
    amplitude : float
        Amplitude of internal reference output [V]
    input : int
        Input configuration
    grounding : int
        Input shield grounding
    coupling : int
        Input coupling
    filter : int
        Input line filter mode
    sensitivity : int
        Input sensitivity mode
    reserve : int
        Dynamic reserve mode
    timeConstant : int
        Time constant mode
    slope : int
        Low-pass filter slope mode
    synchronous : int
        Synchronous filter status
    identification : str
        Identification string returned by instrument

    Methods
    -------
    identify() : bool
        Returns True if attached instrument is a SR830
    busy() : bool
        Returns True if the instrument is busy

    '''

    def __init__(self, baudrate=9600, timeout=1000):
        super(SR830, self).__init__(baudrate=baudrate,
                                    timeout=timeout)

    def identify(self):
        '''Check identity of instrument

        Returns
        -------
        identify : bool
            True if attached instrument is a SR830
        '''
        self.send('OUTX 0')
        res = self.handshake('*IDN?')
        logger.debug(' Received: {}'.format(res))
        found = 'SR830' in res
        logger.info(' SR830: {}'.format(found))
        return found

    def busy(self):
        '''Check if instrument is busy

        Returns
        -------
        busy : bool
            True if instrument is executing a command or has
            an error condition.
        '''
        status = self.status()
        executing = not bool(status & 0b11)
        error = bool(status & 0b100)
        return executing or error

    # Properties
    # Reference and phase commands
    @property
    def phase(self):
        '''Phase offset relative to reference [degrees]'''
        return np.float(self.handshake('PHAS?'))

    @phase.setter
    def phase(self, value):
        v = np.clip(float(value), -360, 729.99)
        self.send('PHAS {:.2f}'.format(v))

    @property
    def source(self):
        '''Reference source:
           0: external
           1: internal
        '''
        return int(self.handshake('FMOD?'))

    @source.setter
    def source(self, value):
        self.send('FMOD {}'.format(np.clip(int(value), 0, 1)))

    @property
    def frequency(self):
        '''Reference frequency [Hz]'''
        return float(self.handshake('FREQ?'))

    @frequency.setter
    def frequency(self, value):
        v = np.clip(float(value), 0.001, 102000.)
        self.send('FREQ {}'.format(v))

    @property
    def trigger(self):
        '''Reference trigger mode for external reference
           0: Sine zero crossing
           1: TTL rising edge
           2: TTL falling edge
        '''
        return int(self.handshake('RSLP?'))

    @trigger.setter
    def trigger(self, value):
        self.send('RSLP {}'.format(np.clip(int(value), 0, 2)))

    @property
    def harmonic(self):
        '''Detection harmonic'''
        return int(self.handshake('HARM?'))

    @harmonic.setter
    def harmonic(self, value):
        self.send('HARM {}'.format(np.clip(int(value), 1, 19999)))

    @property
    def amplitude(self):
        '''Amplitude of sine output [V]'''
        return float(self.handshake('SLVL?'))

    @amplitude.setter
    def amplitude(self, value):
        v = np.clip(float(value), 0.004, 5.)
        self.send('SLVL {:.3f}'.format(v))

    # Input and filter commands
    @property
    def input(self):
        '''Input configuration:
           0: Input A
           1: A-B
           2: I (1 MOhm)
           3: I (100 MOhm)
        '''
        return int(self.handshake('ISRC?'))

    @input.setter
    def input(self, value):
        self.send('ISRC {}'.format(np.clip(int(value), 0, 3)))

    @property
    def grounding(self):
        '''Input shield grounding mode
           0: shield is floating
           1: shield is grounded
        '''
        return int(self.handshake('IGND?'))

    @grounding.setter
    def grounding(self, value):
        self.send('IGND {}'.format(np.clip(int(value), 0, 1)))

    @property
    def coupling(self):
        '''Input coupling mode
           0: AC coupling
           1: DC coupling
        '''
        return int(self.handshake('ICPL?'))

    @coupling.setter
    def coupling(self, value):
        self.send('ICPL {}'.format(np.clip(int(value), 0, 1)))

    @property
    def filter(self):
        '''Input line filter mode
           0: No filters
           1: Line frequency notch filter
           2: 2x line frequency filter
           3: Both notch filters
        '''
        return int(self.handshake('ILIN?'))

    @filter.setter
    def filter(self, value):
        self.send('ILIN {}'.format(np.clip(int(value), 0, 3)))

    # Gain and time constant commands
    @property
    def sensitivity(self):
        '''Input sensitivity mode
           0 : 2 nV/fA    13: 50 µV/pA
           1 : 5 nV/fA    14: 100 µV/pA
           2 : 10 nV/fA   15: 200 µV/pA
           3 : 20 nV/fA   16: 500 µV/pA
           4 : 50 nV/fA   17: 1 mV/nA
           5 : 100 nV/fA  18: 2 mV/nA
           6 : 200 nV/fA  19: 5 mV/nA
           7 : 500 nV/fA  20: 10 mV/nA
           8 : 1 µV/pA    21: 20 mV/nA
           9 : 2 µV/pA    22: 50 mV/nA
           10: 5 µV/pA    23: 100 mV/nA
           11: 10 µV/pA   24: 200 mV/nA
           12: 20 µV/pA   25: 500 mV/nA
                          26: 1 V/µA
        '''
        return int(self.handshake('SENS?'))

    @sensitivity.setter
    def sensitivity(self, value):
        self.send('SENS {}'.format(np.clip(int(value), 0, 26)))

    @property
    def reserve(self):
        '''Dynamic reserve mode
           0: High reserve
           1: Normal
           2: Low noise (minimum)
        '''
        return int(self.handshake('RMOD?'))

    @reserve.setter
    def reserve(self, value):
        self.send('RMOD {}'.format(np.clip(int(value), 0, 2)))

    @property
    def timeConstant(self):
        '''Time constant mode
           0: 10 µs   10: 1 s
           1: 30 µs   11: 3 s
           2: 100 µs  12: 10 s
           3: 300 µs  13: 30 s
           4: 1 ms    14: 100 s
           5: 3 ms    15: 300 s
           6: 10 ms   16: 1 ks
           7: 30 ms   17: 3 ks
           8: 100 ms  18: 10 ks
           9: 300 ms  19: 30 ks
        '''
        return int(self.handshake('OFLT?'))

    @timeConstant.setter
    def timeConstant(self, value):
        self.send('OFLT {}'.format(np.clip(int(value), 0, 19)))

    @property
    def slope(self):
        '''Low pass filter slope mode
           0: 6 dB/oct
           1: 12 dB/oct
           2: 18 dB/oct
           3: 24 dB/oct
        '''
        return int(self.handshake('OFSL?'))

    @slope.setter
    def slope(self, value):
        self.send('OFSL {}'.format(np.clip(int(value), 0, 3)))

    @property
    def synchronous(self):
        '''Synchronous filter mode
           Used if detection frequency is less than 200 Hz
           0: Off
           1: On
        '''
        return int(self.handshake('SYNC?'))

    @synchronous.setter
    def synchronous(self, value):
        self.send('SYNC {}'.format(np.clip(int(value), 0, 1)))

    # Display and output commands

    # Setup commands

    # Auto functions
    def autoGain(self):
        self.send('AGAN')

    def autoReserve(self):
        self.send('ARSV')

    def autoPhase(self):
        self.send('APHS')

    def autoOffset(self, channel):
        c = np.clip(int(channel), 1, 3)
        self.send('AOFF {}'.format(c))

    # Data storage commmands

    # Data transfer commands
    def x(self):
        return float(self.handshake('OUTP?1'))

    def y(self):
        return float(self.handshake('OUTP?2'))

    def r(self):
        return float(self.handshake('OUTP?3'))

    def theta(self):
        return float(self.handshake('OUTP?4'))

    def channel1(self):
        return float(self.handshake('OUTR?1'))

    def channel2(self):
        return float(self.handshake('OUTR?2'))

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
        res = self.handshake('SNAP?{},{}'.format(
            np.clip(int(a), 1, 11),
            np.clip(int(b), 1, 11)))
        va, vb = res.split(',')
        logger.debug('amplitude: {} phase: {}'.format(va, vb))
        return float(va), float(vb)

    @property
    def data(self):
        return self.snap(3, 4)

    # Status reporting commands
    def clearStatusRegisters(self):
        '''Clear status regiesters except status enable registers'''
        self.send('*CLS')

    def status(self):
        '''Read status byte'''
        res = self.handshake('*STB?')
        return np.uint8(res)

    def error(self):
        '''Read error status byte'''
        res = self.handshake('ERRS?')
        return np.uint8(res)
