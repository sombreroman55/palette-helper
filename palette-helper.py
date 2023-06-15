from PIL import Image, ImageDraw
from collections import Counter
import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


class ColorSquare(QWidget):
    def __init__(self, rgba_hex):
        super().__init__()
        self.initUI()
        self.rgba = rgba_hex

    def initUI(self):
        pass


class PaletteTabs(QWidget):
    def __init__(self, rgba_hex):
        super().__init__()
        self.initUI()
        self.rgba = rgba_hex

    def initUI(self):
        pass


class PaletteAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    # TODO: Set up UI

    # +--------------------------------------------------+
    # | File picker   | | T1 | T2 | T3 | etc...          |
    # |               |                                  |
    # | Palette size  | T1 = palette                     |
    # |               | T2 = original image              |
    # | Min Distance  | T3 = color theme preview         |
    # |               |                                  |
    # | Colorsceheme  | The grid should show the squares |
    # | Setup stuff   | of the most used colors and have |
    # |               | the hex codes for those colors   |
    # |               | inside of them, and clicking on  |
    # |               | a square copies the color to the |
    # |               | clipboard.                       |
    # |               |                                  |
    # +--------------------------------------------------+
    def initUI(self):
        self.setWindowTitle('Palette Analyzer')
        self.setGeometry(300, 300, 300, 300)
        self.num_colors = 25
        self.max_distance = 400
        self.show()

    # TODO: Read in multiple files

    # TODO: Allow user to view palettes for individual files or for
    #       the batch as a whole

    # TODO: Add UI to assign colors to a scheme. Start with kitty themes
    #       Since they are an easy 16 color palette that  we can work with
    #       We can expand to more if we want to for emacs or vim or whatever

    # TODO: Create widget for color squares (hex color label and click-to copy)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    analyzer = PaletteAnalyzer()
    sys.exit(app.exec_())
