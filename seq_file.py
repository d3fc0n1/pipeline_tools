import sys
import re
import os
from PySide import QtGui

listview_items = []
print_list = []

class SeqFile(QtGui.QWidget):

    def get_collapsed_names(self, path):

        file_list = os.listdir(path)
        file_parms = {}
        collapsed_names = []

        for index, file in enumerate(file_list):

            full_name, extension = os.path.splitext(file)
            name, frame = os.path.splitext(full_name)
            if file_parms.has_key(name + extension):
                file_parms[name + extension].append(frame[1:].encode('UTF8'))
            else:
                file_parms[name + extension] = [frame[1:].encode('UTF8'), ]

        for name, frames in file_parms.items():
            if len(frames) == 1:
                collapsed_names.append(name)  # single file, add key to list directly
            else:
                if int(frames[-1]) - int(frames[0]) == len(frames) - 1:
                    frame_digits = len(frames[0])  # length of frame number string
                    if frames[0][0] == '0':
                        frame_string = '%0' + str(frame_digits) + 'd'
                    else:
                        frame_string = '%00d'
                    file_name, extension = os.path.splitext(name)
                    collapsed_names.append(
                        file_name + '.' + frame_string + extension + ' ' + str(int(frames[0])) + '-' + str(
                            int(frames[-1])))
                else:
                    # broken sequence - find indices of breaks and proceed
                    frame_limits = self.get_frame_limits(sorted(frames))
                    for limit in frame_limits:
                        file_name, extension = os.path.splitext(name)
                        if limit[0] == limit[1]:
                            collapsed_names.append(file_name + '.' + limit[0] + extension)
                        else:
                            collapsed_names.append(file_name + '.%0' + str(len(limit[0])) + 'd' + extension + ' ' + str(
                                int(limit[0])) + '-' + str(int(limit[1])))

                collapsed_names.sort()
        return collapsed_names

    def get_frame_limits(self, broken_sequence):
        start_index = 0
        frames = []

        for end_index in range(1, len(broken_sequence)):
            start = broken_sequence[start_index]
            end = broken_sequence[end_index]

            if int(start) + (end_index - start_index) != int(end):
                end = broken_sequence[end_index - 1]
                start_index = end_index

            if len(frames) == 0 or frames[-1:][0][0] != start:
                frames.append([start, end])
            else:
                frames[-1:] = [[start, end]]

        return frames

    def build_full_names(self, collapsed_files):

        original_names = []

        for index, file in enumerate(collapsed_files):
            if ' ' in file:  # has sequence numbers

                full_name, frames = file.split(' ')
                name_padding, extension = os.path.splitext(full_name)

                name, padding = os.path.splitext(name_padding)
                start = int(frames.split('-')[0].encode('UTF8'))
                end = int(frames.split('-')[1].encode('UTF8'))

                padding_count = re.search('%0(.*)d',  padding).group(1)

                for i in range(start, end + 1):
                    if len(str(i)) < padding_count:
                        padding = ('0' * (int(padding_count) - len(str(i)))) + str(i)
                    original_names.append(name + '.' + padding + extension)

                collapsed_files.pop(index)

                for i, name in enumerate(original_names):
                    collapsed_files.insert(index + i, name)

                del original_names[:]

        text = ', '.join(collapsed_files)
        return text

    def on_folder_button_clicked(self):
        global listview_items
        path = QtGui.QFileDialog.getExistingDirectory(caption='Select Folder', dir='/')
        listview_items = self.get_collapsed_names(path)
        for item in listview_items:
            self.list_widget.addItem(item)

    def on_show_button_clicked(self):
        msgBox = QtGui.QMessageBox()
        text = self.build_full_names(print_list)
        msgBox.setText(text)
        msgBox.exec_()

    def init_UI(self):
        self.setGeometry(300, 300, 400, 200)
        folder_button = QtGui.QPushButton('Select Folder', self)
        folder_button.clicked.connect(self.on_folder_button_clicked)
        show_button = QtGui.QPushButton('Show Files', self)
        show_button.move(0, 30)
        show_button.clicked.connect(self.on_show_button_clicked)
        self.show()

    def __init__(self):
        super(SeqFile, self).__init__()
        self.list_widget = QtGui.QListWidget(self)
        self.list_widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.list_widget.move(130, 0)
        self.list_widget.itemSelectionChanged.connect(self.on_list_selection_change)
        self.init_UI()

    def on_list_selection_change(self):
        global print_list
        del print_list[:]
        for item in self.list_widget.selectedItems():
            print_list.append(item.text())

def main():
    app = QtGui.QApplication(sys.argv)
    sf = SeqFile()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
