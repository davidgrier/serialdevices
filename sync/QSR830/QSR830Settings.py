# -*- coding: utf-8 -*-

from common.QSettingsWidget import QSettingsWidget
from .SR830Settings_UI import Ui_SR830Settings


class QSR830Settings(QSettingsWidget):
    """Configuration for a Stanford Research Systems SR830 lockin amplifier"""

    def __init__(self, parent=None, device=None):
        super(QSR830Settings, self).__init__(parent=parent,
                                             ui=Ui_SR830Settings())
        self.device = device

    def configureUi(self):
        # Choice of source determines activity of widgets
        self.ui.source.currentIndexChanged[int].connect(
            lambda v: self.ui.frequency.setEnabled(bool(v)))
        self.ui.source.currentIndexChanged[int].connect(
            lambda v: self.ui.amplitude.setEnabled(bool(v)))
        self.ui.source.currentIndexChanged[int].connect(
            lambda v: self.ui.trigger.setDisabled(bool(v)))
        self.ui.frequency.setEnabled(bool(self.ui.source.currentIndex()))
        self.ui.amplitude.setEnabled(bool(self.ui.source.currentIndex()))
        self.ui.trigger.setDisabled(bool(self.ui.source.currentIndex()))


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    from SR830 import SR830

    app = QApplication(sys.argv)
    try:
        device = SR830()
    except ValueError:
        device = None
    wid = QSR830Settings(device=device)
    wid.show()
    sys.exit(app.exec_())
