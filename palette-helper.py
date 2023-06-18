from PIL import Image
from collections import Counter
import os
import math
import sys
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import \
    QApplication, QMainWindow, QWidget, QLabel, QTabWidget, \
    QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, QGridLayout, \
    QSlider


class ColorSquare(QLabel):
    def __init__(self, rgba_hex):
        super().__init__()
        self.rgba = rgba_hex
        self.negative = tuple(~component & 0xFF for component in rgba_hex)
        self.timer = QTimer()
        self.isCopying = False
        self.initUI()

    def initUI(self):
        self.setMouseTracking(True)
        self.style = f"background-color : {self.col2hex(self.rgba)}; color : {self.col2hex(self.negative)};"
        self.hover_style = self.style + f"border: 2px solid {self.col2hex(self.negative)};"
        self.copied_style = self.style + "background-color: green; color: white;"
        self.setText(f"{self.col2hex(self.rgba)}")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self.style)

    def col2hex(self, colorTuple):
        return '#{:02x}{:02x}{:02x}'.format(*colorTuple)

    def enterEvent(self, event):
        if not self.isCopying:
            self.setStyleSheet(self.hover_style)

    def leaveEvent(self, event):
        if not self.isCopying:
            self.setStyleSheet(self.style)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text())
            self.showCopied()
            event.accept()

    def showCopied(self):
        self.isCopying = True
        self.setText("Copied!")
        self.setStyleSheet(self.copied_style)
        self.timer.stop()
        self.timer.setInterval(400)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.restoreWidget)
        self.timer.start()

    def restoreWidget(self):
        self.isCopying = False
        self.setText(f"{self.col2hex(self.rgba)}")
        self.setStyleSheet(self.style)


class PaletteTabs(QTabWidget):
    tabChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.images = None
        self.min_distance = 25
        self.num_colors = 16
        self.colors = []
        self.initUI()

    def initUI(self):
        self.currentChanged.connect(self.changeTab)

    def changeTab(self, index):
        imagePath = self.tabText(index)
        self.tabChanged.emit(imagePath)

    def addImages(self, images):
        self.images = images
        self.analyze()

    def updateMinDistance(self, distance):
        self.min_distance = distance
        self.analyze()

    def updateNumColors(self, colors):
        self.num_colors = colors
        self.analyze()

    def colorDistance(self, color1, color2):
        # Discard alpha channel
        r1, g1, b1, _ = color1
        r2, g2, b2, _ = color2
        return math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)

    def analyze(self):
        self.clear()
        for image in self.images:
            colors = self.getMostFrequentColors(image)
            newTab = QWidget()
            layout = QGridLayout()
            rows = math.ceil(math.sqrt(self.num_colors))
            for i, color in enumerate(colors):
                square = ColorSquare(color[0][:3])
                layout.addWidget(square, i // rows, i % rows)
            newTab.setLayout(layout)
            self.colors.append(colors)
            self.addTab(newTab, os.path.basename(image))

    def getMostFrequentColors(self, image):
        image = Image.open(image)
        image = image.convert('RGBA')
        pixels = list(image.getdata())
        color_count = Counter(pixels)
        sorted_colors = color_count.most_common()

        most_frequent_colors = []
        selected_colors = []

        for color, count in sorted_colors:
            if color[3] <= 200:
                continue
            is_similar = False
            for selected_color in selected_colors:
                if self.colorDistance(color, selected_color) <= self.min_distance:
                    is_similar = True
                    break

            if not is_similar:
                most_frequent_colors.append((color, count))
                selected_colors.append(color)

            if len(most_frequent_colors) == self.num_colors:
                break

        return most_frequent_colors


class PaletteParameters(QWidget):
    files_selected = pyqtSignal(list)
    distance_changed = pyqtSignal(int)
    colors_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.num_colors = 16
        self.min_distance = 25
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.file_button = QPushButton("Open Files")
        self.file_button.clicked.connect(self.selectFiles)

        self.color_label = QLabel(f"Colors: {self.num_colors}")
        self.color_slider = QSlider(Qt.Orientation.Horizontal)
        self.color_slider.setRange(1, 40)
        self.color_slider.setValue(self.num_colors)
        self.color_slider.valueChanged.connect(self.colorSliderChanged)

        self.distance_label = QLabel(f"Min distance: {self.min_distance}")
        self.distance_slider = QSlider(Qt.Orientation.Horizontal)
        self.distance_slider.setRange(0, 50)
        self.distance_slider.setValue(self.min_distance)
        self.distance_slider.valueChanged.connect(self.distanceSliderChanged)

        self.image_label = QLabel("Original image")
        self.original_image = QLabel()
        self.image_label.hide()
        self.original_image.hide()

        layout.addWidget(self.file_button)
        layout.addWidget(self.color_label)
        layout.addWidget(self.color_slider)
        layout.addWidget(self.distance_label)
        layout.addWidget(self.distance_slider)
        layout.addWidget(self.image_label)
        layout.addWidget(self.original_image)

        layout.setStretchFactor(self.file_button, 1)
        layout.setStretchFactor(self.color_label, 1)
        layout.setStretchFactor(self.color_slider, 1)
        layout.setStretchFactor(self.distance_label, 1)
        layout.setStretchFactor(self.distance_slider, 1)
        layout.setStretchFactor(self.image_label, 1)
        layout.setStretchFactor(self.original_image, 2)

        self.setLayout(layout)

    def colorSliderChanged(self, value):
        self.color_label.setText(f"Colors: {value}")
        self.colors_changed.emit(value)

    def distanceSliderChanged(self, value):
        self.distance_label.setText(f"Min distance: {value}")
        self.distance_changed.emit(value)

    def showOriginal(self, image_path):
        image = QPixmap(image_path)
        self.original_image.setPixmap(image)
        self.image_label.show()
        self.original_image.show()

    def selectFiles(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            self.files_selected.emit(selected_files)


class PaletteAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Palette Analyzer')
        self.setGeometry(100, 100, 1280, 720)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        self.parameters = PaletteParameters()
        self.tabs = PaletteTabs()
        layout.addWidget(self.parameters)
        layout.addWidget(self.tabs)

        layout.setStretchFactor(self.parameters, 1)
        layout.setStretchFactor(self.tabs, 3)
        self.parameters.files_selected.connect(self.tabs.addImages)
        self.parameters.colors_changed.connect(self.tabs.updateNumColors)
        self.parameters.distance_changed.connect(self.tabs.updateMinDistance)
        self.tabs.tabChanged.connect(self.parameters.showOriginal)
        self.show()

    # TODO: Add UI to assign colors to a scheme. Start with kitty themes
    #       Since they are an easy 16 color palette that  we can work with
    #       We can expand to more if we want to for emacs or vim or whatever


if __name__ == "__main__":
    app = QApplication(sys.argv)
    analyzer = PaletteAnalyzer()
    sys.exit(app.exec())
