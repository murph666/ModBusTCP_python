from PyQt5 import QtGui, QtWidgets, QtCore, uic
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer
import libscrc
import time
import sys
import queue
import struct

_SERVER_HOST = "localhost"
_SERVER_PORT = 502

class connection(QtCore.QThread):
    # signalStatusConnection = QtCore.pyqtSignal(bool)
    signalMessage = QtCore.pyqtSignal(int)
    signalConfig = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        global _SERVER_HOST
        self.modbusClient = ModbusClient(host="192.168.1.235", port=_SERVER_PORT, unit_id=1, auto_open=True)
        # self.modbusServer = ModbusServer(host=_SERVER_HOST, port=_SERVER_PORT, no_block=True)
        self.txq = queue.Queue()
        self.newMessage = False
        # print('created')
        self.message = 'qwe'

    def currentTime(self):
        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
        return time_string


    def runSerialConnection(self):
        coils = []
        self.modbusClient.open()

        application.terminal.append(
            f"<{self.currentTime()}> Opening {self.modbusClient.host} at {self.modbusClient.port}")
        while self.modbusClient.is_open:
            coils_l = self.modbusClient.read_holding_registers(468,2)
            if coils_l and coils != coils_l[0]:
                application.terminal.append(f"<{self.currentTime()}> 'coil ad #0 to 9: {coils_l}")
                self.signalMessage.emit(coils_l[0])
                coils = coils_l[0]

            if not self.txq.empty():
                tx = self.txq.get()
                self.modbusClient.write_single_register(470,tx)
            time.sleep(0.1)


class ApplicationWindow(QtWidgets.QMainWindow):
    _Serial_connection = False
    _rx_Message = ''

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        uic.loadUi('./ui/terminal.ui', self)
        self.message = ''
        self.setValidator()
        self.createThreads()
        self.defineActions()
        self.getIp()


# <-----------------------------------UIPART----------------------------------->

    def defineActions(self):
        self.radioButton.clicked.connect(self.constructNumber)
        self.radioButton_2.clicked.connect(self.constructNumber)
        self.radioButton_3.clicked.connect(self.constructNumber)
        self.radioButton_4.clicked.connect(self.constructNumber)
        self.radioButton_5.clicked.connect(self.constructNumber)
        self.radioButton_6.clicked.connect(self.constructNumber)
        self.radioButton_7.clicked.connect(self.constructNumber)
        self.radioButton_8.clicked.connect(self.constructNumber)
        self.radioButton_9.clicked.connect(self.constructNumber)
        self.radioButton_10.clicked.connect(self.constructNumber)
        self.radioButton_11.clicked.connect(self.constructNumber)
        self.radioButton_12.clicked.connect(self.constructNumber)
        self.radioButton_13.clicked.connect(self.constructNumber)
        self.radioButton_14.clicked.connect(self.constructNumber)
        self.radioButton_15.clicked.connect(self.constructNumber)
        self.radioButton_16.clicked.connect(self.constructNumber)

        self.lineEdit_ip.textEdited.connect(self.getIp)
        self.pushButton_connect.clicked.connect(self.serialConnect)

    def getIp(self):
        global _SERVER_HOST
        _SERVER_HOST = self.lineEdit_ip.text()

    def constructNumber(self):
        msg =   str(int(self.radioButton.isChecked())) + \
                str(int(self.radioButton_2.isChecked())) + \
                str(int(self.radioButton_3.isChecked())) + \
                str(int(self.radioButton_4.isChecked())) + \
                str(int(self.radioButton_5.isChecked())) + \
                str(int(self.radioButton_6.isChecked())) + \
                str(int(self.radioButton_7.isChecked())) + \
                str(int(self.radioButton_8.isChecked())) + \
                str(int(self.radioButton_9.isChecked())) + \
                str(int(self.radioButton_10.isChecked())) + \
                str(int(self.radioButton_11.isChecked())) + \
                str(int(self.radioButton_12.isChecked())) + \
                str(int(self.radioButton_13.isChecked())) + \
                str(int(self.radioButton_14.isChecked())) + \
                str(int(self.radioButton_15.isChecked())) + \
                str(int(self.radioButton_16.isChecked()))
        self.exchange.txq.put(int(msg, 2))



    def setValidator(self):
        ipRange = "^(?:25[0-5]|2[0-4]\d|[0-1]?\d{1,2})(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d{1,2})){3}$"
        # portRange = "^([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[1-5])$"
        ipRegex = QtCore.QRegExp("^" + ipRange + "\\." + ipRange +
                                 "\\." + ipRange + "\\." + ipRange + "$")
        # portRegex = QtCore.QRegExp("^" + portRange + "\\." + portRange + "\\." +
        #    portRange + "\\." + portRange + "\\." + portRange + "$")
        ipValidator = QtGui.QRegExpValidator(ipRegex)

        self.lineEdit_ip.setValidator(ipValidator)
        self.lineEdit_IPMask.setValidator(ipValidator)

# <-----------------------------------UIPART----------------------------------->

# <-----------------------------------THREADS--------------------------------- ->

    def createThreads(self):
        # <----------define instances---------->
        self.exchangeThread = QtCore.QThread()
        self.exchange = connection()
        self.exchange.moveToThread(self.exchangeThread)
        # <----------define instances---------->
        # <----------connect signals----------->
        # self.exchangeThread.started.connect(self.sendMessage)
        self.exchangeThread.started.connect(
            self.exchange.runSerialConnection)

        self.exchangeThread.finished.connect(self.exchangeThread.quit)
        self.exchangeThread.finished.connect(self.exchange.deleteLater)
        self.exchangeThread.finished.connect(
            self.exchangeThread.deleteLater)
        # self.exchangeThread.finished.connect(
        #     lambda: self.terminal.append('exchangeThread.finished'))
        # <----------connect signals---------->
        self.exchange.signalMessage.connect(self.showByte)
# <-----------------------------------THREADS---------------------------------->

# <-----------------------------------Serial---------------------------------->

    def serialConnect(self):
        if not self._Serial_connection:
            self.getIp()
            self.exchangeThread.start()
            self._Serial_connection = True
            self.pushButton_connect.setStyleSheet("background-color: green")
        else:
            self._Serial_connection = False
            self.pushButton_connect.setStyleSheet("background-color: red")
            self.exchangeThread.finished.emit()
# <-----------------------------------Serial---------------------------------->

# <--------------------------------MESSAGEPROC--------------------------------->

    def createMessage(self):
        if self.comboBox_port_2.currentText() == 'Serial':
            self.message = []
            self.message.append(int(self.config['Connection']['SLAVE_ID']))
            self.message.append(int(self.config['Connection']['FUNCTION']))
            self.message.append(int(self.config['Connection']['FIRST_REG']))
            self.message.append(int(self.config['Connection']['NO_REG']))
            self.message = self.convertToHEX(self.message)
            self.message += self.convertToHEX(libscrc.modbus(self.message))
            # print(self.message)
        else:
            pass
            # MB TCP/IP MESSAGE

# <--------------------------------MESSAGEPROC--------------------------------->

# <----------------------------------UISLOTS----------------------------------->
    @QtCore.pyqtSlot(int)
    def showByte(self, value):
        str = f'{value:016b}'
        print(str)
        if int(str[0]): self.radioButton.setChecked(True)
        else: self.radioButton.setChecked(False)
        if int(str[1]): self.radioButton_2.setChecked(True)
        else: self.radioButton_2.setChecked(False)
        if int(str[2]): self.radioButton_3.setChecked(True)
        else: self.radioButton_3.setChecked(False)
        if int(str[3]): self.radioButton_4.setChecked(True)
        else: self.radioButton_4.setChecked(False)
        if int(str[4]): self.radioButton_5.setChecked(True)
        else: self.radioButton_5.setChecked(False)
        if int(str[5]): self.radioButton_6.setChecked(True)
        else: self.radioButton_6.setChecked(False)
        if int(str[6]): self.radioButton_7.setChecked(True)
        else: self.radioButton_7.setChecked(False)
        if int(str[7]): self.radioButton_8.setChecked(True)
        else: self.radioButton_8.setChecked(False)
        if int(str[8]): self.radioButton_9.setChecked(True)
        else: self.radioButton_9.setChecked(False)
        if int(str[9]): self.radioButton_10.setChecked(True)
        else: self.radioButton_10.setChecked(False)
        if int(str[10]): self.radioButton_11.setChecked(True)
        else: self.radioButton_11.setChecked(False)
        if int(str[11]): self.radioButton_12.setChecked(True)
        else: self.radioButton_12.setChecked(False)
        if int(str[12]): self.radioButton_13.setChecked(True)
        else: self.radioButton_13.setChecked(False)
        if int(str[13]): self.radioButton_14.setChecked(True)
        else: self.radioButton_14.setChecked(False)
        if int(str[14]): self.radioButton_15.setChecked(True)
        else: self.radioButton_15.setChecked(False)
        if int(str[15]): self.radioButton_16.setChecked(True)
        else: self.radioButton_15.setChecked(False)

# <----------------------------------UISLOTS----------------------------------->


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())
