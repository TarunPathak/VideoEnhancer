#code: Tarun Pathak

##
#credit: icons downloaded from flaticon
##

#importing libraries
from time import sleep
from datetime import datetime
from PyQt5.QtGui import QPixmap
from qtwidgets import AnimatedToggle
from dialogs import PreferenceDialog
from vidgear.gears import WriteGear
from vidgear.gears.stabilizer import Stabilizer
from shutil import copyfile, rmtree
from PyQt5.Qt import QIcon, Qt, QImage
from scipy.ndimage.filters import median_filter
from moviepy.video.io.VideoFileClip import VideoFileClip
import sys, utils, cv2, numpy as np, os, uuid, qdarkstyle
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QGroupBox, QPushButton, QSizePolicy, QSplashScreen, QMessageBox

#variables
app_path = utils.get_application_path()
app_icon = f"{app_path}\\assets\\icons\\app_icon.ico"
ffmpeg_path = f"{app_path}\\assets\\ffmpeg\\bin\\"

#UI
class VideoEnhancer(QWidget):

    #init
    def __init__(self, app):

        #parent class
        QWidget.__init__(self)

        #app
        self.app = app

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
        self.label_height = self.geom.height() * 0.84

        #ui elements
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.actual_label = QLabel('<b>Actual<b>')
        self.actual_label.setFixedHeight(15)
        self.layout.addWidget(self.actual_label, 0, 0, 1, 1, Qt.AlignTop)
        self.processed_label = QLabel('<b>Processed<b>')
        self.processed_label.setFixedHeight(15)
        self.layout.addWidget(self.processed_label, 0, 1, 1, 1, Qt.AlignTop)

        self.actual_img_label = QLabel()
        self.actual_img_label.setStyleSheet("QLabel { background-color : #D3D3D3;}");
        self.actual_img_label.setFixedSize(self.label_width, self.label_height)
        self.layout.addWidget(self.actual_img_label, 1, 0, 1, 1, Qt.AlignTop)

        self.processed_img_label = QLabel()
        self.processed_img_label.setStyleSheet("QLabel { background-color : #D3D3D3;}");
        self.processed_img_label.setFixedSize(self.label_width, self.label_height)
        self.layout.addWidget(self.processed_img_label, 1, 1, 1, 1, Qt.AlignTop)

        self.gb = QGroupBox()
        self.gb_layout = QGridLayout()
        self.gb_layout.setAlignment(Qt.AlignLeft)
        self.gb.setLayout(self.gb_layout)

        self.open_label = QLabel('Enhance a video')
        self.gb_layout.addWidget(self.open_label, 0, 0, 1, 1)
        self.start_pb = QPushButton('Start')
        self.start_pb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.start_pb.clicked.connect(lambda: self.__process__())
        self.gb_layout.addWidget(self.start_pb, 0, 1, 1, 1)
        self.gb_layout.addWidget(QLabel('\tDark Theme'), 0, 2, 1, 1)
        self.skin_toggle = AnimatedToggle(checked_color="#4682B4", pulse_checked_color="#44FFB000")
        self.skin_toggle.clicked.connect(lambda: self.__manage_skin__())
        self.gb_layout.addWidget(self.skin_toggle, 0, 3, 1, 1, Qt.AlignRight)
        self.gb_layout.addWidget(QLabel(), 0, 4, 1, 1)
        self.file_label = QLabel()
        self.gb_layout.addWidget(self.file_label, 0, 5, 1, 1)
        self.gb_layout.addWidget(QLabel(), 0, 6, 1, 1)
        self.frame_counter_label = QLabel()
        self.gb_layout.addWidget(self.frame_counter_label, 0, 7, 1, 1)
        self.gb_layout.addWidget(QLabel(), 0, 8, 1, 1)
        self.eta_label = QLabel()
        self.gb_layout.addWidget(self.eta_label, 0, 9, 1, 1)
        self.layout.addWidget(self.gb, 2, 0, 1, 2, Qt.AlignTop)


    #function to change UI skin
    def __manage_skin__(self):

        if self.skin_toggle.isChecked():
            self.app.setStyleSheet(qdarkstyle.load_stylesheet())
        else:
            self.app.setStyleSheet(None)


    #function to select video file
    def __get_file__(self):

        #selecting file
        self.file_path = utils.get_video()
        basename = os.path.splitext(os.path.basename(self.file_path))
        self.file_name = basename[0]
        self.file_extension = basename[1]

        #displaying file path
        self.file_label.setText(f"{self.file_path}")


    #function to extract audio
    def __extract_audio__(self):

        clip = VideoFileClip(self.file_path)
        clip.audio.write_audiofile(f"{self.temp_dir}\\audio.mp3")


    #function to resize and convert opencv image to pixmap
    def __to_pixmap__(self, image):

        #converting to pixmap
        #based on number of channels
        if len(image.shape) == 3:
            img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        else:
            img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)

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


    #function to retain audio
    def __retain_audio__(self):

        command = \
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
                f"{self.temp_dir}\\{self.file_name}_with_audio{self.file_extension}",
            ]  # `-y` parameter is to overwrite output file if exists

        self.writer.execute_ffmpeg_cmd(command)


    #function to adjust volume
    def __adjust_volume__(self):

        #adjusting volume
        src = f"{self.temp_dir}\\{self.file_name}_with_audio{self.file_extension}"
        dest = f"{self.temp_dir}\\{self.file_name}_volume_adjusted{self.file_extension}"

        amount = int(self.preferences['Audio Level']['Amount'])
        amount_dict = {-50: .5, -60: .6, -70: .7, -80: .8,
                       -90: .9, 0: 1, 10: 1.1, 20: 1.2,
                       30: 1.3, 40: 1.4, 50: 1.5, 60: 1.6,
                       70: 1.7, 80: 1.8, 90: 1.9, 100: 2}

        command = ["-i", src, "-af", f"""volume={amount_dict[amount]}""", dest]
        print(command)
        self.writer.execute_ffmpeg_cmd(command)

        #deleting file
        #renaming volume adjusted file
        os.remove(src)
        os.rename(dest, src)


    #function to process the file
    def __process__(self):

        #selecting file
        #exiting (if no file is selected)
        self.__get_file__()

        if self.file_name=='':
            return

        #dialog
        self.preferences = PreferenceDialog.showDialog(self)

        #creating temp directory
        self.temp_dir = f"{app_path}\\processing\\{uuid.uuid4().hex}"
        os.mkdir(self.temp_dir)

        #extracting audio
        #if audio is to be retained
        if self.preferences['Retain Audio']:
            self.__extract_audio__()

        #video capture object
        cap = cv2.VideoCapture(self.file_path)

        #initiate stabilizer object with default parameters
        #if user selected the option
        if self.preferences['Enable Stablization']:
            stab = Stabilizer(smoothing_radius=20, crop_n_zoom=True, border_size=5, logging=True)

        #frame count
        counter = 1
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        #video writer object
        output_params = {"-vcodec": "libx264", "-crf": int(self.preferences['Compression']), "-preset": "fast"}
        self.writer = WriteGear(output_filename=f'{self.temp_dir}\\{self.file_name}_processed{self.file_extension}', custom_ffmpeg=ffmpeg_path, logging=True, **output_params)

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

                #copying frame
                frame_copy = frame

                #stablizing frame
                #if specified by user
                if self.preferences['Enable Stablization']:

                    stabilized_frame = stab.stabilize(frame_copy)

                    #wait for stabilizer which still be initializing
                    if stabilized_frame is None:
                        continue

                    #replacing frame
                    frame_copy = stabilized_frame

                #sharpening image

                modified_frame = self.__sharpen__(frame_copy, sigma=1)
                sharpen_psnr = cv2.PSNR(frame, modified_frame)

                #bilateral filter to reduce noise and smoothen image
                #the filter keeps edges intact
                #only implemented if psnr is high
                #higher psnr = better image quality
                bf_frame = cv2.bilateralFilter(modified_frame, 9, 50, 50)
                bf_psnr = cv2.PSNR(modified_frame, bf_frame)

                if bf_psnr > sharpen_psnr:
                    modified_frame = bf_frame

                #converting to B&W
                #if specified by user in preferences
                if self.preferences['BnW']:
                    modified_frame = cv2.cvtColor(modified_frame, cv2.COLOR_BGR2GRAY)

                #displaying frames
                self.actual_img_label.setPixmap(self.__to_pixmap__(frame))
                self.processed_img_label.setPixmap(self.__to_pixmap__(modified_frame))

                #wait
                cv2.waitKey(1)

                #write the flipped frame
                self.writer.write(modified_frame)

                #incrementing frame count
                counter = counter + 1

            else:
                break

        #release everything
        cap.release()
        self.writer.close()
        cv2.destroyAllWindows()

        #using FFmpeg to stitch audio back
        #if specified in setting
        #performing other audio related operations
        if self.preferences['Retain Audio']:

            #retaining audio
            self.__retain_audio__()

            #adjusting volume
            #if specified in preferences
            if self.preferences['Audio Level']['Checked']:
                self.__adjust_volume__()


        #adding thumbnail
        command = ["-y", "-i", f"{self.temp_dir}\\{self.file_name}_with_audio{self.file_extension}", "-ss", "00:00:05.000", "-vframes", "1", f"{self.temp_dir}\\Thumbnail.png"]
        self.writer.execute_ffmpeg_cmd(command)

        command = ["-i", f"{self.temp_dir}\\{self.file_name}_with_audio{self.file_extension}", "-i", f"{self.temp_dir}\\Thumbnail.png", "-map", "0", "-map", "1", "-c", "copy", "-c:v:1",
                   "png", "-disposition:v:1", "attached_pic", f"{self.temp_dir}\\{self.file_name}_with_thumbnail{self.file_extension}"]
        self.writer.execute_ffmpeg_cmd(command)

        #copying the file
        src = f"{self.temp_dir}\\{self.file_name}_with_thumbnail{self.file_extension}"
        dest = f"{self.preferences['Output Folder']}\\{self.file_name}_video_enhancer{self.file_extension}"
        copyfile(src, dest)

        #deleting temp directory
        rmtree(self.temp_dir, ignore_errors=True)

        #notifying user
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Information')
        msg.setWindowIcon(QIcon(app_icon))
        msg.setText('Done!\nFile has been saved in source folder.')
        msg.exec_()


#splash screen
def splash(app):

    #displaying splash
    splash_pix = QPixmap(utils.get_application_path() + '\\assets\\icons\\splash.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()

    for i in range(0,3):
        sleep(0.6)
        app.processEvents()

    #closing splash
    splash.close()

#main
if __name__ == '__main__':

    #creating application
    app = QApplication(sys.argv)

    #setting dark stylesheet
    #app.setStyleSheet(qdarkstyle.load_stylesheet())

    #displaying splash screen
    splash(app)

    #displaying application
    widget = VideoEnhancer(app=app)
    sys.exit(app.exec_())