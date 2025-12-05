from PyQt5.QtCore import Qt
try:
    print(Qt.WindowType.FramelessWindowHint)
except AttributeError:
    print("Qt.WindowType not found")

try:
    print(Qt.FramelessWindowHint)
    print("Qt.FramelessWindowHint found")
except AttributeError:
    print("Qt.FramelessWindowHint not found")
