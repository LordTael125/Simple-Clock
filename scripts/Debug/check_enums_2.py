from PyQt5.QtCore import Qt
try:
    print(Qt.MouseButton.LeftButton)
except AttributeError:
    print("Qt.MouseButton not found")

try:
    print(Qt.LeftButton)
    print("Qt.LeftButton found")
except AttributeError:
    print("Qt.LeftButton not found")
