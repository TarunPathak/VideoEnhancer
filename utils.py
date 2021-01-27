#code: Tarun Pathak

#importing libraries
from PyQt5 import QtWidgets
from datetime import datetime
import sys, os, winshell, numpy as np
from PyQt5.QtWidgets import QFileDialog

#function to get screen size
def get_screen_size():
    return QtWidgets.QDesktopWidget().screenGeometry(-1)


#function to get application path
def get_application_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    elif __file__:
        return os.path.dirname(__file__)


#function to select video file
def get_video():
    return QFileDialog.getOpenFileName(None, 'Select Video', winshell.desktop(), 'Videos (*.mp4)')[0]


#function to calculate signal to noise ratio
def signaltonoise(a, axis=0, ddof=0):
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)


#function to calculate eta
def get_eta(start_time, frames_completed, remaining_frames):

    #time elapsed (in minutes)
    time_diff = datetime.now() - start_time

    #frames completed per second
    fps = frames_completed/ time_diff.total_seconds()

    #eta to complete remaining frames
    eta = remaining_frames/fps

    #converting eta to h:m:s format
    min, sec = divmod(eta, 60)
    hour, min = divmod(min, 60)

    #returning
    return "%d h:%02d m:%02d s" % (hour, min, sec)



