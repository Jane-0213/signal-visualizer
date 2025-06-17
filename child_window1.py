import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout,QMessageBox,QComboBox,QDialog
from PyQt5.QtCore import pyqtSignal

# 自定义信号数据类
class SignalData:
    def __init__(self, signal_type, period, amplitude, baseline, phase):
        self.signal_type = signal_type
        self.period = period
        self.amplitude = amplitude
        self.baseline = baseline
        self.phase = phase

class SignalSynthesisDialog(QDialog):
    data_returned = pyqtSignal(list)  # 自定义信号，用于传递信号数据列表

    def __init__(self, parent=None):
        super(SignalSynthesisDialog,self).__init__(parent)
        self.initUI()

    def initUI(self):
        # 创建布局
        self.layout = QVBoxLayout()

        # 创建输入数字的文本框和按钮
        self.num_signals_label = QLabel("输入合成信号的数量:")
        self.num_signals_input = QLineEdit()
        self.add_signals_button = QPushButton("添加信号")
        self.add_signals_button.clicked.connect(self.addSignals)

        # 创建信号设置的网格布局
        self.signal_grid = QGridLayout()


        # 将控件添加到垂直布局中
        self.layout.addWidget(self.num_signals_label)
        self.layout.addWidget(self.num_signals_input)
        self.layout.addWidget(self.add_signals_button)
        self.layout.addLayout(self.signal_grid)

        # 设置窗口的主布局
        self.setLayout(self.layout)
        self.setWindowTitle('信号合成页面')
        self.show()

    def addSignals(self):
        try:
            #清空前一次的网格布局
            self.clear_grid_layout()

            num_signals = int(self.num_signals_input.text())
            for i in range(num_signals):
                # 为每个信号创建一个行
                row = self.signal_grid.rowCount()
                self.signal_grid.addWidget(QLabel(f"信号 {i+1} "), row, 0)

                # 周期
                type_label = QLabel("信号类型:")
                type_input = QComboBox()
                type_input.addItem("正弦波", 1)
                type_input.addItem("三角波", 2)
                type_input.addItem("锯齿波", 3)
                type_input.addItem("方波", 4)
                self.signal_grid.addWidget(type_label, row, 1)
                self.signal_grid.addWidget(type_input, row, 2)

                # 周期
                period_label = QLabel("周期:")
                period_input = QLineEdit()
                self.signal_grid.addWidget(period_label, row, 3)
                self.signal_grid.addWidget(period_input, row, 4)

                # 幅值
                amplitude_label = QLabel("幅值:")
                amplitude_input = QLineEdit()
                self.signal_grid.addWidget(amplitude_label, row, 5)
                self.signal_grid.addWidget(amplitude_input, row, 6)

                # 基线
                baseline_label = QLabel("基线:")
                baseline_input = QLineEdit()
                self.signal_grid.addWidget(baseline_label, row, 7)
                self.signal_grid.addWidget(baseline_input, row, 8)

                # 相位（时移）
                phase_label = QLabel("时移:")
                phase_input = QLineEdit()
                self.signal_grid.addWidget(phase_label, row, 9)
                self.signal_grid.addWidget(phase_input, row, 10)

            # 合成信号按钮
            self.synthesize_button = QPushButton("合成信号")
            self.synthesize_button.clicked.connect(self.on_synthesize)
            self.layout.addWidget(self.synthesize_button)

        except ValueError:
            # 创建一个 QMessageBox 实例
            msgBox = QMessageBox()
            # 设置消息框的标题
            msgBox.setWindowTitle("警告")
            # 设置消息框的文本
            msgBox.setText("请输入一个有效的整数！")
            # 设置消息框的图标为警告图标
            msgBox.setIcon(QMessageBox.Warning)
            # 显示消息框，并等待用户响应
            msgBox.exec_()

    def clear_grid_layout(self):
        if self.signal_grid is not None:
            for i in reversed(range(self.signal_grid.count())):
                item = self.signal_grid.takeAt(i)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

    def on_synthesize(self):
        # 收集所有信号数据
        signal_data_list = []
        column_count = self.signal_grid.columnCount()  # 获取列数
        for row in range(self.signal_grid.rowCount()):
            type_input_index = row * column_count + 2  # 假设类型控件在第三列（索引为2）
            period_input_index = row * column_count + 4  # 假设周期控件在第五列（索引为4）
            amplitude_input_index = row * column_count + 6  # 假设幅值控件在第七列（索引为6）
            baseline_input_index = row * column_count + 8  # 假设基线控件在第九列（索引为8）
            phase_input_index = row * column_count + 10  # 假设相位控件在第十一列（索引为10）

            # 分别获取每个控件的项
            type_item = self.signal_grid.itemAt(type_input_index)
            period_item = self.signal_grid.itemAt(period_input_index)
            amplitude_item = self.signal_grid.itemAt(amplitude_input_index)
            baseline_item = self.signal_grid.itemAt(baseline_input_index)
            phase_item = self.signal_grid.itemAt(phase_input_index)

            # 检查每个项是否为None，并获取对应的widget
            type_input = type_item.widget() if type_item else None
            period_input = period_item.widget() if period_item else None
            amplitude_input = amplitude_item.widget() if amplitude_item else None
            baseline_input = baseline_item.widget() if baseline_item else None
            phase_input = phase_item.widget() if phase_item else None

            if all([type_input, period_input, amplitude_input, baseline_input, phase_input]):
                try:
                    signal_type = int(type_input.currentData())
                    period = float(period_input.text())
                    if period == 0:
                        raise ValueError("周期不能为零")
                    amplitude = float(amplitude_input.text())
                    baseline = float(baseline_input.text())
                    phase = float(phase_input.text())

                    signal_data = SignalData(signal_type, period, amplitude, baseline, phase)
                    signal_data_list.append(signal_data)
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

        # 发送信号数据列表回主窗口
        self.data_returned.emit(signal_data_list)
        self.close()  # 关闭子窗口

#单独调试需要用到
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SignalSynthesisDialog()
    sys.exit(app.exec_())
