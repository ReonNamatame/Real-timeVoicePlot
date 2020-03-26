import pyaudio #handling recording function
import wave #handling .wav file
from os import listdir, makedirs

#プロット関係のライブラリ
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import sys

#beginning of class Recorder
class Recorder(object):
#public methods
    def __init__(self):
        # recording time (unit: s)
        self.__record_time = 5
        # file name
        self.__output_wavfile = ["record.wav"]
        # index number of microphone
        self.__idevice = 1
        # format of audio
        self.__format = pyaudio.paInt16
        # monaural
        self.__nchannels = 1
        # sampling rate,which is usually 16KHz(=16kHz?) In the special case, raspberryPi needs 44.1kHz
        self.__sampling_rate = 44100 #8192*2
        # number of extracted data at a time,that is called chunk
        self.__chunk = 2**10
        # get device information
        self.__audio = pyaudio.PyAudio()
        # instance of stream obj for making wav file
        self.__stream = None

        self.byte_data = []
    
    def set_config(self, time_sec=3, outfile=["record.wav"], device_index=1, sampling_rate=44100, chunk=2**10, format=pyaudio.paInt16, nchannels=1):
        # configure foundimental information

        # recording time (unit: s)
        self.__record_time = time_sec
        # file name
        self.__output_wavfile = outfile
        # index number of microphone
        self.__idevice = device_index
        # sampling rate,which is usually 16kHz
        self.__sampling_rate = sampling_rate
        # number of extracted data at a time,that is called chunk
        self.__chunk = chunk
        # format of audio
        self.__format = format
        # monaural
        self.__nchannels = nchannels
    
    def get_chunk(self):
        return self.__chunk

    def get_output_file_list(self):
        return self.__output_wavfile
    
    def get_device_info(self):
        for i in range(self.__audio.get_device_count()):
            print(self.__audio.get_device_info_by_index(i))

    def record_voice(self, wfile_list=["record.wav"], dst="./control/audioSample/", overwrite=False) -> list:
        if dst[-1] != "/":
            print("Destination must be ended with \"/\"")
            raise NotADirectoryError

        makedirs(dst, exist_ok=True) # check if dst already exists. If doesn't, make new dir
        if overwrite == False and set.intersection(set(wfile_list), listdir(dst)) != set():
            print("Same wavfile exists in {0}\nYou were about to overwrite {1}\nIf you wouldn't mind it, set overwrite flag True".format(dst, dst+w))
            raise FileExistsError

        #audio.open() method returns a new Stream instance taking some arguments for configuration
        self.__stream = self.__audio.open(
            format = self.__format,
            channels = self.__nchannels,
            rate = self.__sampling_rate,
            input = True,
            output = False,
            input_device_index = self.__idevice, # device1(Mouse_mic) will be used for input device
            frames_per_buffer = self.__chunk
        )
        write_to_stream_time = int(self.__sampling_rate * self.__record_time / self.__chunk)
        for w in wfile_list:
            print("Start recording...")
            #self.byte_data = [self.__stream.read(self.__chunk) for _ in range(write_to_stream_time)]
            self.byte_data = []
            for i in range(0, write_to_stream_time):
                data = self.__stream.read(self.__chunk) #write raw data in the stream at each chunk
                self.byte_data.append(data)
            print("Finished recording")
            #self.__make_wav_file(self.byte_data, dst+w)
            print("Wav file was generated\n")
        self.__output_wavfile = wfile_list
        self.__close_all()
        return self.__output_wavfile

#private methods          
    def __make_wav_file(self, frames, wfile, mode='wb'):
        wavefile = wave.open(wfile, mode)
        wavefile.setnchannels(self.__nchannels)
        wavefile.setsampwidth(self.__audio.get_sample_size(self.__format))
        wavefile.setframerate(self.__sampling_rate)
        wavefile.writeframes(b"".join(frames))
        wavefile.close()
        return wfile

    def __close_all(self):
        self.__stream.close()
        self.__audio.terminate()
        print("pyaudio was terminated")

#end of class Recorder

class VoicePlotWindow(object):
    
    def __init__(self):
        # recording time (unit: s)
        self.__record_time = 3
        # file name
        self.__output_wavfile = ["record.wav"]
        # index number of microphone
        self.__idevice = 1
        # format of audio
        self.__format = pyaudio.paInt16
        # monaural
        self.__nchannels = 1
        # sampling rate,which is usually 16KHz(=16kHz?) In the special case, raspberryPi needs 44.1kHz
        self.__sampling_rate = 44100 #8192*2
        # number of extracted data at a time,that is called chunk
        self.__chunk = 2**10
        # get device information
        self.__audio = pyaudio.PyAudio()
        # instance of stream obj for making wav file
        self.__stream = None

        self.byte_data = []
        self.win=pg.GraphicsWindow()
        self.win.setWindowTitle("Real-time plot")
        self.plt=self.win.addPlot() #プロットのビジュアル関係
        self.plt.setYRange(-1,1)    #y軸の上限、下限の設定
        self.curve=self.plt.plot()  #プロットデータを入れる場所
        
        #アップデート時間設定
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)    #10msごとにupdateを呼び出し
        
        #音声データの格納場所(プロットデータ)
        self.plot_data = np.zeros(self.__chunk)
    
    def set_config(self, time_sec=3, outfile=["record.wav"], device_index=1, sampling_rate=44100, chunk=2**10, format=pyaudio.paInt16, nchannels=1):
        # configure foundimental information

        # recording time (unit: s)
        self.__record_time = time_sec
        # file name
        self.__output_wavfile = outfile
        # index number of microphone
        self.__idevice = device_index
        # sampling rate,which is usually 16kHz
        self.__sampling_rate = sampling_rate
        # number of extracted data at a time,that is called chunk
        self.__chunk = chunk
        # format of audio
        self.__format = format
        # monaural
        self.__nchannels = nchannels
    
    def get_chunk(self):
        return self.__chunk

    def get_output_file_list(self):
        return self.__output_wavfile
    
    def get_device_info(self):
        for i in range(self.__audio.get_device_count()):
            print(self.__audio.get_device_info_by_index(i))

    def record_voice(self, wfile_list=["record.wav"], dst="./control/audioSample/", overwrite=False) -> list:
        if dst[-1] != "/":
            print("Destination must be ended with \"/\"")
            raise NotADirectoryError

        makedirs(dst, exist_ok=True) # check if dst already exists. If doesn't, make new dir
        if overwrite == False and set.intersection(set(wfile_list), listdir(dst)) != set():
            print("Same wavfile exists in {0}\nYou were about to overwrite {1}\nIf you wouldn't mind it, set overwrite flag True".format(dst, dst+w))
            raise FileExistsError

        #audio.open() method returns a new Stream instance taking some arguments for configuration
        self.__stream = self.__audio.open(
            format = self.__format,
            channels = self.__nchannels,
            rate = self.__sampling_rate,
            input = True,
            output = False,
            input_device_index = self.__idevice, # device1(Mouse_mic) will be used for input device
            frames_per_buffer = self.__chunk
        )
        write_to_stream_time = int(self.__sampling_rate * self.__record_time / self.__chunk)
        for w in wfile_list:
            print("Start recording...")
            #self.byte_data = [self.__stream.read(self.__chunk) for _ in range(write_to_stream_time)]
            self.byte_data = []
            for i in range(0, write_to_stream_time):
                b_data = self.__stream.read(self.__chunk) #write raw data in the stream at each chunk
                self.byte_data.append(b_data)
            print("Finished recording")
            #self.__make_wav_file(self.byte_data, dst+w)
            print("Wav file was generated\n")
        self.__output_wavfile = wfile_list
        self.__close_all()
        return self.__output_wavfile

#private methods          
    def __make_wav_file(self, frames, wfile, mode='wb'):
        wavefile = wave.open(wfile, mode)
        wavefile.setnchannels(self.__nchannels)
        wavefile.setsampwidth(self.__audio.get_sample_size(self.__format))
        wavefile.setframerate(self.__sampling_rate)
        wavefile.writeframes(b"".join(frames))
        wavefile.close()
        return wfile

    def __close_all(self):
        self.__stream.close()
        self.__audio.terminate()
        print("pyaudio was terminated")

    def update(self):
        next_chunk = self.byte_data[self.prev:self.next]
        next_chunk = np.frombuffer(b"".join(next_chunk), dtype="int16") / 2**15
        self.plot_data = np.append(self.plot_data, next_chunk)
        self.prev = self.next
        self.next = self.next + self.get_chunk()
        self.curve.setData(self.plot_data)   #プロットデータを格納
    
if __name__=="__main__":
    
    plotwin = VoicePlotWindow()
    
    plotwin.record_voice(wfile_list=["one.wav", "two.wav"], dst="./audioSample/", overwrite=True)
    
    if (sys.flags.interactive!=1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_() 