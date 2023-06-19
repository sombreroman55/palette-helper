from collections import Counter
import os
import math
import sys
from PIL import Image
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import \
    QApplication, QMainWindow, QWidget, QLabel, QTabWidget, \
    QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, QGridLayout, \
    QSlider


def col2hex(ct):
    return '#{:02x}{:02x}{:02x}'.format(*ct)


def colorDistance(color1, color2):
    # Discard alpha channel
    r1, g1, b1, _ = color1
    r2, g2, b2, _ = color2
    return math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)


class ColorSquare(QLabel):
    def __init__(self, rgba_hex):
        super().__init__()
        self.rgba = col2hex(rgba_hex)
        self.negative = col2hex(
                tuple(~component & 0xFF for component in rgba_hex))
        self.timer = QTimer()
        self.is_copying = False
        self.defineStyles()
        self.initUI()

    def defineStyles(self):
        common = f"background-color: {self.rgba}; color: {self.negative};"
        self.styles = {
            "normal": common,
            "hover": common + f" border: 2px solid {self.negative};",
            "copying": "background-color: green; color: white;",
        }

    def initUI(self):
        self.setMouseTracking(True)
        self.setText(f"{self.rgba}")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self.styles["normal"])

    def enterEvent(self, event):
        if not self.is_copying:
            self.setStyleSheet(self.styles["hover"])

    def leaveEvent(self, event):
        if not self.is_copying:
            self.setStyleSheet(self.styles["normal"])

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text())
            self.showCopied()
            event.accept()

    def showCopied(self):
        self.is_copying = True
        self.setText("Copied!")
        self.setStyleSheet(self.styles["copying"])
        self.timer.stop()
        self.timer.setInterval(400)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.restore)
        self.timer.start()

    def restore(self):
        self.is_copying = False
        self.setText(f"{self.rgba}")
        self.setStyleSheet(self.styles["normal"])


class PaletteParameters(QWidget):
    distance_changed = pyqtSignal(int)
    colors_changed = pyqtSignal(int)

    def __init__(self, image):
        super().__init__()
        self.image_path = image
        self.num_colors = 16
        self.min_distance = 25
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.color_label = QLabel(f"Colors: {self.num_colors}")
        self.color_slider = QSlider(Qt.Orientation.Horizontal)
        self.color_slider.setRange(1, 36)
        self.color_slider.setValue(self.num_colors)
        self.color_slider.valueChanged.connect(self.colorSliderChanged)

        self.distance_label = QLabel(f"Min distance: {self.min_distance}")
        self.distance_slider = QSlider(Qt.Orientation.Horizontal)
        self.distance_slider.setRange(0, 40)
        self.distance_slider.setValue(self.min_distance)
        self.distance_slider.valueChanged.connect(self.distanceSliderChanged)

        self.image_label = QLabel("Original image:")
        self.original_image = QLabel()
        pixmap = QPixmap(self.image_path)

        self.original_image.setPixmap(
                pixmap.scaled(
                    self.original_image.size(),
                    Qt.AspectRatioMode.KeepAspectRatio))

        layout.addWidget(self.color_label)
        layout.addWidget(self.color_slider)
        layout.addWidget(self.distance_label)
        layout.addWidget(self.distance_slider)
        layout.addWidget(self.image_label)
        layout.addWidget(self.original_image)

        layout.setStretchFactor(self.color_label, 1)
        layout.setStretchFactor(self.color_slider, 1)
        layout.setStretchFactor(self.distance_label, 1)
        layout.setStretchFactor(self.distance_slider, 1)
        layout.setStretchFactor(self.image_label, 1)
        layout.setStretchFactor(self.original_image, 5)

        self.setLayout(layout)

    def colorSliderChanged(self, value):
        self.color_label.setText(f"Colors: {value}")
        self.colors_changed.emit(value)

    def distanceSliderChanged(self, value):
        self.distance_label.setText(f"Min distance: {value}")
        self.distance_changed.emit(value)


class PaletteTabView(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.min_distance = 25
        self.num_colors = 16
        self.alpha_cutoff = 200
        self.colors = {}
        self.precalculateColors()
        self.initUI()

    # PERF: This is slow
    def precalculateColors(self):
        image = Image.open(self.image_path)
        image = image.convert('RGBA')
        colors = list(image.getdata())
        color_count = Counter(colors)
        sorted_colors = color_count.most_common()
        for i in range(1, 37):
            for j in range(0, 41):
                most_frequent_colors = []
                selected_colors = []

                for color, _ in sorted_colors:
                    # Ignore overly transparent colors
                    if color[3] <= self.alpha_cutoff:
                        continue
                    is_similar = False
                    for selected in selected_colors:
                        if colorDistance(color, selected) <= j:
                            is_similar = True
                            break

                    if not is_similar:
                        most_frequent_colors.append(color)
                        selected_colors.append(color)

                    if len(most_frequent_colors) == i:
                        break

                self.colors[(i, j)] = most_frequent_colors

    def updateMinDistance(self, distance):
        self.min_distance = distance
        self.updateGrid()

    def updateNumColors(self, colors):
        self.num_colors = colors
        self.updateGrid()

    def initUI(self):
        layout = QHBoxLayout()
        self.parameters = PaletteParameters(self.image_path)
        self.grid_view = QWidget()
        grid_layout = QGridLayout()
        self.grid_view.setLayout(grid_layout)

        layout.addWidget(self.parameters)
        layout.addWidget(self.grid_view)
        layout.setStretchFactor(self.parameters, 1)
        layout.setStretchFactor(self.grid_view, 5)

        self.parameters.colors_changed.connect(self.updateNumColors)
        self.parameters.distance_changed.connect(self.updateMinDistance)
        self.updateGrid()
        self.setLayout(layout)

    def updateGrid(self):
        layout = self.grid_view.layout()
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)
        colors = self.colors[(self.num_colors, self.min_distance)]
        rows = math.ceil(math.sqrt(self.num_colors))
        for i, color in enumerate(colors):
            square = ColorSquare(color[:3])
            layout.addWidget(square, i // rows, i % rows)


class PaletteTabs(QTabWidget):
    def __init__(self):
        super().__init__()
        self.images = set()
        self.open_tabs = set()
        self.initUI()

    def initUI(self):
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)

    def closeTab(self, index):
        widget = self.widget(index)
        self.removeTab(index)
        widget.deleteLater()

    def addImages(self, images):
        # N^2 but who cares
        for image in images:
            already_here = False
            for tab in range(self.count()):
                widget = self.widget(tab)
                if image == widget.image_path:
                    already_here = True
                    break

            if not already_here:
                newTabView = PaletteTabView(image)
                self.addTab(newTabView, os.path.basename(image))


class PaletteAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Palette Analyzer')
        self.setGeometry(100, 100, 1280, 720)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.file_button = QPushButton("Open Files")
        self.file_button.clicked.connect(self.selectFiles)
        self.tabs = PaletteTabs()
        layout.addWidget(self.file_button)
        layout.addWidget(self.tabs)
        layout.setStretchFactor(self.file_button, 1)
        layout.setStretchFactor(self.tabs, 8)
        self.show()

    def selectFiles(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            self.tabs.addImages(selected_files)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    analyzer = PaletteAnalyzer()
    sys.exit(app.exec())
