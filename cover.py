from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ui.uidesign import Ui_MainWindow
from app.control import *
from threading import *
import sys
import os
import shutil
import xlwt


def basedir():
    if getattr(sys, 'frozen', False):
        BASEDIR = os.path.dirname(sys.executable)
    else:
        BASEDIR = os.getcwd()
    return BASEDIR

DATA_ALL = []

class Host(QThread):
    messageReceived = pyqtSignal(object)
    processBar = pyqtSignal(object)
    enableBT = pyqtSignal(object)
    popup = pyqtSignal(object)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        self.enableBT.emit(False)
        k = 0
        for i in self.data:
            if i != "":
                file_name = str(convert_url(i))
                file_path_mp3 =  dir_mp3 + os.sep + file_name + ".mp3"
                file_path_wav =  dir_wav + os.sep + file_name + ".wav"
                dl = download(i, file_path_mp3)
                if dl is True:
                    cv = convert_wav(dir_ffmpeg, file_path_mp3, file_path_wav)
                    if cv is True:
                        to_text = audio_to_text(file_path_wav)
                        if to_text != "Error":
                            self.messageReceived.emit(f"{file_name} >>> {to_text}")
                            DATA_ALL.append([file_name, to_text])
                        else:
                            self.messageReceived.emit(f"{file_name} >>> Không nhập dạng được giọng nói")
                            DATA_ALL.append([file_name, "Không nhập dạng được giọng nói"])
            k += 1
            self.processBar.emit(k)
        self.enableBT.emit(True)
        shutil.rmtree(dir_root + os.sep + "output")
        self.popup.emit(["Process","Done!!!"])

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.progress_main.setValue(0)
        self.ui.bt_Clear.clicked.connect(self.removeLOG)
        self.ui.bt_Start.clicked.connect(self.loadDATA)
        self.ui.bt_Import.clicked.connect(self.openFileDialog)
        self.ui.bt_Export.clicked.connect(self.savefile)

    def addLOG(self, t):
        self.ui.resultView.append(t)

    def removeLOG(self):
        global DATA_ALL
        DATA_ALL = []
        self.ui.progress_main.setValue(0)
        self.ui.inputURL.clear()
        self.ui.resultView.clear()

    def enableBT(self, bl):
        if bl is True:
            self.ui.bt_Clear.setEnabled(True)
            self.ui.bt_Start.setEnabled(True)
            self.ui.bt_Export.setEnabled(True)
            self.ui.bt_Import.setEnabled(True)
        else:
            self.ui.bt_Clear.setEnabled(False)
            self.ui.bt_Start.setEnabled(False)
            self.ui.bt_Export.setEnabled(False)
            self.ui.bt_Import.setEnabled(False)

    def loadDATA(self):
        data = self.ui.inputURL.toPlainText()
        if data:
            self.data = data.split("\n")
            self.ui.progress_main.setMaximum(len(self.data))
            self.ui.progress_main.setValue(0)
            # Theard
            self.run_process = Host(self.data)
            self.run_process.messageReceived.connect(self.addLOG)
            self.run_process.processBar.connect(self.ui.progress_main.setValue)
            self.run_process.enableBT.connect(self.enableBT)
            self.run_process.popup.connect(self.popup)
            self.run_process.start()
        else:
            self.popup(["Input data", "Nothing!!!"])

    def openFileDialog(self):
        filename = QFileDialog.getOpenFileName(self,'Open File')
        if filename[0]:
            f = open(filename[0],'r')
            with f:
                data = f.read()
                self.ui.inputURL.setPlainText(data)

    def createTable(self):
        global DATA_ALL
        if DATA_ALL:
            self.tableWidget = QTableWidget()
            self.tableWidget.setRowCount(4)
            self.tableWidget.setColumnCount(2)
            self.tableWidget.setHorizontalHeaderLabels(['a','b'])
            for i in range(len(DATA_ALL)):
                for j in range(2):
                    self.tableWidget.setItem(i,j, QTableWidgetItem(DATA_ALL[i][j]))
            self.tableWidget.move(0,0)

    def savefile(self):
        self.createTable()
        filename = QFileDialog.getSaveFileName(self, 'Save File', '', ".xls(*.xls)")
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet("sheet", cell_overwrite_ok=True)
        for currentColumn in range(self.tableWidget.columnCount()):
            for currentRow in range(self.tableWidget.rowCount()):
                text = ""
                if self.tableWidget.item(currentRow, currentColumn) is not None:
                    text = str(self.tableWidget.item(currentRow, currentColumn).text())
                sheet.write(currentRow, currentColumn, text)
        wbk.save(filename[0])
        self.popup(["Export Data", "Done!!!"])

    def popup(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(text[0])
        msg.setText(text[1])
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == "__main__":
    dir_root = basedir()
    os.makedirs(dir_root + os.sep + "output", exist_ok=True)
    dir_mp3   = dir_root + os.sep + "output" + os.sep + "mp3"
    os.makedirs(dir_mp3, exist_ok=True)
    dir_wav  = dir_root + os.sep + "output" + os.sep + "wav"
    os.makedirs(dir_wav, exist_ok=True)
    dir_ffmpeg = dir_root + os.sep + "ffmpeg/bin/ffmpeg.exe"

    app = QApplication(sys.argv)
    clipboard = app.clipboard()
    window = MainWindow()
    window.setWindowTitle("Speech To Text - Google API | https://www.phucuongds.com")
    window.setWindowIcon(QIcon('favicon.ico'))
    window.show()
    sys.exit(app.exec())