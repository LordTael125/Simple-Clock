from PyQt6.QtCore import Qt
try:
    print("Qt.Edge attributes:")
    for d in dir(Qt.Edge):
        print(d)
except AttributeError:
    print("Qt.Edge not found")

try:
    print("\nQt attributes starting with Bottom:")
    for d in dir(Qt):
        if d.startswith("Bottom"):
            print(d)
except:
    pass
