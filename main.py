import sys
from PyQt5.QtWidgets import QApplication
from src.clock_widget import ClockWidget

def main():
    app = QApplication(sys.argv)
    window = ClockWidget()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
