import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QSpacerItem, QPushButton, QLabel, QFileDialog, QCheckBox, \
    QVBoxLayout, \
    QHBoxLayout, QMessageBox, QLineEdit, QListWidget, QListWidgetItem, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore


class window(QWidget):
    def __init__(self, title):
        super().__init__()
        self.initUI(title)

    def initUI(self, title):
        # viarables
        self.setWindowTitle(title)
        self.pic_list = []
        self.index = 0
        self.pic = QLabel(self)
        self.pic.setMinimumSize(400, 400)
        self.pic.setText("No Pics.")
        self.pic.setAlignment(QtCore.Qt.AlignCenter)
        self.label_dict = {}  # save label info in a dictionary
        self.class_list = []  # save total class(str)
        self.save_url = None

        # left part layout
        file_choose_btn = QPushButton(self)
        file_choose_btn.setStyleSheet("QPushButton{border-image:url(icons/open_folder.png)}"
                                      "QPushButton:hover{border-image:url(icons/open_folder_hover.png)}")
        file_choose_btn.setToolTip("Open a directory")
        file_choose_btn.setMinimumSize(40, 40)
        file_choose_btn.clicked.connect(self.chooseOpenPath)
        file_choose_btn.setMaximumSize(100, 100)

        save_path_btn = QPushButton(self)  # default: label.json
        save_path_btn.setStyleSheet("QPushButton{border-image:url(icons/save_path.png)}"
                                    "QPushButton:hover{border-image:url(icons/save_path_hover.png)}")
        save_path_btn.setToolTip("Choose a save path")
        save_path_btn.setMinimumSize(35, 35)
        save_path_btn.clicked.connect(self.chooseSavePath)
        save_path_btn.setMaximumSize(100, 100)

        left_part = QVBoxLayout()
        left_part.addWidget(file_choose_btn)
        left_part.addWidget(save_path_btn)

        spacer = QSpacerItem(20, 20, QSizePolicy.Maximum, QSizePolicy.Expanding)
        left_part.addSpacerItem(spacer)

        # down part layout
        prev_btn = QPushButton(self)
        prev_btn.setStyleSheet("QPushButton{border-image:url(icons/prev.png)}"
                               "QPushButton:hover{border-image:url(icons/prev_hover.png)}")
        prev_btn.setFixedSize(60, 60)
        prev_btn.clicked.connect(self.showPrev)

        next_btn = QPushButton(self)
        next_btn.setStyleSheet("QPushButton{border-image:url(icons/next.png)}"
                               "QPushButton:hover{border-image:url(icons/next_hover.png)}")
        next_btn.setFixedSize(60, 60)
        next_btn.clicked.connect(self.showNext)

        down_part = QHBoxLayout()
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        down_part.addSpacerItem(spacer)
        down_part.addWidget(prev_btn)
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        down_part.addSpacerItem(spacer)
        down_part.addWidget(next_btn)
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        down_part.addSpacerItem(spacer)

        # center part layout
        center_part = QVBoxLayout()
        center_part.addWidget(self.pic)
        center_part.addLayout(down_part)

        # right part layout
        # # right down part
        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.save_file)

        self.auto_save_box = QCheckBox("Auto save", self)

        right_down_part = QVBoxLayout()
        right_down_part.addWidget(save_btn)
        right_down_part.addWidget(self.auto_save_box)

        # # right top part
        right_top_part = QVBoxLayout()

        # # # label layout part
        self.label_zone = QListWidget()
        self.label_zone.setMaximumWidth(300)
        self.checkbox_list = []
        self.loadClassFile() # load default

        right_top_part.addWidget(self.label_zone)
        # # # add label button
        add_class_btn = QPushButton("+ Add Class", self)
        add_class_btn.clicked.connect(self.inputClass)
        right_top_part.addWidget(add_class_btn)

        load_class_file_btn = QPushButton("Load file", self)
        load_class_file_btn.clicked.connect(self.chooseClassFile)
        right_top_part.addWidget(load_class_file_btn)

        right_part = QVBoxLayout()
        right_part.addLayout(right_top_part)
        right_part.addLayout(right_down_part)

        # total layout
        window_layout = QHBoxLayout()
        window_layout.addLayout(left_part)
        window_layout.addLayout(center_part)
        window_layout.addLayout(right_part)

        self.setLayout(window_layout)

        self.inputWindow = inputBox()

        self.inputWindow._signal.connect(self.addNewClass)

        self.show()

    def chooseOpenPath(self):
        self.open_dir = QFileDialog.getExistingDirectory(self, "Choose Picture Directory")
        if self.open_dir == '':
            return
        self.save_url = os.path.join(self.open_dir, "label.json")  # default
        self.pic_list = []
        dict_path = os.path.join(self.open_dir, "label.json")
        if os.path.exists(dict_path):
            self.label_dict = json.load(open(dict_path))
        else:
            self.label_dict = {}
        for filename in os.listdir(self.open_dir):
            if filename.lower().endswith(
                    ('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
                self.pic_list.append(filename)
        # print(self.pic_list)
        self.index = 0  # 表示show第1张图片
        self.showPics()

    def chooseSavePath(self):
        self.save_url, file_type = QFileDialog.getSaveFileName(self, "Save your label file", "./label.json")
        if self.save_url == '':
            return
        # read infos in already saved file
        if not os.path.exists(self.save_url):
            self.label_dict = {}
        else:
            self.label_dict = json.load(open(self.save_url, "w"))

    def chooseClassFile(self):
        filename, file_type= QFileDialog.getOpenFileName(self, "Choose your class file", "./", "json files(*.txt)")
        if filename != '':
            self.loadClassFile(filename)

    def loadClassFile(self, filename="default.txt"):
        print(filename)
        try:
            with open(filename, "r") as f:
                self.label_zone.clear()
                lines = f.readlines()
                for line in lines:
                    line = line.strip("\n")
                    label_checkbox = QCheckBox(line, self)
                    item = QListWidgetItem()
                    self.label_zone.addItem(item)
                    self.label_zone.setItemWidget(item, label_checkbox)
                    self.class_list.append(line)
                    self.checkbox_list.append(label_checkbox)
        except:
            QMessageBox.warning(self, "Warning", "Unable to open class file!")

    def showPics(self):
        current_file = self.pic_list[self.index]
        # reset pic
        img = QPixmap(os.path.join(self.open_dir, current_file)).scaled(self.pic.width(),
                                                                        self.pic.height())
        self.pic.setPixmap(img)
        self.pic.repaint()
        # set label from the dictionary file
        print(current_file, self.label_dict)
        for checkbox in self.checkbox_list:
            try:
                if checkbox.text() in self.label_dict[current_file]:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
            except:
                checkbox.setChecked(False)
            checkbox.repaint()

    def showPrev(self):
        if self.index <= 0:
            return
        else:
            self.index = self.index - 1
            self.showPics()
            if self.pic_list[self.index] not in self.label_dict.keys():
                self.cur_label_list = []
            else:
                self.cur_label_list = self.label_dict[self.pic_list[self.index]]
            self.changeLabel()  # change label tags

    def showNext(self):
        # check if auto save
        if self.auto_save_box.isChecked():
            self.save_file()
            if self.index >= len(self.pic_list) - 1:
                return
            else:
                self.index = self.index + 1
                self.showPics()
        else:
            reply = QMessageBox.question(self, "Warning",
                                         "You haven't save the file, would you like to go next anyway?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.index >= len(self.pic_list) - 1:
                    return
                else:
                    self.index = self.index + 1
                    self.showPics()

    def save_file(self):
        if len(self.pic_list):
            cur_label_list = []
            for checkBox in self.checkbox_list:
                if checkBox.isChecked():
                    cur_label_list.append(checkBox.text())
            current_file = self.pic_list[self.index]
            self.label_dict[current_file] = cur_label_list
        if not self.save_url:
            QMessageBox.warning(self, "Warning", "Please open a directory and set your save path!")
        else:
            with open(self.save_url, "w") as f:
                json.dump(self.label_dict, f)

    def inputClass(self):  # to be finished
        self.inputWindow.class_list = self.class_list
        self.inputWindow.show()

    def addNewClass(self, data):
        checkbox = QCheckBox(data, self)
        item = QListWidgetItem()
        self.label_zone.addItem(item)
        self.label_zone.setItemWidget(item, checkbox)
        self.checkbox_list.append(checkbox)

    def changeLabel(self):
        for checkbox in self.checkbox_list:
            if checkbox.text() in self.cur_label_list:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
            checkbox.repaint()


class inputBox(QDialog):
    _signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.class_list = []

    def initUI(self):
        self.setWindowTitle("Input")
        top_layout = QHBoxLayout()
        label = QLabel("Please input class name: ", self)
        self.input = QLineEdit()
        top_layout.addWidget(label)
        top_layout.addWidget(self.input)

        cancel_btn = QPushButton("Cancel", self)
        ok_btn = QPushButton("Ok", self)
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        bottom_layout = QHBoxLayout()
        bottom_layout.addSpacerItem(spacer)
        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addWidget(ok_btn)

        ok_btn.clicked.connect(self.getClassName)
        cancel_btn.clicked.connect(self.onClickCancel)

        window_layout = QVBoxLayout()
        window_layout.addLayout(top_layout)
        window_layout.addLayout(bottom_layout)
        self.setLayout(window_layout)

    def getClassName(self):
        data = self.input.text()
        if data == "":
            QMessageBox.warning(self, "Warning", "Class name can't be empty!")
        elif data in self.class_list:
            QMessageBox.warning(self, "Warning", "Class already exists!")
        else:
            self._signal.emit(data)
            self.close()

    def onClickCancel(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = window('Label Class')
    sys.exit(app.exec_())
