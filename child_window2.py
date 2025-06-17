import numpy as np
from PyQt5.QtWidgets import  QVBoxLayout, QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SpectrumDialog(QDialog):
    def __init__(self, signal_data,sample_rate, parent=None):
        super(SpectrumDialog, self).__init__(parent)
        self.initUI(signal_data,sample_rate)

    def initUI(self, signal_data,sample_rate):
        self.setWindowTitle('频谱图')
        self.setLayout(QVBoxLayout())

        # 创建matplotlib的Figure和Canvas
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.layout().addWidget(self.canvas)

        # 计算频谱
        N = len(signal_data)
        T = 1.0 / sample_rate
        yf = np.fft.rfftfreq(N, T)
        y = np.fft.rfft(signal_data)

        # 绘制频谱图
        self.ax.plot(yf, np.abs(y))
        self.ax.set_xlabel('f (Hz)')
        self.ax.set_ylabel('amplitude')
        self.ax.set_title('Spectrogram')
        # 调整坐标轴范围以适应数据
        self.ax.relim()
        self.ax.autoscale_view()
        # 刷新Canvas
        self.canvas.draw()