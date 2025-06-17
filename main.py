import sys
import csv
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox,QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import QTimer,Qt
from signalGenerator import Ui_MainWindow  # 导入 signalGenerator.py 中的 Ui_MainWindow 界面类
from child_window1 import SignalSynthesisDialog
from child_window2 import SpectrumDialog

class MyMainWindow(QMainWindow, Ui_MainWindow):  # 继承 QMainWindow类和 Ui_MainWindow界面类
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)  # 初始化父类
        self.setupUi(self)  # 继承 Ui_MainWindow 界面类

        # 创建一个Matplotlib的Figure实例,创建一个画布，并添加到verticalLayout1的布局中
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.verticalLayout1.addWidget(self.canvas)
        self.ax = self.fig.add_subplot(111)

        # 连接信号与槽
        self.connect_signals_slots()

        # 初始化信号参数
        self.init_signal_parameters()



    def connect_signals_slots(self):
        # 连接信号与槽函数
        # 信号类型Combox的索引值改变连接生成波形的函数
        self.signalType.currentIndexChanged.connect(self.check_signalType)  # 信号类型

        # 信号参数输入完毕连接调整参数的函数
        self.signalAmplitude.editingFinished.connect(self.check_parameter)  # 信号幅值
        self.signalBaseline.editingFinished.connect(self.check_parameter)  # 信号基线
        self.signalPeriod.editingFinished.connect(self.check_parameter)  # 信号周期
        self.signalPhase.editingFinished.connect(self.check_parameter)  # 信号相位

        # 点击放大缩小按钮连接波形放大缩小的函数
        self.zoomin_Button.clicked.connect(self.zoomin_update)  # 波形放大
        self.zoomout_Button.clicked.connect(self.zoomout_update)  # 波形缩小

        # 在画布区域的鼠标点击事件连接显示该点波形值的函数
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)  # 鼠标点击

        # 点击各功能按钮连接相应功能的函数
        self.dynamicButton.clicked.connect(self.dynamic_enable)  # 动态演示
        self.addButton.clicked.connect(self.addNoise_enable)  # 添加噪声
        self.filterButton.clicked.connect(self.filter_enable)  # 进行滤波
        self.syntheticButton.clicked.connect(self.synthesis_enable)  # 合成信号使能并生成界面
        self.spectrumButton.clicked.connect(self.open_child_window2)  # 生成频谱图界面

        # 改变复选框的状态连接禁用另一复选框的函数
        self.basic_signal.stateChanged.connect(self.on_checkbox_state_changed)
        self.ecg_signal.stateChanged.connect(self.on_checkbox_state_changed)

        # 改变滑动条的值连接生成波形的函数
        self.ecg_valueSlider.valueChanged.connect(self.check_signalType)

        # 点击菜单栏触发的动作信号连接相应功能的函数
        self.actionSave.triggered.connect(self.save_figure)
        self.actionInstruct.triggered.connect(self.show_help)

    def init_signal_parameters(self):
        # 初始化信号参数
        self.amplitude = float(self.signalAmplitude.text())  # 幅值
        self.baseline = float(self.signalBaseline.text())  # 基线
        self.period = float(self.signalPeriod.text())  # 周期
        self.phase = float(self.signalPhase.text())  # 相位（以周期为单位）
        self.x = np.linspace(0, 10 * self.period, 1000)  # 生成0到10 * self.period之间的1000个等间距点
        self.y = None

        # 初始化文本对象（一开始不显示）
        self.click_text = None
        self.scale_factor = 1

        # 初始化动态演示使能参数
        self.dynamic_enable = False
        self.noise_scale = 0.1  # 噪声强度
        self.apply_filter = True  # 是否应用滤波
        self.filter_size = 5  # 滤波器大小

        # 合成信号使能参数
        self.synthesis_enable = False
        # 初始化存储合成信号数据的列表
        self.signal_data_list = []

        # 设置滑动条的最小值、最大值和步长
        self.ecg_valueSlider.setMinimum(0)  # 设置最小值
        self.ecg_valueSlider.setMaximum(7)  # 设置最大值
        self.ecg_valueSlider.setSingleStep(1)  # 设置步长 0 30 60 80 90 120 150 300

        # 滑动条值的映射字典
        self.value_mapping = {
            1: 30,
            2: 60,
            3: 80,
            4: 90,
            5: 120,
            6: 150,
            7: 300
        }

    def check_signalType(self):
        # 清除之前的图形
        self.ax.clear()
        # 检查基本信号复选框是否被选中
        if self.basic_signal.isChecked():
            if not self.synthesis_enable:
                if self.signalType.currentIndex() == 0:
                    self.plot_sin()
                elif self.signalType.currentIndex() == 1:
                    self.plot_triangle()
                elif self.signalType.currentIndex() == 2:
                    self.plot_sawtooth()
                elif self.signalType.currentIndex() == 3:
                    self.plot_square()
            elif self.synthesis_enable:
                self.plot_synthesis()

        # 检查心电信号复选框是否被选中
        if self.ecg_signal.isChecked():
            self.plot_ecg()

    def check_parameter(self):
        try:
            # 清除旧的图形
            self.ax.clear()
            self.amplitude = float(self.signalAmplitude.text())  # 幅值
            self.baseline = float(self.signalBaseline.text())  # 基线
            self.period = float(self.signalPeriod.text())  # 周期
            if self.period == 0:
                raise ValueError("周期不能为零")
            self.phase = float(self.signalPhase.text())  # 相位（以周期为单位）
            # 生成新的波形
            self.check_signalType()
        except ValueError as e:
            # 创建一个 QMessageBox 实例
            msgBox = QMessageBox()
            # 设置消息框的标题
            msgBox.setWindowTitle("警告")
            if "周期不能为零" in str(e):
                # 如果异常消息包含“周期不能为零”，则设置特定的错误消息
                msgBox.setText("请输入一个非零的有效数字！")
            else:
                # 对于其他类型的ValueError，使用通用错误消息
                msgBox.setText("请输入一个有效数字！")
            # 设置消息框的图标为警告图标
            msgBox.setIcon(QMessageBox.Warning)
            # 显示消息框，并等待用户响应
            msgBox.exec_()

    def plot_sin(self):
        # 计算正弦波
        self.y = self.amplitude * np.sin(2 * np.pi * (self.x - self.phase) / self.period) + self.baseline
        # 清除之前的图形
        self.ax.clear()
        # 绘制图形
        self.line, = self.ax.plot(self.x, self.y)
        # 设置坐标轴标签和标题
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Sine Wave')
        self.ax.set_title('Sine Wave Plot')
        # 显示网格
        self.ax.grid(True)
        # 调整坐标轴范围以适应数据
        self.ax.relim()
        self.ax.autoscale_view()
         # 刷新画布
        self.canvas.draw()

    def plot_triangle(self):
        # 考虑相位偏移# 将 x_shifted 映射到 [0, period) 以确保周期性# 计算三角波
        x_shifted = self.x - self.phase
        x_wrapped = np.mod(x_shifted, self.period)
        self.y = self.amplitude * np.abs(x_wrapped - self.period / 2) + self.baseline
        # 清除之前的图形
        self.ax.clear()
        # 绘制三角波
        self.line, = self.ax.plot(self.x, self.y)
        # 设置坐标轴标签和标题
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Triangle Wave')
        self.ax.set_title('Triangle Wave Plot')
        # 显示网格
        self.ax.grid(True)
        # 调整坐标轴范围以适应数据
        self.ax.relim()
        self.ax.autoscale_view()
        # 更新画布以显示图形
        self.canvas.draw()

    def plot_sawtooth(self):
        # 计算锯齿波
        x_shifted = self.x - self.phase
        x_wrapped = np.mod(x_shifted, self.period)
        self.y = self.baseline + self.amplitude * x_wrapped / self.period
        # 清除之前的图形
        self.ax.clear()
        # 绘制三角波
        self.line, = self.ax.plot(self.x, self.y)
        # 设置坐标轴标签和标题
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Sawtooth Wave')
        self.ax.set_title('Sawtooth Wave Plot')
        # 显示网格
        self.ax.grid(True)
        # 调整坐标轴范围以适应数据
        self.ax.relim()
        self.ax.autoscale_view()
        # 更新画布以显示图形
        self.canvas.draw()

    def plot_square(self):
        #计算方波
        x_shifted = self.x - self.phase
        self.y=self.baseline + self.amplitude * np.sign(np.sin(2 * np.pi * x_shifted / self.period))
        # 清除之前的图形
        self.ax.clear()
        # 绘制方波
        self.line, = self.ax.plot(self.x, self.y)
        # 设置坐标轴标签和标题
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Square Wave')
        self.ax.set_title('Square Wave Plot')
        # 显示网格
        self.ax.grid(True)
        # 调整坐标轴范围以适应数据
        self.ax.relim()
        self.ax.autoscale_view()
        # 更新画布以显示图形
        self.canvas.draw()

    def plot_ecg(self):
        # 清除之前的图形
        self.ax.clear()
        self.y = []  # 初始化为空列表

        # 根据滑块的值获取映射后的数值
        heart_rate_value = self.value_mapping.get(self.ecg_valueSlider.value())
        self.ecg_valueText.setText(f'心率值： {heart_rate_value}')

        # 根据映射后的数值读取相应的CSV文件
        if heart_rate_value != None:
            file_path = f'data/bpm{heart_rate_value}.csv'
            # 计数器，记录已读取的行数
            row_count = 0
            # 使用 'utf-8' 编码打开文件
            with open(file_path, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                # 读取CSV文件的每一行
                for row in csv_reader:
                    self.y.append(int(row[0]))
                    row_count += 1

                    # 如果读取的行数达到两千行，则停止读取
                    if row_count >= 2000:
                        break
        # 绘制心电波形
        self.line, =self.ax.plot(self.y)
        # 设置坐标轴标签和标题
        self.ax.set_ylabel('ECG Wave')
        self.ax.set_title('ECG Wave Plot')
        # 显示网格
        self.ax.grid(True)
        # 更新画布以显示图形
        self.canvas.draw()

    def dynamic_enable(self):
        # 当y有值时才能对状态进行动态演示
        if self.y is not None:
            # 动态演示使能状态取反
            self.dynamic_enable = not self.dynamic_enable
            if self.dynamic_enable:
                # 清除之前的图形
                self.ax.clear()
                # 设置定时器
                self.timer = QTimer(self)
                # 检查基本信号复选框是否被选中
                if self.basic_signal.isChecked():
                    self.timer.timeout.connect(self.basic_update_plot)
                # 检查心电信号复选框是否被选中
                if self.ecg_signal.isChecked():
                    self.timer.timeout.connect(self.ecg_update_plot)
                self.timer.start(1)  # 每1毫秒更新一次
                self.dynamicButton.setStyleSheet("background-color: rgb(255, 225, 255);")
            elif not self.dynamic_enable:
                self.timer.stop()
                self.dynamicButton.setStyleSheet("background-color:white;")

    def basic_update_plot(self):
        # 更新相位
        self.phase -= 0.05
        # 更新曲线数据
        self.line.set_ydata(self.y)
        # 生成新的波形
        self.check_signalType()

    def ecg_update_plot(self):
        # 清除之前的图形
        self.ax.clear()
        # 实现循环移位
        shift_amount = 15  # 每次移位的数量
        self.y = self.y[shift_amount:] + self.y[:shift_amount]
        # 更新曲线数据
        self.line.set_ydata(self.y)
        # 刷新画布
        self.fig.canvas.draw_idle()
        # 绘制心电波形
        self.line, =self.ax.plot(self.y)
        # 设置坐标轴标签和标题
        self.ax.set_ylabel('ECG Wave')
        self.ax.set_title('ECG Wave Plot')
        # 显示网格
        self.ax.grid(True)
        # 更新画布以显示图形
        self.canvas.draw()

    def zoomin_update(self):
        #放大缩小是相对于波形来说
        self.scale_factor /= 1.1  # 缩小坐标轴，放大波形
        # 应用放大因子
        if self.basic_signal.isChecked():
            self.ax.set_xlim(min(self.x) * self.scale_factor, max(self.x) * self.scale_factor)
            self.ax.set_ylim(min(self.y) * self.scale_factor, max(self.y) * self.scale_factor)
        if self.ecg_signal.isChecked():
            self.ax.set_xlim(500 * self.scale_factor, 1500 * self.scale_factor)
            self.ax.set_ylim(2150 * self.scale_factor, 2200 * self.scale_factor)

        # 刷新画布
        self.ax.relim()  # 自动调整轴限制
        self.ax.autoscale_view()  # 自动缩放视图
        self.fig.canvas.draw_idle()  # 刷新画布

    def zoomout_update(self):
        # 放大缩小是相对于波形来说
        self.scale_factor *= 1.1  # 放大坐标轴，缩小波形
        # 应用缩小因子
        if self.basic_signal.isChecked():
            self.ax.set_xlim(min(self.x) * self.scale_factor, max(self.x) * self.scale_factor)
            self.ax.set_ylim(min(self.y) * self.scale_factor, max(self.y) * self.scale_factor)
        if self.ecg_signal.isChecked():
            self.ax.set_xlim(500 * self.scale_factor, 1500 * self.scale_factor)
            self.ax.set_ylim(2150 * self.scale_factor, 2200 * self.scale_factor)


        # 刷新画布
        self.ax.relim()  # 自动调整轴限制
        self.ax.autoscale_view()  # 自动缩放视图
        self.fig.canvas.draw_idle()  # 刷新画布

    def on_click(self, event):
        # 检查点击是否在坐标轴上
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            print("1")

            # 清除之前可能存在的文本对象
            if self.click_text is not None:
                self.click_text.remove()
                self.click_text = None

            # 计算波形上最接近点击位置的点的索引
            distances = np.sqrt((x - self.line.get_xdata()) ** 2 + (y - self.line.get_ydata()) ** 2)

            closest_index = np.argmin(distances)
            closest_x, closest_y = self.line.get_xdata()[closest_index], self.line.get_ydata()[closest_index]

            # 检查点击位置是否在波形的容差范围内
            tolerance = 0.5  # 根据需要调整容差大小
            if np.isclose(x, closest_x, atol=tolerance) and np.isclose(y, closest_y, atol=tolerance):
                # 在波形上创建一个文本对象，显示点击位置的坐标
                self.click_text = self.ax.text(x, y, f'({x:.2f}, {y:.2f})', color='purple')

                # 重绘图形
                self.fig.canvas.draw_idle()

    def addNoise_enable(self):
        # 当y有值时才能对状态进行修改
        if self.y is not None:
            # 添加噪声
            if hasattr(self, 'noise_scale') and self.noise_scale > 0:
                noise = self.noise_scale * np.random.normal(size=len(self.x))
                if self.basic_signal.isChecked():
                    self.y += noise
                    # 更新曲线数据
                    self.line.set_ydata(self.y)
                    # 刷新画布
                    self.fig.canvas.draw_idle()
                if self.ecg_signal.isChecked():
                    self.y = [x + np.random.normal(0, 10) for x in self.y]
                    # 更新曲线数据
                    self.line.set_ydata(self.y)
                    # 刷新画布
                    self.fig.canvas.draw_idle()

    def filter_enable(self):
        # 当y有值时才能对状态进行修改
        if self.y is not None:
            # 应用滤波
            if hasattr(self, 'apply_filter') and self.apply_filter:
                if self.basic_signal.isChecked():
                    # 使用简单的平均滤波器
                    self.y = np.convolve(self.y, np.ones((self.filter_size,)))/ self.filter_size
                    # 需要调整x轴的数据以适应滤波后的y轴数据长度
                    self.y = self.y[:len(self.x)]
                    # 更新曲线数据
                    self.line.set_ydata(self.y)
                    # 刷新画布
                    self.fig.canvas.draw_idle()

                if self.ecg_signal.isChecked():
                    # 对数据进行移动平均滤波
                    filtered_y = []
                    for i in range(len(self.y)):
                        # 确保索引不会超出范围
                        start_idx = max(0, i - self.filter_size + 1)
                        end_idx = min(i + 1, len(self.y))
                        window = self.y[start_idx:end_idx]
                        # 计算窗口内元素的平均值，并将其添加到滤波后的列表中
                        filtered_y.append(np.mean(window))
                    # 更新self.y为滤波后的数据
                    self.y = filtered_y
                    # 更新曲线数据
                    self.line.set_ydata(self.y)
                    # 刷新画布
                    self.fig.canvas.draw_idle()

    def synthesis_enable(self):
        # 使能状态取反
        self.synthesis_enable = not self.synthesis_enable
        # 合成信号使能参数
        if self.synthesis_enable == True:
            self.open_child_window1()
            self.syntheticButton.setStyleSheet("background-color: rgb(255, 225, 255);")
        elif self.synthesis_enable == False:
            self.syntheticButton.setStyleSheet("background-color:white;")

    def open_child_window1(self):
        # 创建并显示子窗口，传递父窗口的实例作为参数
        child_window1 = SignalSynthesisDialog(self)
        child_window1.data_returned.connect(self.on_data_returned)
        # 生成非模态对话框
        child_window1.show()

    def on_data_returned(self, signal_data_list):
        # 处理信号数据列表
        self.signal_data_list=signal_data_list[:]#或者直接self.signal_data_list=signal_data_list也可以
        # 生成新的波形
        self.check_signalType()

    def plot_synthesis(self):
        list_y = []
        #i为列表中的组数的索引值
        for i in range(len(self.signal_data_list)):
            amplitude = float(self.signal_data_list[i].amplitude)  # 幅值
            baseline = float(self.signal_data_list[i].baseline)  # 基线
            period = float(self.signal_data_list[i].period)  # 周期
            phase = float(self.signal_data_list[i].phase) + self.phase # 相位（以周期为单位）+self.phase是为了实现动态更新
            if self.signal_data_list[i].signal_type == 1:  # 正弦波
                result = amplitude * np.sin(2 * np.pi * (self.x - phase) / period) + baseline
                list_y.append(result)
            if self.signal_data_list[i].signal_type == 2:  # 三角波
                x_shifted = self.x - phase
                x_wrapped = np.mod(x_shifted, period)
                result= amplitude * np.abs(np.mod(x_wrapped, period) - period / 2) + baseline
                list_y.append(result)
            if self.signal_data_list[i].signal_type == 3:  # 锯齿波
                x_shifted = self.x - phase
                x_wrapped = np.mod(x_shifted, period)
                result = baseline + amplitude * x_wrapped / period
                list_y.append(result)
            if self.signal_data_list[i].signal_type == 4:  # 方波
                x_shifted = self.x - phase
                result = baseline + amplitude * np.sign(np.sin(2 * np.pi * x_shifted / period))
                list_y.append(result)

        self.y = sum(list_y)

        # 绘制合成波
        self.line, = self.ax.plot(self.x, self.y)
        # 设置坐标轴标签和标题
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Synthesis Wave')
        self.ax.set_title('Synthesis Wave Plot')
        # 显示网格
        self.ax.grid(True)
        # 调整坐标轴范围以适应数据
        self.ax.relim()
        self.ax.autoscale_view()
        # 更新画布以显示图形
        self.canvas.draw()

    def open_child_window2(self):
        # 当y有值时才能对状态进行修改
        if self.y is not None:
            # 创建频谱图对话框并显示
            sampling_frequency=10*(1/self.period)# 采样率要大于最高频率成分的两倍
            spectrum_dialog = SpectrumDialog(self.y, sampling_frequency)
            spectrum_dialog.exec_()

    def on_checkbox_state_changed(self, state):
        # 检查是哪个复选框的状态发生了变化
        if self.sender() == self.basic_signal:
            # 如果复选框1被选中，则禁用复选框2
            self.ecg_signal.setDisabled(state == Qt.Checked)
        elif self.sender() == self.ecg_signal:
            # 如果复选框2被选中，则禁用复选框1
            self.basic_signal.setDisabled(state == Qt.Checked)

    def save_figure(self):
        # 使用文件对话框选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'PNG Files (*.png);;All Files (*)')
        if file_path:
            # 使用 Figure 对象的 savefig 方法保存图形
            self.fig.savefig(file_path)

    def show_help(self):
        # 准备帮助文档内容
        help_text = """
帮助文档：
    勾选“基本信号”或“心电信号”复选框后，再进行参数的设置和功能的使用。
    “基本信号”可以修改信号的周期、幅值、基线、时移，编辑框内的数字，可以实现参数的调整。
    “心电信号”可以改变滑动条调整心率。
    点击各功能按钮即可实现相应功能。
    波形右上角的“+”，“-”按钮可实现波形的放大与缩小。
    当有波形显示时，点击波形上的点，可显示波形该点的数值。
    
注意：
1.各功能在波形Y值为空时使用不了，即点击无效，但不会造成程序崩溃。
2.放大缩小功能只能在信号静态演示时使用。
3.添加噪声后仍可动态演示。
4.点击动态演示按钮，按钮有颜色时为使能态；按钮无颜色为无效态。
5.合成信号按钮必须在勾选“基本信号”时使用。
    

        """

        # 使用QMessageBox显示帮助文档
        QMessageBox.information(self, 'Help', help_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 在 QApplication 方法中使用，创建应用程序对象
    myWin = MyMainWindow()  # 实例化 MyMainWindow 类，创建主窗口
    myWin.show()  # 在桌面显示控件 myWin
    sys.exit(app.exec_())  # 结束进程，退出程序
