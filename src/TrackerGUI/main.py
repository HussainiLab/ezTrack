# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 11:21:06 2021

@author: vajra
"""

import os
import sys

from ComputeTracking import computeTracking
from functools import partial
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from worker_thread.Worker import Worker

# =========================================================================== #
        
class startWindow(QWidget):
    
    '''
        Main UI for selecting video files 
    '''

    def __init__(self):
        
        QWidget.__init__(self)
        
        # Setting main window geometry
        self.setGeometry(50, 50, 300, 100)
        self.center()
        self.mainUI()
        self.setWindowFlag(Qt.WindowCloseButtonHint, False) # Grey out 'X' button to prevent improper PyQt termination
        
    # ------------------------------------------- # 
    
    def center(self):

        '''
            Centers the GUI window on screen upon launch
        '''

        # Geometry of the main window
        qr = self.frameGeometry()

        # Center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # Move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # Top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())
        
    # ------------------------------------------- #  
    
    def mainUI(self):
        
        # Class porperties
        self.active_folder = None
        self.files = None
        self.folder = None
        self.list_of_paths = []
        self.downSample = 1
        self.method = 'dark'
        
        # Initialize layout and title
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Select video")
        
        # Widget creation
        single_processor = QPushButton('Process a single video', self)
        batch_processor = QPushButton('Process multiple videos', self)
        quit_button = QPushButton('Quit', self)
        
        self.downSample_Label = QLabel()
        self.downSample_Label.setText("Down sample factor per frame:")
        self.method_Label = QLabel()
        self.method_Label.setText("Color of subject to track is:")
        
        self.label = QLabel(self) 
        self.pixmap = QPixmap('ezTrack_logo.png') 
        self.pixmap = self.pixmap.scaledToWidth(256)
        self.label.setPixmap(self.pixmap)
        self.label.resize(100,100)
        
        downSampleBox = QComboBox()
        downSampleBox.setFixedWidth(60)
        downSampleBox.addItem("1")
        downSampleBox.addItem("0.75")
        downSampleBox.addItem("0.5")
        downSampleBox.addItem("0.25")
        
        methodBox = QComboBox()
        methodBox.setFixedWidth(60)
        methodBox.addItem("dark")
        methodBox.addItem("light")
        
        self.bar = QProgressBar(self)
        self.bar.setOrientation(Qt.Vertical)
        
        # Placing widgets in layout 
        self.layout.addWidget(self.label,0,0)
        self.layout.addWidget(self.bar, 0,1)
        self.layout.addWidget(self.downSample_Label,1,0)
        self.layout.addWidget(downSampleBox,2,0)
        self.layout.addWidget(self.method_Label,3,0)
        self.layout.addWidget(methodBox,4,0)
        self.layout.addWidget(single_processor, 5,0)
        self.layout.addWidget(batch_processor, 6,0)
        self.layout.addWidget(quit_button, 7,0)
        
        # Widget signalling
        quit_button.clicked.connect(self.quitClicked)
        single_processor.clicked.connect(partial(self.runSession, 0))
        batch_processor.clicked.connect(partial(self.runSession, 1))
        downSampleBox.activated[str].connect(self.downSampleChanged)
        methodBox.activated[str].connect(self.methodChanged)
        
    # ------------------------------------------- #
     
    def quitClicked(self):
        
       '''
           Application exit.
       '''
       
       print('quit')
       QApplication.quit()
       self.close()
    
    # ------------------------------------------- #
    
    def openDialog(self, mode, title):
        
        '''
            Will query OS to open file dialog box and user can choose video file/folder
            
            Params: 
                title (str) : 
                    Title that shows up at the top of the file dialog box
                mode (int):
                    Determines if user wants to choose files or a directory
                    mode=0 will invoke file selection
                    mode=1 will invoke folder selection
            Returns: 
                For mode 'files': List of file paths
                For mode 'folder': list containing one folder directory path
        '''
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        if mode == 0:
            files, _ = QFileDialog.getOpenFileNames(self, title, self.active_folder, options=options)
        
            if len(files) > 0:
                self.active_folder = dir_path = os.path.dirname(os.path.realpath((files[0]))) 
        
            return files

        elif mode == 1:
            folder = QFileDialog.getExistingDirectory(self, title)

            if len(folder) > 0:
                self.active_folder = dir_path = os.path.dirname(os.path.realpath((folder[0]))) 
            else:
                return 

            return folder
        
    # ------------------------------------------- #   
    
    def progressBar(self, n):
  
        '''
            Reflects progress of frequency map and scaling factor computations
        '''

        n = int(n)
        # Setting geometry to progress bar
        self.bar.setValue(n)
        
    # ------------------------------------------- #   
    
    def downSampleChanged(self, value):
        self.downSample = float(value)
        
    # ------------------------------------------- #  
    
    def methodChanged(self, value):
        self.method = value
        
    # ------------------------------------------- #  
    
    def runSession(self, mode):
        
        warn = QMessageBox()
        warn.setIcon(QMessageBox.Warning)
        warn.setWindowTitle("Warning")
        warn.setText("One or more of the chosen videos have unsupported formats and were removed from the processing queue. \n Supported video types are: 'avi', 'mkv', 'mov', 'mpg', 'mp4', 'wmv'.")
        
        if mode == 0:
            self.files = self.openDialog(0, "Select a video file/file(s)")
        else:
            self.folder = self.openDialog(1, "Select a folder of videos")
        
        file_formats = ['avi', 'mkv', 'mov', 'mpg', 'mp4', 'wmv']
        
        
        if self.files is not None:
            self.list_of_paths = self.files
        elif self.folder is not None:
            for file in os.listdir(self.folder):
                self.list_of_paths.append(os.path.abspath(file))
            
        # Remove any files that do not have correct file type
        original_length = len(self.list_of_paths)
        for i, file in enumerate(self.list_of_paths):
            if file.split('.')[-1] not in file_formats:
                self.list_of_paths.pop(i)
        
        # If anything was removed from the processing queue, alert user        
        if original_length > len(self.list_of_paths):
            warn.exec_()
            
        
        # Set and execute tracking function in worker thread
        self.worker = Worker(computeTracking, self.active_folder, self.list_of_paths, self.downSample, self.method)
        self.worker.start()
        self.worker.signals.progress.connect(self.progressBar)
        
                    
    # ------------------------------------------- #   
    
    def showTrackingWindow(self):
        
        '''
            Opens separate window where user can choose tracking options
        '''
        
        self.w = trackingProperties()
        # Closes main gui window
        self.w.show()
        self.close()
    
# =========================================================================== #
    
def main(): 
    
    '''
        Main function invokes application start.
    '''
    
    app = QApplication(sys.argv)
    screen = startWindow()
    screen.show()
    sys.exit(app.exec_())
    
if __name__=="__main__":
    main()
        