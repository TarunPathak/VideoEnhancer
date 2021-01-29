#code: Tarun Pathak

##
#credit: icons downloaded from flaticon
##

#importing libraries
from shutil import copyfile
from datetime import datetime
from PyQt5.QtGui import QPixmap
from vidgear.gears import WriteGear
from PyQt5.Qt import QIcon, Qt, QImage
import sys, utils, cv2, numpy as np, os, uuid
from scipy.ndimage.filters import median_filter
from moviepy.video.io.VideoFileClip import VideoFileClip
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QGroupBox, QPushButton, QSizePolicy, QCheckBox, QMessageBox

#variables
app_path = utils.get_application_path()
app_icon = f"{app_path}\\assets\\icons\\app_icon.ico"

#UI
class Application(QWidget):

    #init
    def __init__(self):

        #parent class
        QWidget.__init__(self)

        #general properties
        self.setWindowTitle('Video Enhancer')
        self.setWindowIcon(QIcon(app_icon))

        self.geom= utils.get_screen_size()
        self.setFixedSize(self.geom.width(), self.geom.height())

        #creating interface
        self.__build_ui__()

        #displaying
        self.showMaximized()


    #function to create UI
    def __build_ui__(self):

        #ui dimensions
        self.label_width = (self.geom.width()-50)/2
        self.label_height = self.geom.height() * 0.78

        #ui elements
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.actual_img_label = QLabel()
        self.actual_img_label.setStyleSheet("QLabel { background-color : #D3D3D3;}");
        self.actual_img_label.setFixedSize(self.label_width, self.label_height)
        self.layout.addWidget(self.actual_img_label, 0, 0, 1, 1, Qt.AlignTop)

        self.processed_img_label = QLabel()
        self.processed_img_label.setStyleSheet("QLabel { background-color : #D3D3D3;}");
        self.processed_img_label.setFixedSize(self.label_width, self.label_height)
        self.layout.addWidget(self.processed_img_label, 0, 1, 1, 1, Qt.AlignTop)

        self.gb = QGroupBox()
        self.gb_layout = QGridLayout()
        self.gb_layout.setAlignment(Qt.AlignLeft)
        self.gb.setLayout(self.gb_layout)

        self.open_label = QLabel('Select the video')
        self.gb_layout.addWidget(self.open_label, 0, 0, 1, 1)
        self.browse_pb = QPushButton('Browse')
        self.browse_pb.clicked.connect(lambda: self.__get_file__())
        self.browse_pb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.gb_layout.addWidget(self.browse_pb, 0, 1, 1, 1)
        self.gb_layout.addWidget(QLabel(), 0, 2, 1, 1)
        self.file_label = QLabel()
        self.gb_layout.addWidget(self.file_label, 0, 3, 1, 1)
        self.gb_layout.addWidget(QLabel(), 0, 4, 1, 1)
        self.frame_counter_label = QLabel()
        self.gb_layout.addWidget(self.frame_counter_label, 0, 5, 1, 1)
        self.gb_layout.addWidget(QLabel(), 0, 6, 1, 1)
        self.eta_label = QLabel()
        self.gb_layout.addWidget(self.eta_label, 0, 7, 1, 1)

        self.pref_label = QLabel('\nPreferences\n')
        self.gb_layout.addWidget(self.pref_label, 1, 0, 1, 2)
        self.retain_audio_cb = QCheckBox('Retain Audio')
        self.retain_audio_cb.setChecked(True)
        self.gb_layout.addWidget(self.retain_audio_cb, 2, 0, 1, 2)

        self.gb_layout.addWidget(QLabel(), 3, 0, 1, 2)

        self.start_pb = QPushButton('Start')
        self.start_pb.setEnabled(False)
        self.start_pb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.start_pb.clicked.connect(lambda: self.__process__())
        self.gb_layout.addWidget(self.start_pb, 4, 0, 1, 1)
        self.pause_pb = QPushButton('Pause')
        self.pause_pb.setEnabled(False)
        self.pause_pb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.gb_layout.addWidget(self.pause_pb, 4, 1, 1, 1)

        self.layout.addWidget(self.gb, 1, 0, 1, 2, Qt.AlignTop)


    #function to select video file
    def __get_file__(self):

        #selecting file
        self.file_path = utils.get_video()
        basename = os.path.splitext(os.path.basename(self.file_path))
        self.file_name = basename[0]
        self.file_extension = basename[1]

        #displaying file path
        self.file_label.setText(f"{self.file_path}")

        #managing start/pause buttons
        if not len(self.file_path) > 0:

            if self.start_pb.isEnabled():
                self.start_pb.setEnabled(False)

            if self.pause_pb.isEnabled():
                self.pause_pb.setEnabled(False)

        else:

            if not self.start_pb.isEnabled():
                self.start_pb.setEnabled(True)

            if not self.pause_pb.isEnabled():
                self.pause_pb.setEnabled(True)


    #function to extract audio
    def __extract_audio__(self):

        clip = VideoFileClip(self.file_path)
        clip.audio.write_audiofile(f"{self.temp_dir}\\audio.mp3")


    #function to equalize histogram
    def __equalize_histogram__(self, image):

        img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2, 2))
        img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])
        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)


    #function to resize and convert opencv image to pixmap
    def __to_pixmap__(self, image):

        #converting to pixmap
        img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        return QPixmap.fromImage(img)


    #function to sharpen image
    def __sharpen__(self, image, sigma=5, strength=1):

        #creating empty image vector
        output = np.zeros_like(image)

        #running sharpness on each channel
        for c in range(image.shape[2]):

            #channel
            channel = image[:, :, c]

            #median filter (noise removal)
            #sigma (kernel size) has to be a positive odd integer
            image_med = median_filter(channel, sigma)

            #calculate the Laplacian
            #laplacian does edge detection
            image_lap = cv2.Laplacian(image_med, cv2.CV_64F)

            #sharpening image
            #strength is the amount of laplacian we want to apply
            #max value can be 1
            sharp = channel - strength * image_lap

            #saturate the pixels in either direction
            sharp[sharp > 255] = 255
            sharp[sharp < 0] = 0

            output[:, :, c] = sharp

        return output


    #function to process the file
    def __process__(self):

        #creating temp directory
        self.temp_dir = f"{app_path}\\processing\\{uuid.uuid4().hex}"
        os.mkdir(self.temp_dir)

        #extracting audio
        #if audio is to be retained
        if self.retain_audio_cb.isChecked():
            self.__extract_audio__()

        #video capture object
        cap = cv2.VideoCapture(self.file_path)

        #frame count
        counter = 1
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        #video writer object
        output_params = {"-vcodec": "libx264", "-crf": 0, "-preset": "fast"}
        writer = WriteGear(output_filename=f'{self.temp_dir}\\{self.file_name}_processed{self.file_extension}', logging=True, **output_params)

        #processing till end of frame
        start_time = datetime.now()

        while cap.isOpened():

            #frame
            ret, frame = cap.read()

            if ret == True and not frame is None:

                #updating frame counter
                self.frame_counter_label.setText(f"\tFrame <b>{counter}</b> of <b>{frame_count}</b>")

                #updating eta
                eta = utils.get_eta(start_time, frames_completed=counter, remaining_frames=frame_count - counter)
                self.eta_label.setText(f'\tEstimated Time: {eta}')

                #sharpening image
                modified_frame = self.__sharpen__(frame, sigma=1)

                #displaying frames
                self.actual_img_label.setPixmap(self.__to_pixmap__(frame))
                self.processed_img_label.setPixmap(self.__to_pixmap__(modified_frame))

                #wait
                cv2.waitKey(1)

                #write the flipped frame
                writer.write(modified_frame)

                #incrementing counter
                counter = counter + 1

            else:
                break

        #release everything
        cap.release()
        writer.close()
        cv2.destroyAllWindows()

        #using FFmpeg to stitch audio back
        #if specified in setting
        if self.retain_audio_cb.isChecked():

            ffmpeg_command = \
            [
                "-y",
                "-i",
                f"{self.temp_dir}\\{self.file_name}_processed{self.file_extension}",
                "-i",
                f"{self.temp_dir}\\audio.mp3",
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-shortest",
                f"{self.temp_dir}\\{self.file_name}_processed{self.file_extension}",
            ]  # `-y` parameter is to overwrite output file if exists

            #execute FFmpeg command
            writer.execute_ffmpeg_cmd(ffmpeg_command)

        #adding thumbnail
        command = ["-y", "-i", f"{self.temp_dir}\\{self.file_name}_processed{self.file_extension}", "-ss", "00:00:05.000", "-vframes", "1", f"{self.temp_dir}\\Thumbnail.png"]
        writer.execute_ffmpeg_cmd(command)

        command = ["-i", f"{self.temp_dir}\\{self.file_name}_processed{self.file_extension}", "-i", f"{self.temp_dir}\\Thumbnail.png", "-map", "0", "-map", "1", "-c", "copy", "-c:v:1",
                   "png", "-disposition:v:1", "attached_pic", f"{self.temp_dir}\\{self.file_name}{self.file_extension}"]
        writer.execute_ffmpeg_cmd(command)

        #copying the file
        src = f"{self.temp_dir}\\{self.file_name}{self.file_extension}"
        dest = f"{os.path.dirname(self.file_path)}\\{self.file_name}_video_enhancer{self.file_extension}"
        copyfile(src, dest)

        #notifying user
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Information')
        msg.setInformativeText('Done!\nFile has been saved in source folder.')
        msg.exec_()


#main
if __name__ == '__main__':

    #creating application
    app = QApplication(sys.argv)
    widget = Application()
    sys.exit(app.exec_())