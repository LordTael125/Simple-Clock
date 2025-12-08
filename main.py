import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.clock_widget import ClockWidget, resource_path

def main():
    app = QApplication(sys.argv)
    
    # Set Application Icon (Important for Taskbar/Panel on Linux)
    icon_path = resource_path("icon.png")
    app.setWindowIcon(QIcon(icon_path))
    
    window = ClockWidget()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
