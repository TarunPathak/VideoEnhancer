#code: Tarun Pathak

##
#credit: icons downloaded from flaticon
##

#importing libraries
import utils, os
from PyQt5 import QtCore
from PyQt5.Qt import QIcon, Qt, QDialog
from PyQt5.QtWidgets import QGridLayout, QPushButton, QCheckBox, QLabel, QLineEdit, QSizePolicy, QMessageBox

#variables
app_path = utils.get_application_path()
app_icon = f"{app_path}\\assets\\icons\\app_icon.ico"

#custom dialog class
class EnhancerDialog(QDialog):

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
        self.setFixedSize(self.sizeHint().width() + 50, self.sizeHint().height() + 10)


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
        self.layout.addWidget(self.choose_folder_pb, 0, 2, 1, 1)

        self.audio_preferences_label = QLabel('<br><b>Audio<b><br><hr>')
        self.layout.addWidget(self.audio_preferences_label, 1, 0, 1, 1)
        self.retain_audio_cb = QCheckBox('Retain Audio')
        self.retain_audio_cb.setChecked(True)
        self.layout.addWidget(self.retain_audio_cb, 2, 0, 1, 1)

        self.proceed_pb = QPushButton('Proceed')
        self.proceed_pb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.proceed_pb.clicked.connect(lambda: self.__submit__())
        self.layout.addWidget(self.proceed_pb, 3, 0, 1, 3, Qt.AlignCenter)


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
                'Retain Audio': dialog.retain_audio_cb.isChecked()}