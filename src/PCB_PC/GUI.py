# -*- coding: utf-8 -*-
import sys
from web_func import *
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
from PIL import Image, ImageDraw

# class for display the main window
class Example(QMainWindow):

    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
    def initUI(self):
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid) 

        # buttons basic settsing
        quitButton = QtGui.QPushButton('&Quit')
        self.connect(quitButton, SIGNAL('clicked()'),self.close)

        caliButton = QPushButton('C&alibration', self)
        self.connect(caliButton, SIGNAL('clicked()'), self.show_cali_window)

        checkButton = QPushButton('C&heck', self)
        self.connect(checkButton, SIGNAL('clicked()'), self.show_check_window) 

        adsButton = QPushButton('Advanced settings', self)
        self.connect(adsButton, SIGNAL('clicked()'), self.ads_window)

        # set the shortcut of the buttons
        caliButton.setShortcut('Ctrl+A')
        checkButton.setShortcut('Ctrl+H')
        quitButton.setShortcut('Ctrl+Q') 

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)        
        grid.addWidget(caliButton, 1, 0)
        grid.addWidget(checkButton, 2, 0)
        grid.addWidget(adsButton, 3, 0)
        grid.addWidget(quitButton, 4, 0)

        wid.setLayout(grid)
        self.center()
        self.setWindowTitle('Main Window')
        self.show() 
    def show_cali_window(self):
        self.my_cali_window = caliWindow()
        self.my_cali_window.show()
    def show_check_window(self):
        self.my_check_window = checkWindow()
        self.my_check_window.show()
        
    def ads_window(self):
        self.my_adsWindow = adsWindow()
        self.my_adsWindow.show()
    # set the GUI to display in the center of the screen
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class adsWindow(QMainWindow):
    def __init__(self):
        super(adsWindow, self).__init__()
        self.initUI()
    def initUI(self):
        # basic settings
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid) 
        self.statusBar()

        # labels
        expText = QtGui.QLabel('Exposure')
        timesText = QtGui.QLabel('Test times')
        self.expLow = QtGui.QLineEdit()
        self.expHigh = QtGui.QLineEdit()
        self.time_num = QtGui.QLineEdit()

        # auto refresh after press Enter
        self.expLow.returnPressed.connect(self.auto_refresh)
        self.expHigh.returnPressed.connect(self.auto_refresh)
        self.time_num.returnPressed.connect(self.auto_refresh)

        # settings of the grid layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(10) 
        grid.addWidget(expText, 1, 0)
        grid.addWidget(self.expLow, 1, 1)
        grid.addWidget(QtGui.QLabel('to'), 1, 2)
        grid.addWidget(self.expHigh, 1, 3)
        grid.addWidget(timesText, 2, 0)
        grid.addWidget(self.time_num, 2, 1, 2, 3)

        # show the grid layout
        wid.setLayout(grid)
        self.center()
        self.setWindowTitle('Advanced settings')

        # get the settings now
        self.show_ads()

        # show it 
        self.show()

    def show_ads(self):
        low, high, times = get_ads()
        self.expLow.setText(str(low))
        self.expHigh.setText(str(high))
        self.time_num.setText(str(times))
        return low, high, times

    def upload_ads(self):
        neo_low = int(self.expLow.text())
        neo_high = int(self.expHigh.text())
        neo_test_num = int(self.time_num.text())
        set_ads(neo_low, neo_high, neo_test_num)

    def auto_refresh(self):
        self.upload_ads()
        low, high, times = self.show_ads()
        text = u'Upload exp({_low}, {_high}) times：{_times}'
        text = text.format(_low = low, _high = high, _times = times)
        self.statusBar().showMessage(text)
    # set the GUI to display in the center of the screen
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class caliWindow(QMainWindow):
    def __init__(self):
        super(caliWindow, self).__init__()
        self.initUI()
    def initUI(self):
        # basic settings
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid) 
        self.statusBar()

        # buttons basic settsing
        quitButton = QtGui.QPushButton('&Quit')
        self.connect(quitButton, SIGNAL('clicked()'),self.close)

        startButton = QPushButton('&Start', self)
        self.connect(startButton, SIGNAL('clicked()'), self.start_cali)

        uploadButton = QPushButton('&Upload', self)
        self.connect(uploadButton, SIGNAL('clicked()'), self.upload)
        
        detailButton = QPushButton('&Detail information', self)
        self.connect(detailButton, SIGNAL('clicked()'), self.detail_window)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)        
        grid.addWidget(startButton, 1, 0)
        grid.addWidget(uploadButton, 2, 0)
        grid.addWidget(detailButton, 3, 0)
        grid.addWidget(quitButton, 4, 0)

        wid.setLayout(grid)
        self.center()
        self.setWindowTitle('Calibration')

    def detail_window(self):
        self.detail_cali_info = cali_info()
        self.detail_cali_info.show()

    def start_cali(self):
        GPIO_start()
        global ledlist
        ledlist = []
        smf_len = get_smf_len()
        # big FOR to look patterns
        for i in range(0, smf_len):
            text4show = 'pattern {pattern_num} is working ...'
            text4show = text4show.format(pattern_num = i+1)
            self.statusBar().showMessage(text4show)
            self.statusBar().showMessage(text4show)
            pos, pointNum = look(i, 1)
            ledlist.append(pos)
        GPIO_clean()
        self.statusBar().showMessage('Calibration finished')

    def upload(self):
        save_msg = "Are you sure you want to upload the new led list?"
        reply = QtGui.QMessageBox.question(self, 'Message', save_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            global ledlist
            result = upload_new_ledlist(ledlist)
            self.statusBar().showMessage(result)
        else:
            pass

    # set the GUI to display in the center of the screen
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class checkWindow(QMainWindow):
    def __init__(self):
        super(checkWindow, self).__init__()
        self.initUI()
    def initUI(self):

        # basic settings
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid) 
        self.statusBar()
        self.statusBar().showMessage( 'Ready' )

        # buttons basic settsing
        quitButton = QtGui.QPushButton('&Quit')
        self.connect(quitButton, SIGNAL('clicked()'),self.close)

        startButton = QtGui.QPushButton('&Start')
        self.connect(startButton, SIGNAL('clicked()'),self.start_check)

        detailButton = QPushButton('&Detail information', self)
        self.connect(detailButton, SIGNAL('clicked()'), self.detail_window)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)        
        grid.addWidget(startButton, 1, 0)
        grid.addWidget(detailButton, 2, 0)
        grid.addWidget(quitButton, 3, 0)

        wid.setLayout(grid)
        self.center()
        self.setWindowTitle('Check')

    def detail_window(self):
        self.detail_error_info = error_info()
        self.detail_error_info.show()

    def start_check(self):
        print('start_check')
        global error_list 
        error_list = []
        GPIO_start()
        smf_len = get_smf_len()
        ledlist = get_st_ledlist()
        if (smf_len == len(ledlist)):
            for i in range(0, smf_len):
                text4show = 'pattern {pattern_num} is processing...'
                text4show = text4show.format(pattern_num = i+1)
                self.statusBar().showMessage(text4show)
                self.statusBar().showMessage(text4show)
                pos, pointNum = look(i, 2)
                lost = find_difference(ledlist[i], pos)
                new = find_difference(pos, ledlist[i])
                if((lost != []) or (new != [])):
                    error_list.append([i, lost, new])
             # error analsy
            if (error_list == []):
                self.statusBar().showMessage("Qualified")
            else:
                self.statusBar().showMessage("Unqualified, click detail for more information")
        else:
            self.statusBar().showMessage('length of ledlist dont match the length of patteens!!! please check them!')
        GPIO_clean()
        print(error_list)

    # set the GUI to display in the center of the screen
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class error_info(QWidget):
    def __init__(self):
        super(error_info, self).__init__()
        self.initUI()
    def initUI(self):
        self.refer = 0

        nextButton = QtGui.QPushButton('Next pattern', self)
        self.connect(nextButton, SIGNAL('clicked()'),self.next_frame)

        prevButton = QPushButton('Previous pattern', self)
        self.connect(prevButton, SIGNAL('clicked()'), self.prev_frame)

        # settings of the QLabel
        global lbl_cali
        lbl_cali = QLabel(self)


        global lbl_check
        lbl_check = QLabel(self)

        # setting of the grid layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(lbl_cali, 1, 1)
        grid.addWidget(lbl_check, 1, 2)
        grid.addWidget(nextButton, 2, 1)
        grid.addWidget(prevButton, 2, 2)               

        self.setLayout(grid)
        self.center()
        self.setWindowTitle('Detail error information')
        self.refresh()

    def next_frame(self):
        self.refer  = (self.refer+1)%(len(error_list))
        self.refresh()
    def prev_frame(self):
        self.refer  = (self.refer-1)%(len(error_list))
        self.refresh()
    def refresh(self):
        # make some copies
        smf_num = error_list[self.refer][0]
        get_frame(smf_num, 1)
        im = Image.open('/tmp/frame.png')
        im.save('/tmp/cali_frame.png', 'PNG')
        get_frame(smf_num, 2)
        im = Image.open('/tmp/frame.png')
        im.save('/tmp/check_frame.png', 'PNG')
        # reload
        global lbl_cali
        global lbl_check
        lbl_cali.setPixmap(QtGui.QPixmap('/tmp/cali_frame.png'))
        lbl_check.setPixmap(QtGui.QPixmap('/tmp/check_frame.png'))
        self.update()
    # set the GUI to display in the center of the screen
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class cali_info(QWidget):
    def __init__(self):
        super(cali_info, self).__init__()
        self.initUI()
    def initUI(self):
        self.refer = 0
        self.smf_len = get_smf_len()
        nextButton = QtGui.QPushButton('Next pattern', self)
        self.connect(nextButton, SIGNAL('clicked()'),self.next_frame)

        prevButton = QPushButton('Previous pattern', self)
        self.connect(prevButton, SIGNAL('clicked()'), self.prev_frame)

        # settings of the QLabel
        global lbl
        lbl = QLabel(self)

        # setting of the grid layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(lbl, 1, 0, 2, 2)
        grid.addWidget(nextButton, 3, 0)
        grid.addWidget(prevButton, 3, 1)               

        self.setLayout(grid)
        self.center()
        self.setWindowTitle('Detail calibration information')
        self.refresh()

    def next_frame(self):
        self.refer  = (self.refer+1)%(self.smf_len)
        self.refresh()
    def prev_frame(self):
        self.refer  = (self.refer-1)%(self.smf_len)
        self.refresh()
    def refresh(self):
        # make some copies
        smf_num = self.refer
        get_frame(smf_num, 1)
        # reload
        global lbl
        lbl.setPixmap(QtGui.QPixmap('/tmp/frame.png'))
        self.update()
    # set the GUI to display in the center of the screen
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
def main():
    # show the GUI
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
