#code: Tarun Pathak

##
#credit: icons downloaded from flaticon
##

#importing libraries
import utils, os
from PyQt5 import QtCore
from PyQt5.Qt import QIcon, Qt, QDialog
from PyQt5.QtWidgets import QGridLayout, QPushButton, QCheckBox, QLabel, QLineEdit, QSizePolicy, QMessageBox, QComboBox, QSlider, QGroupBox

#variables
app_path = utils.get_application_path()
app_icon = f"{app_path}\\assets\\icons\\app_icon.ico"

#custom dialog class
class PreferenceDialog(QDialog):

    #init
    def __init__(self, parent=None):

        #passing arguments to parent class
        self.parent = parent
        QDialog.__init__(self, parent)

        #general properties
        self.setWindowTitle('Preferences')
        self.setWindowIcon(QIcon(app_icon))
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        #building UI
        self.__build_ui__()

        #setting size
        self.setFixedSize(self.sizeHint().width(), self.sizeHint().height() + 10)


    #function to build ui
    def __build_ui__(self):

        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.output_folder_label = QLabel('Output Folder')
        self.layout.addWidget(self.output_folder_label, 0, 0, 1, 1)
        self.output_folder_le = QLineEdit()
        self.output_folder_le.setEnabled(False)
        self.output_folder_le.setText(os.path.dirname(self.parent.file_path))
        self.output_folder_le.setFixedWidth(250)
        self.layout.addWidget(self.output_folder_le, 0, 1, 1, 1)
        self.choose_folder_pb = QPushButton('...')
        self.choose_folder_pb.clicked.connect(lambda: self.output_folder_le.setText(utils.get_folder()))
        self.choose_folder_pb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(self.choose_folder_pb, 0, 2, 1, 2)

        self.audio_preferences_label = QLabel('<br><b>Audio<b><br><hr>')
        self.layout.addWidget(self.audio_preferences_label, 1, 0, 1, 1)
        self.retain_audio_cb = QCheckBox('Retain Audio')
        self.retain_audio_cb.setChecked(True)
        self.retain_audio_cb.stateChanged.connect(lambda: self.__manage_widgets__())
        self.layout.addWidget(self.retain_audio_cb, 2, 0, 1, 1)

        self.audio_gb = QGroupBox()
        self.audio_gb_layout = QGridLayout()
        self.audio_gb_layout.setAlignment(Qt.AlignLeft)
        self.audio_gb.setLayout(self.audio_gb_layout)
        self.layout.addWidget(self.audio_gb, 2, 1, 1, 2)

        self.audio_level_cb = QCheckBox(' adjust volume by:\n Negative adjustment results in volume reduction.')
        self.audio_level_cb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.audio_level_cb.stateChanged.connect(lambda: self.__manage_widgets__())
        self.audio_gb_layout.addWidget(self.audio_level_cb, 0, 0, 1, 1)
        self.audio_slider = QSlider(Qt.Horizontal)
        self.audio_slider.setEnabled(False)
        self.audio_slider.setMinimum(-50)
        self.audio_slider.setMaximum(100)
        self.audio_slider.setValue(10)
        self.audio_slider.setTickInterval(10)
        self.audio_slider.setSingleStep(10)
        self.audio_slider.setPageStep(10)
        self.audio_slider.setTickPosition(QSlider.TicksBelow)
        self.audio_slider.valueChanged.connect(lambda: self.slider_le.setText(f"{self.audio_slider.value()}%"))
        self.audio_gb_layout.addWidget(self.audio_slider, 1, 0, 1, 1)
        self.slider_le = QLineEdit()
        self.slider_le.setText('5%')
        self.slider_le.setFixedWidth(40)
        self.slider_le.setEnabled(False)
        self.audio_gb_layout.addWidget(self.slider_le, 1, 2, 1, 1)

        self.color_preferences_label = QLabel('<br><b>Color<b><br><hr>')
        self.layout.addWidget(self.color_preferences_label, 3, 0, 1, 1)
        self.bnw_cb = QCheckBox('Convert to Black && White')
        self.layout.addWidget(self.bnw_cb, 4, 0, 1, 1)

        self.proceed_pb = QPushButton('Proceed')
        self.proceed_pb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.proceed_pb.clicked.connect(lambda: self.__submit__())
        self.layout.addWidget(self.proceed_pb, 5, 0, 1, 3, Qt.AlignCenter)


    #function to manage widgets
    def __manage_widgets__(self):

        if self.sender() == self.audio_level_cb:

            if self.audio_level_cb.isChecked():
                self.audio_slider.setEnabled(True)
            else:
                self.audio_slider.setEnabled(False)

        elif self.sender() == self.retain_audio_cb:

            if not self.retain_audio_cb.isChecked():
                self.audio_level_cb.setChecked(False)
                self.audio_level_cb.setEnabled(False)
            else:
                self.audio_level_cb.setEnabled(True)



    #function to submit data
    def __submit__(self):

        #exiting (if output folder is not choosen)
        if self.output_folder_le.text() == '':

            #notifying user
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle('Information')
            msg.setWindowIcon(QIcon(app_icon))
            msg.setText('Please select the output folder.')
            msg.exec_()

            #return
            return

        #closing dialog
        self.close()


    #class method to return data
    @classmethod
    def showDialog(cls, parent):

        dialog = cls(parent=parent)
        dialog.exec_()
        return {'Output Folder': dialog.output_folder_le.text(),
                'Retain Audio': dialog.retain_audio_cb.isChecked(),
                'Audio Level': {'Checked': dialog.audio_level_cb.isChecked(),
                                'Amount': dialog.audio_slider.value()
                                },
                'BnW': dialog.bnw_cb.isChecked()}