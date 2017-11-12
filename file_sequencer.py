import sys
import os
import re
from PySide import QtGui

path = ''


class FileSequencer(QtGui.QWidget):
    def __init__(self):
        super(FileSequencer, self).__init__()
        self.list_widget = QtGui.QListWidget(self)
        self.list_widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.list_widget.move(130, 0)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 400, 200)
        folder_button = QtGui.QPushButton('Select Folder', self)
        folder_button.clicked.connect(self.on_folder_button_clicked)
        rename_button = QtGui.QPushButton('Rename', self)
        rename_button.move(0, 30)
        rename_button.clicked.connect(self.on_rename_clicked)
        self.show()

    def on_folder_button_clicked(self):
        global path
        self.list_widget.clear()
        path = QtGui.QFileDialog.getExistingDirectory(caption='Select Folder', dir='/')
        for frame_file in os.listdir(path):
            self.list_widget.addItem(frame_file)

    def on_rename_clicked(self):
        if self.list_widget.count() == 0:
            return

        global path
        msg_box = QtGui.QMessageBox()
        file_list = set()
        max_sequence_length = 0
        pattern = re.compile(r".*?([0-9]+)$")  # pattern to isolate numbers at end of file name

        for frame_file in os.listdir(path):
            file_name, ext = os.path.splitext(frame_file)  # unpack file name and extension
            match = re.match(pattern, file_name)  # find match for pattern

            try:
                sequence_length = len(match.groups()[0])  # get length of sequence number in file name
            except AttributeError:
                msg_box.setText('File "' + file_name + '" is not named as per convention.')
                msg_box.exec_()
                return

            file_list.add(file_name[:-sequence_length] + ext)  # unique 'name.extension's excluding sequence
            if max_sequence_length < sequence_length:
                max_sequence_length = sequence_length

        self.list_widget.clear()

        for item in file_list:
            name, ext = os.path.splitext(item)
            counter = 1

            for frame_file in sorted(os.listdir(path), key=sort_key):  # parse files in human-sorted order
                if frame_file.startswith(name) and frame_file.endswith(ext):
                    # 0-pad and standardize sequence length
                    new_name = name + str(counter).zfill(max_sequence_length) + ext
                    os.rename(path + '/' + frame_file, path + '/' + new_name)  # rename
                    self.list_widget.addItem(frame_file + ' --> ' + new_name)  # update list
                    counter += 1

        msg_box.setText('Renaming Complete.')
        msg_box.exec_()


def sort_key(name):
    return [check_digit(char) for char in re.split('([0-9]+)', name)]


def check_digit(char):
    try:
        return int(char)
    except ValueError:
        return char


def main():
    app = QtGui.QApplication(sys.argv)
    fs = FileSequencer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
