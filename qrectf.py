from PySide6.QtCore import QRectF, QPointF

# Creating a QRectF
rect = QRectF(10.5, 20.5, 100.0, 50.0)  # (x, y, width, height)

# Accessing properties
print("X:", rect.x())       # X coordinate of the top-left corner
print("Y:", rect.y())       # Y coordinate of the top-left corner
print("Width:", rect.width())   # Width of the rectangle
print("Height:", rect.height())  # Height of the rectangle

# Moving the rectangle
rect.moveTopLeft(QPointF(50.0, 60.0))  # Move the top-left corner to (50, 60)

# Resizing the rectangle
rect.setWidth(150.0)
rect.setHeight(75.0)

# Checking containment
point = QPointF(80.0, 70.0)
if rect.contains(point):
    print("Point is inside the rectangle")
else:
    print("Point is outside the rectangle")
