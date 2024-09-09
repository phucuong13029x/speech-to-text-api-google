from subprocess import call
from time import time as ts
from urllib.request import urlretrieve
import speech_recognition as sr


def convert_url(url):
    number = url.find("id=")
    if number != -1:
        number = number + 3
        filename = url[number:]
    else:
        filename = int(ts())
    return filename

def download(url, filename):
    try:
        urlretrieve(url, filename)
        return True
    except Exception as e:
        return False
    
def convert_wav(f, i, o):
    try:
        call([f, '-hide_banner', '-v', 'error', '-y', '-i', i, o])
        return True
    except Exception as e:
        print(e)
        return False

def audio_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)  # Đọc dữ liệu âm thanh từ file
    try:
        text = r.recognize_google(audio, language="vi-VN")  # Nhận dạng giọng nói thành văn bản
        return text
    except sr.UnknownValueError:
        # print("[Error] Không thể nhận dạng giọng nói")
        return "Error"
    except sr.RequestError as e:
        # print("[Error] Lỗi trong việc truy cập dịch vụ nhận dạng giọng nói")
        return "Error"