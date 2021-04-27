# version: 0.0.1
# data: 2021.04.26
# author: Roy Kid
# contact: lijichen365@126.com

import sys

from PySide6.QtGui import QAction, QImage, QPixmap
from paperSpider.backend import Backend
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QMenu
from PySide6.QtCore import QFile, QIODevice, Slot


class PaperSpider:

    def __init__(self) -> None:
        self.app, self.window = self.initUI("words.ui", "debug")
        self.set_interaction_logic()
        self.backend = Backend()

    def initUI(self, uiname, mode):
        # release mode
        # TODO: convert .ui to py code
        app = QApplication(sys.argv)

        # debug mode
        if mode == 'debug':
            ui_file_name = uiname
            ui_file = QFile(ui_file_name)
            if not ui_file.open(QIODevice.ReadOnly):
                print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
                sys.exit(-1)
            loader = QUiLoader()
            window = loader.load(ui_file)
            ui_file.close()
            if not window:
                print(loader.errorString())
                sys.exit(-1)
            window.show()

        return app, window

    def set_interaction_logic(self):
        self.window.addButton.clicked.connect(self._on_add_click)
        self.window.removeButton.clicked.connect(self._on_remove_click)
        # TODO: right click menu
        # https://blog.csdn.net/qq_39858109/article/details/108778860
        self.window.calcWordFreqButton.clicked.connect(self._on_calculate_word_freq)

    @Slot()
    def _on_add_click(self):

        # https://doc.qt.io/qtforpython/PySide6/QtWidgets/QFileDialog.html#PySide6.QtWidgets.PySide6.QtWidgets.QFileDialog.getOpenFileNames
        self.refPaths, selectedFilter = QFileDialog.getOpenFileNames(
            caption="Select one or more files to open", filter="PDF (*.pdf)", dir="Desktop")
        # add refname to the item container
        self.refNames = []
        for refPath in self.refPaths:

            # widgetres = []
            # # 获取listwidget中条目数
            # count = window.refList.count()
            # 遍历listwidget中的内容
            # for i in range(count):
            #     widgetres.append(self.listWidget.item(i).text())
            # print(widgetres)
            refName = refPath.split('/')[-1]
            if refName not in self.refNames:
                # https://doc.qt.io/qtforpython/PySide6/QtWidgets/QListWidget.html
                self.window.refListView.addItem(refName)
                self.refNames.append(refName)
            else:
                continue

        self.update()

    @Slot()
    def _on_remove_click(self):
        
        selecteds = self.window.refListView.selectedIndexes()
        
        for selected in selecteds:
            index = selected.row()
            self.window.refListView.takeItem(index)
            print(self.refNames)
            del self.refNames[index]
            del self.refPaths[index]
            print(self.refNames)
        self.update()

    @Slot()
    def _on_calculate_word_freq(self):
        # one reference
        # selected = self.window.refListView.currentIndex().row()
        # refPath = self.refPaths[selected]
        selecteds = self.window.refListView.selectedIndexes()
        selectedRefPaths = []
        for selected in selecteds:
            selectedRefPaths.append(self.refPaths[selected.row()])

        self.backend.update_refs(selectedRefPaths)
        wordCloudDraw = self.backend.drawWordCloud()

        # binary
        biWordCloudDraw = wordCloudDraw.to_array()


        x = biWordCloudDraw.shape[1]
        y = biWordCloudDraw.shape[0]
        channel = biWordCloudDraw.shape[2]
        frame = QImage(biWordCloudDraw, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pix)
        scene.addItem(item)

        self.window.wordCloudView.setScene(scene)
        
        def fit_view():
            self.window.wordCloudView.fitInView(item)

        def save_image():
            wordCloudDraw.to_file('wc.png')

        rezoom = QAction(self.window.wordCloudView)
        rezoom.setText('Rezoom')
        rezoom.triggered.connect(fit_view)

        save = QAction(self.window.wordCloudView)
        save.setText('Save')
        save.triggered.connect(save_image)

        self.window.wordCloudView.addAction(rezoom)
        self.window.wordCloudView.addAction(save)



        
    def update(self):
        self.window.refCountNum.setText(str(self.window.refListView.count()))


if __name__ == "__main__":

    mainWindow = PaperSpider()

    sys.exit(mainWindow.app.exec_())
