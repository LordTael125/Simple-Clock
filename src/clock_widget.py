import sys
from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtCore import QTimer, QTime, Qt, QPoint, QEvent
from PyQt5.QtGui import QPainter, QColor, QPolygon, QRegion, QIcon
import PyQt5.uic
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Load UI
        ui_path = resource_path(os.path.join("ui", "clock.ui"))
        PyQt5.uic.loadUi(ui_path, self)
        
        # Window Setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Timer for updating the clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # Update every second
        
        self.setWindowTitle("Analog Clock")
        
        # Set Window Icon
        icon_path = resource_path("icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        self.resize(400, 400)

    def resizeEvent(self, event):
        # Set mask to make the window circular
        side = min(self.width(), self.height())
        region = QPolygon()
        # Create a circular mask
        side = min(self.width(), self.height())
        region = QRegion(0, 0, side, side, QRegion.Ellipse)
        self.setMask(region)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if clicked on resize grip
            side = min(self.width(), self.height())
            center_x = self.width() / 2
            center_y = self.height() / 2
            radius = side / 2
            
            # Resize Grip (Bottom-Right, 45 deg)
            grip_dist = radius - 20
            grip_x = center_x + grip_dist * 0.7071
            grip_y = center_y + grip_dist * 0.7071
            
            # Close Button (Top-Right, -45 deg)
            # sin(-45) is -0.7071
            close_x = center_x + grip_dist * 0.7071
            close_y = center_y - grip_dist * 0.7071
            
            click_pos = event.pos()
            
            # Check resize grip
            dist_to_grip = ((click_pos.x() - grip_x)**2 + (click_pos.y() - grip_y)**2)**0.5
            if dist_to_grip < 15:
                 self.mode = 'RESIZE'
                 self.drag_pos = event.globalPos()
                 return

            # Check close button
            dist_to_close = ((click_pos.x() - close_x)**2 + (click_pos.y() - close_y)**2)**0.5
            if dist_to_close < 15:
                self.close()
                return

            # Otherwise move
            self.windowHandle().startSystemMove()
                
        elif event.button() == Qt.RightButton:
            menu = QMenu(self)
            close_action = menu.addAction("Close")
            action = menu.exec_(event.globalPos())
            if action == close_action:
                self.close()

    def changeEvent(self, event):
        if event.type() == QEvent.ActivationChange:
            self.update()
        super().changeEvent(event)

    def mouseMoveEvent(self, event):
        if getattr(self, 'mode', None) == 'RESIZE':
            global_pos = event.globalPos()
            delta = global_pos - self.drag_pos
            
            # Resize logic
            change = max(delta.x(), delta.y())
            
            new_size = max(100, self.width() + change)
            self.resize(new_size, new_size)
            self.drag_pos = global_pos

    def mouseReleaseEvent(self, event):
        self.mode = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Coordinate system setup
        side = min(self.width(), self.height())
        painter.setViewport((self.width() - side) // 2, (self.height() - side) // 2, side, side)
        painter.setWindow(0, 0, 200, 200) # Logical coordinates 200x200
        
        # Draw Clock Face
        self.draw_clock_face(painter)
        
        # Get current time
        time = QTime.currentTime()
        
        # Draw Digital Clock (7-Segment Style)
        self.draw_digital_clock(painter, time)
        
        # Draw Hands
        self.draw_hour_hand(painter, time)
        self.draw_minute_hand(painter, time)
        self.draw_second_hand(painter, time)
        
        # Draw Resize Grip (Bottom-Right)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(200, 200, 200, 150)) # Semi-transparent gray
        painter.drawEllipse(QPoint(164, 164), 5, 5) # Small dot
        
        # Draw Close Button (Top-Right)
        # Smaller, no X
        painter.setBrush(QColor(255, 50, 50, 200)) # Red
        painter.drawEllipse(QPoint(164, 36), 6, 6) # Radius 6 (Diameter 12)

    def draw_digital_clock(self, painter, time):
        # 7-Segment Display at Top Center
        h = time.hour()
        m = time.minute()
        # s = time.second() # Seconds removed
        
        # Format: HH:MM
        digits = [h // 10, h % 10, m // 10, m % 10]
        
        # Settings
        digit_width = 8
        digit_height = 14
        spacing = 4
        group_spacing = 6
        start_y = 45
        
        # Calculate total width to center it
        # 4 digits * width + 3 * spacing (some are group spacing)
        # Groups: HH : MM
        # Width: (2*w + s) + gs + (2*w + s)
        # = 4w + 2s + gs
        total_width = 4 * digit_width + 2 * spacing + 1 * group_spacing
        start_x = 100 - total_width / 2
        
        current_x = start_x
        
        painter.save()
        painter.setPen(Qt.NoPen)
        
        for i, digit in enumerate(digits):
            self.draw_seven_segment_digit(painter, current_x, start_y, digit_width, digit_height, digit)
            current_x += digit_width + spacing
            
            # Add extra spacing after hours (index 1)
            if i == 1:
                # Draw colon dots
                painter.setBrush(QColor(0, 255, 0, 200))
                painter.drawEllipse(QPoint(int(current_x - spacing/2 + group_spacing/2 - 1), int(start_y + digit_height/3)), 2, 2)
                painter.drawEllipse(QPoint(int(current_x - spacing/2 + group_spacing/2 - 1), int(start_y + 2*digit_height/3)), 2, 2)
                current_x += group_spacing
                
        painter.restore()

    def draw_seven_segment_digit(self, painter, x, y, w, h, num):
        # Segments:
        #   A
        # F   B
        #   G
        # E   C
        #   D
        
        # Segment definitions (relative to x, y, w, h)
        thickness = 2
        
        # Polygons for segments (simplified as rectangles for now, or small polygons)
        # Horizontal segments: A, G, D
        # Vertical segments: F, B, E, C
        
        segments = {
            'A': QPolygon([QPoint(int(x+1), int(y)), QPoint(int(x+w-1), int(y)), QPoint(int(x+w-2), int(y+thickness)), QPoint(int(x+2), int(y+thickness))]),
            'B': QPolygon([QPoint(int(x+w), int(y+1)), QPoint(int(x+w), int(y+h/2-1)), QPoint(int(x+w-thickness), int(y+h/2-2)), QPoint(int(x+w-thickness), int(y+2))]),
            'C': QPolygon([QPoint(int(x+w), int(y+h/2+1)), QPoint(int(x+w), int(y+h-1)), QPoint(int(x+w-thickness), int(y+h-2)), QPoint(int(x+w-thickness), int(y+h/2+2))]),
            'D': QPolygon([QPoint(int(x+1), int(y+h)), QPoint(int(x+w-1), int(y+h)), QPoint(int(x+w-2), int(y+h-thickness)), QPoint(int(x+2), int(y+h-thickness))]),
            'E': QPolygon([QPoint(int(x), int(y+h/2+1)), QPoint(int(x), int(y+h-1)), QPoint(int(x+thickness), int(y+h-2)), QPoint(int(x+thickness), int(y+h/2+2))]),
            'F': QPolygon([QPoint(int(x), int(y+1)), QPoint(int(x), int(y+h/2-1)), QPoint(int(x+thickness), int(y+h/2-2)), QPoint(int(x+thickness), int(y+2))]),
            'G': QPolygon([QPoint(int(x+2), int(y+h/2)), QPoint(int(x+w-2), int(y+h/2)), QPoint(int(x+w-3), int(y+h/2+1)), QPoint(int(x+3), int(y+h/2+1))]) # Thin line
        }
        
        # Map digits to segments
        # 0: A, B, C, D, E, F
        # 1: B, C
        # 2: A, B, G, E, D
        # 3: A, B, G, C, D
        # 4: F, G, B, C
        # 5: A, F, G, C, D
        # 6: A, F, E, D, C, G
        # 7: A, B, C
        # 8: All
        # 9: A, F, G, B, C, D
        
        map_digits = {
            0: ['A', 'B', 'C', 'D', 'E', 'F'],
            1: ['B', 'C'],
            2: ['A', 'B', 'D', 'E', 'G'],
            3: ['A', 'B', 'C', 'D', 'G'],
            4: ['B', 'C', 'F', 'G'],
            5: ['A', 'C', 'D', 'F', 'G'],
            6: ['A', 'C', 'D', 'E', 'F', 'G'],
            7: ['A', 'B', 'C'],
            8: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
            9: ['A', 'B', 'C', 'D', 'F', 'G']
        }
        
        active_segments = map_digits.get(num, [])
        
        # Draw background (dimmed) segments? User requested "classic bcd 7 segment display style"
        # Usually 7-segment has dim background segments.
        
        # Draw all segments dim
        painter.setBrush(QColor(50, 50, 50, 100))
        for seg_name, poly in segments.items():
            painter.drawConvexPolygon(poly)
            
        # Draw active segments bright
        painter.setBrush(QColor(0, 255, 0, 200)) # Green
        for seg_name in active_segments:
            painter.drawConvexPolygon(segments[seg_name])


    def draw_clock_face(self, painter):
        painter.save()
        painter.translate(100, 100)
        
        # Draw transparent/semi-transparent background if needed, 
        # but user asked for "transparent" app, usually meaning the window background.
        # We can draw a semi-transparent circle for the clock face so it's visible.
        
        # Dynamic Transparency
        if self.isActiveWindow():
            bg_color = QColor(0, 0, 0, 240) # Almost opaque when focused
        else:
            bg_color = QColor(0, 0, 0, 150) # Semi-transparent when unfocused
            
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(0, 0), 98, 98)
        
        # Draw Hour Marks
        painter.setPen(QColor(255, 255, 255))
        for i in range(12):
            painter.drawLine(0, -90, 0, -98)
            painter.rotate(30)
            
        painter.restore()

    def draw_hour_hand(self, painter, time):
        painter.save()
        painter.translate(100, 100)
        painter.rotate(30 * (time.hour() + time.minute() / 60))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawPolygon(QPolygon([QPoint(-3, 0), QPoint(0, -50), QPoint(3, 0)]))
        painter.restore()

    def draw_minute_hand(self, painter, time):
        painter.save()
        painter.translate(100, 100)
        painter.rotate(6 * (time.minute() + time.second() / 60))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(200, 200, 200))
        painter.drawPolygon(QPolygon([QPoint(-2, 0), QPoint(0, -70), QPoint(2, 0)]))
        painter.restore()

    def draw_second_hand(self, painter, time):
        painter.save()
        painter.translate(100, 100)
        
        # Rotate: 6 degrees per second
        angle = 6.0 * time.second()
        painter.rotate(angle - 90)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 0, 0))
        
        hand = QPolygon([QPoint(0, -1), QPoint(90, 0), QPoint(0, 1)])
        painter.drawConvexPolygon(hand)
        
        painter.restore()
