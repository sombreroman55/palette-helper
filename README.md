# palette-helper
A small Python utility to help extract a palette from images.

## Dependencies
palette-helper uses the following pip packages. You can install them yourself or use `pip install -r
requirements.txt` to have pip install them all at once. The `requirements.txt` file uses PyQt6, but
PyQt5 should also work.

- PyQt5/6
- Pillow

## Usage
The following screenshot shows the layout of palette-helper:

TODO

Use the button to open a file dialog to select the images you want to pull a palette from. You can
select multiple images of several different kinds. You can control the number of colors you want to
extract and the minimum "distance" they should be from each other on the side.

The main view is a tabbed view containing the extracted colors and the original image for each image
chosen, as well as a palette that is a composite of all the images if more than one was selected.

TODO Write more here

## Reporting Bugs
This is only meant to be small tool for me that I thought others might want to use, so I haven't
really planned to invest that much time into developing it. All the same, feel free to open an issue
if you find anything wrong that you'd like me to take a look at. The fact that you used this tool at
all is very flattering.
