from PyQt4 import QtGui, QtCore
from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph as pg
import numpy as np


class WaveformWidget(GraphicsLayoutWidget):
    def __init__(self):
        GraphicsLayoutWidget.__init__(self, parent=None)

        self.layout = pg.GraphicsLayout()
        self._set_size_policy()

    def _set_size_policy(self):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        self.setMinimumSize(QtCore.QSize(0, 50))
        self.setMaximumSize(QtCore.QSize(16777215, 50))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setAcceptDrops(False)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def plot_waveform(self, raw_audio):
        self.waveform = self.layout.addPlot()
        self.waveform.hideAxis(axis='bottom')
        self.waveform.hideAxis(axis='left')

        self.waveform.setMaximumHeight(50)
        self.waveform.setMouseEnabled(x=False, y=False)
        self.waveform.setMenuEnabled(False)

        raw_audio = np.array(raw_audio)
        raw_audio += abs(min(raw_audio))

        self.waveform.plot(y=raw_audio, pen=(20, 170, 100, 30))
        self.waveform.setDownsampling(ds=True, auto=True, mode='peak')

        self.add_elements_to_plot(raw_audio)

    def add_elements_to_plot(self, raw_audio):
        # region wf
        min_audio = min(raw_audio)
        max_audio = max(raw_audio)
        len_audio = len(raw_audio)

        pos_wf_x_max = len_audio / 25.
        self.region_wf = pg.LinearRegionItem([0, pos_wf_x_max],
                                             brush=pg.mkBrush((50, 255, 255, 45)),
                                             bounds=[0, len_audio])
        self.region_wf.setZValue(10)

        self.region_wf_hor = pg.LinearRegionItem(
            brush=pg.mkBrush((50, 255, 255, 10)),
            orientation=pg.LinearRegionItem.Horizontal, movable=True,
            values=[min_audio, max_audio],
            bounds=[min_audio, max_audio])

        # vline for wf
        self.vline_wf = pg.ROI([0, 0], [0, max_audio], angle=0,
                               pen=pg.mkPen((255, 40, 35, 150), cosmetic=True,
                                            width=1))
        self.waveform.addItem(self.vline_wf)
        # self.waveform.addItem(self.region_wf_hor)
        self.waveform.addItem(self.region_wf)
        self.layout.addItem(self.waveform)
        self.addItem(self.layout)
