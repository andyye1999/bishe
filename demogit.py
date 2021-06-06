# encoding:utf-8
import requests
import pyaudio
import wave
import webbrowser as web
from urllib.parse import quote
import snowboydecoder
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import signal
import time
import re
# pyaudio录音
def rec():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "recording.pcm"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("识别到唤醒词snowboy")
    print("请说出你想播放的歌曲名称")
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("识别完毕")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()



# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=【官网获取的AK】&client_secret=【官网获取的SK】'
response = requests.get(host)
if response:
    print(response.json())
from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = 'xxxx'
API_KEY = 'xxxx'
SECRET_KEY = 'xxxxxx'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 读取文件
def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()

# 语音识别音乐播放
def music():
    # 录音
    rec()
    # 识别本地文件
    result = client.asr(get_file_content('recording.pcm'), 'pcm', 16000, {
        'dev_pid': 1537,  # 默认1537（普通话 输入法模型），dev_pid参数见本节开头的表格
    })
    # time.sleep( 5 )
    # 显示歌曲名称
    str = result['result'][0]
    # 文本处理
    str1 = re.sub('播放歌曲','',str)
    print("歌曲名称为：")
    print(str1)
    print("正在搜索歌曲，请稍等。。。")
    # 汉字转码
    url_encode_name = quote(str1)
    # str1 = 'https://music.liuzhijin.cn/?name=%E5%AD%A6%E7%8C%AB%E5%8F%AB&type=netease'
    # https://music.liuzhijin.cn/?name=%E5%AD%A6%E7%8C%AB%E5%8F%AB&type=netease
    # 网站地址
    str2 = 'https://music.liuzhijin.cn/?name=%s&type=netease'%(url_encode_name)
    # 打开浏览器
    web.open(str2)



interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

#  回调函数，语音识别放在这里
def callbacks():
    global detector

    # 语音唤醒后，提示ding两声
    # snowboydecoder.play_audio_file()
    snowboydecoder.play_audio_file()
    snowboydecoder.play_audio_file()


    #  关闭snowboy功能
    detector.terminate()
    
    #  开启语音识别
    music()

    # 打开snowboy功能
    wake_up()    # wake_up —> monitor —> wake_up  递归调用

# 热词唤醒
def wake_up():

    global detector
    # /home/pi/snowboy/resources/models/snowboy.umdl
    model = './resources/models/snowboy.umdl'  #  唤醒词为 SnowBoy
    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # 唤醒词检测函数，调整sensitivity参数可修改唤醒词检测的准确性
    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    print('Listening... please say wake-up word:SnowBoy')
    # main loop
    # 回调函数 detected_callback=snowboydecoder.play_audio_file
    # 修改回调函数可实现我们想要的功能
    detector.start(detected_callback=callbacks,      # 自定义回调函数
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)
    # 释放资源
    detector.terminate()





# 主程序
if __name__ == "__main__":
    wake_up()