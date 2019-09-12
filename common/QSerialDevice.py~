# -*- coding: utf-8 -*-

from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QByteArray)
from PyQt5.QtSerialPort import (QSerialPort, QSerialPortInfo)
from PyQt5.QtWidgets import QMainWindow

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class QSerialDevice(QSerialPort):
    '''
    Abstraction of an instrument connected to a serial port

    ...

    Attributes
    ----------
    eol : str, optional
        End-of-line character.
        Default: '\r' (carriage return)
    manufacturer : str, optional
        Identifier for the serial interface manufacturer.
        Default: 'Prolific'
    baudrate : int, optional
        Baud rate for serial communication.
        Default: 9600
    parity : int, optional
        One of the constants defined in the serial package
    stopbits : int, optional
        One of the constants defined in the serial package
    timeout : float
        Read timeout period [s].
        Default: 0.1

    Methods
    -------
    find() : bool
        Find the serial device that satisfies identify().
        Returns True if the device is found and correctly opened.
    identify() : bool
        Returns True if the device on the opened port correctly
        identifies itself.  Subclasses must override this method.
    send(cmd)
        Write cmd to serial device with eol termination.
        Response is handled by call to process().
    process(data)
        Process data returned by device.
        Subclasses should override this method.
    handshake(cmd) : str
        Write cmd to serial device and return response.

    Signals
    -------
    dataReady(data)
        Emitted when eol-terminated data is returned by the device.
    '''

    dataReady = pyqtSignal(str)

    def __init__(self, parent=None, port=None,
                 eol='\r',
                 manufacturer='Prolific',
                 baudrate=QSerialPort.Baud9600,
                 databits=QSerialPort.Data8,
                 parity=QSerialPort.NoParity,
                 stopbits=QSerialPort.OneStop,
                 timeout=1000,
                 **kwargs):
        super(QSerialDevice, self).__init__(parent=parent, **kwargs)
        self.eol = eol
        self.manufacturer = manufacturer
        self.baudrate = baudrate
        self.databits = databits
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.readyRead.connect(self.receive)
        self.buffer = QByteArray()
        if port is None:
            self.find()
        else:
            self.setup(port)
        if not self.isOpen():
            raise ValueError('Could not find serial device')

    def setup(self, portinfo):
        if portinfo is None:
            logger.info('No serial port specified')
            return False
        name = portinfo.systemLocation()
        logger.debug(' Setting up {}'.format(name))
        if portinfo.isBusy():
            logger.debug(' Port is busy: {}'.format(name))
            return False
        self.setPort(portinfo)
        self.setBaudRate(self.baudrate)
        self.setDataBits(self.databits)
        self.setParity(self.parity)
        self.setStopBits(self.stopbits)
        if not self.open(QSerialPort.ReadWrite):
            logger.debug(' Could not open port: {}'.format(name))
            return False
        if self.bytesAvailable():
            tmp = self.readAll()
            logger.info(' Cleared bytes from device: {}'.format(tmp))
        if self.identify():
            logger.info(' Device found at {}'.format(name))
            return True
        self.close()
        logger.debug(' Device not connected to {}'.format(name))
        return False

    def find(self):
        '''
        Attempt to identify and open the serial port

        Returns
        -------
        find : bool
            True if port identified and successfully opened.
        '''
        ports = QSerialPortInfo.availablePorts()
        if len(ports) < 1:
            logger.warning(' No serial ports detected')
            return
        for port in ports:
            portinfo = QSerialPortInfo(port)
            if self.setup(portinfo):
                break

    def identify(self):
        '''
        Identify this device

        Subclasses must override this method

        Returns
        -------
        identify : bool
            True if attached device correctly identifies itself.
        '''
        return True

    def process(self, data):
        '''
        Process data received from device

        Subclasses should override this method
        '''
        logger.debug('process: {}'.format(data))

    def send(self, data):
        '''
        Write string to serial device with eol termination

        Parameters
        ----------
        str : string
            String to be transferred
        '''
        cmd = data + self.eol
        self.write(cmd.encode())
        logger.debug(' Data sent: {}'.format(data))

    @pyqtSlot()
    def receive(self):
        '''
        Slot for readyRead signal

        Appends data received from device to a buffer
        until eol character is received, then processes
        the contents of the buffer.
        '''
        logger.debug(' Data received')
        self.buffer.append(self.readAll())
        if self.buffer.contains(self.eol.encode()):
            logger.debug(' EOL character received')
            data = self.buffer.trimmed().data().decode()
            self.dataReady.emit(data)
            self.process(data)
            self.buffer.clear()

    def gets(self):
        '''
        Read characters from the serial port until eol is received

        Returns
        -------
        s : str
            Decoded string
        '''
        while not self.buffer.contains(self.eol.encode()):
            if self.waitForReadyRead(self.timeout):
                self.buffer.append(self.readAll())
            else:
                logger.debug(' gets() timed out')
                break
        s = self.buffer.trimmed().data().decode()
        logger.debug(' gets() received {} bytes: {}'.format(len(s), s))
        self.buffer.clear()
        return s

    def handshake(self, cmd):
        '''
        Send command string to device and return the
        response from the device

        ...

        This form of communication bypasses the
        signal/slot mechanism and thus is blocking.

        Arguments
        ---------
        cmd : str
            String to be transmitted to device

        Returns
        -------
        res : str
            Response from device
        '''
        self.blockSignals(True)
        self.send(cmd)
        res = self.gets()
        self.blockSignals(False)
        return res


class Main(QMainWindow):
    def __init__(self, number=0):
        super().__init__()
        ports = QSerialPortInfo.availablePorts()
        if len(ports) < 1:
            logger.warning('No serial ports')
        port = QSerialPortInfo(ports[number])
        print(port.systemLocation())
        self.serial = QSerialDevice(port=port)
        if self.serial.isOpen():
            print('open')
            print(self.serial.handshake('VERSION'))

    def closeEvent(self, event):
        self.serial.close()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    gui = Main(0)
    gui.show()
    sys.exit(app.exec_())
