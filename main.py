from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ui.uidesign import Ui_MainWindow
import sys
from subprocess import call
from time import time as ts
import os
from urllib.request import urlretrieve
import speech_recognition as sr
from threading import *


def basedir():
    if getattr(sys, 'frozen', False):
        BASEDIR = os.path.dirname(sys.executable)
    else:
        BASEDIR = os.getcwd()
    return BASEDIR

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.progress_main.setValue(0)
        self.ui.bt_Copy.clicked.connect(lambda: self.addLOG(t="hi"))
        self.ui.bt_Clear.clicked.connect(self.removeLOG)
        self.ui.bt_Start.clicked.connect(self.loadDATA)

    def addLOG(self, t):
        self.ui.resultView.append(t)

    def removeLOG(self):
        self.ui.inputURL.clear()
        self.ui.resultView.clear()

    def loadDATA(self):
        data = self.ui.inputURL.toPlainText()
        if data:
            self.data = data.split("\n")
            runner = Thread(target=self.loopData)
            runner.start()
        else:
            self.addLOG(t="Chưa nhập giá trị")

    def loopData(self):
        try:
            self.ui.progress_main.setMaximum(len(self.data))
            self.ui.bt_Copy.setEnabled(False)
            self.ui.bt_Clear.setEnabled(False)
            self.ui.bt_Start.setEnabled(False)
            self.ui.bt_Export.setEnabled(False)
            self.ui.bt_Import.setEnabled(False)
            k = 0
            for i in self.data:
                if i != "":
                    self.process(i)
                    self.ui.progress_main.setValue(k + 1)
        except Exception as e:
            self.addLOG(t="[Error] Lỗi không xác định.")
        finally:
            self.ui.bt_Copy.setEnabled(True)
            self.ui.bt_Clear.setEnabled(True)
            self.ui.bt_Start.setEnabled(True)
            self.ui.bt_Export.setEnabled(True)
            self.ui.bt_Import.setEnabled(True)

    def convert_url(self, url):
        number = url.find("id=")
        if number != -1:
            number = number + 3
            filename = url[number:]
        else:
            filename = int(ts())
        return filename
    
    def download(self, url, filename):
        try:
            urlretrieve(url, filename)
            return True
        except Exception as e:
            return False
        
    def convert_wav(self, f, i, o):
        try:
            call([f, '-hide_banner', '-v', 'error', '-y', '-i', i, o])
            return True
        except:
            return False

    def audio_to_text(self, audio_file):
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)  # Đọc dữ liệu âm thanh từ file
        try:
            text = r.recognize_google(audio, language="vi-VN")  # Nhận dạng giọng nói thành văn bản
            return text
        except sr.UnknownValueError:
            self.addLOG(t="[Error] Không thể nhận dạng giọng nói")
            return "Error"
        except sr.RequestError as e:
            self.addLOG(t="[Error] Lỗi trong việc truy cập dịch vụ nhận dạng giọng nói")
            return "Error"

    def process(self, url):
        try:
            self.addLOG(t=f"[Start] ...")
            file_name = str(self.convert_url(url))
            file_path_mp3 =  dir_mp3 + os.sep + file_name + ".mp3"
            file_path_wav =  dir_wav + os.sep + file_name + ".wav"
            # self.addLOG(t=f"[Process] Đang tải file âm thanh <{file_name}>...")
            dl = self.download(url, file_path_mp3)
            if dl is True:
                # self.addLOG(t="[Process] Đang chuyển đổi mp3 sang wav...")
                cv = self.convert_wav(dir_ffmpeg, file_path_mp3, file_path_wav)
                if cv is True:
                    # self.addLOG(t="[Process] Đang chuyển đổi giọng nói sang văn bản...")
                    to_text = self.audio_to_text(file_path_wav)
                    if to_text != "Error":
                        self.addLOG(t="[Info] Chuyển đổi thành công")
                        self.addLOG(t=f"{file_name} >>> {to_text}")
                else:
                    pass
                    # self.addLOG(t="[Error] Lỗi trong quá trình convert file.")
            else:
                pass
                # self.addLOG(t="[Error] Tải file âm thanh không thành công.")
        except:
            pass
            # self.addLOG(t="[Warning] Quá trình xử lý gặp lỗi không xác định.")

if __name__ == "__main__":
    dir_root = basedir()
    os.makedirs(dir_root + os.sep + "output", exist_ok=True)
    dir_mp3   = dir_root + os.sep + "output" + os.sep + "mp3"
    os.makedirs(dir_mp3, exist_ok=True)
    dir_wav  = dir_root + os.sep + "output" + os.sep + "wav"
    os.makedirs(dir_wav, exist_ok=True)
    dir_ffmpeg = dir_root + os.sep + "ffmpeg/bin/ffmpeg.exe"

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Speech To Text - Google API")
    window.show()
    sys.exit(app.exec())