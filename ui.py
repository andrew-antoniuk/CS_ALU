"""ui"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QFrame, QSplitter, QGraphicsScene, QGraphicsView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen, QBrush, QFont, QPainter

class ModernSidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(44)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2D2D35;
                color: #D1D5DB;
                border: none;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
                padding-left: 14px;
            }
            QPushButton:hover {
                background-color: #3F3F4C;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #1E1E24;
            }
        """)

class CircuitGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setBackgroundBrush(QColor("#18181C"))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 0.85
        self.scale(factor, factor)

class CircuitConstructorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конструктор логічних елементів (Симулятор)")
        self.resize(1024, 680)
        self.setStyleSheet("background-color: #0F0F12; color: #E0E0E0;")
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("background-color: #141418; border-right: 1px solid #1F1F24;")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 20)
        sidebar_layout.setSpacing(12)
        
        title_label = QLabel("Конструктор")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFFFFF; margin-bottom: 8px;")
        
        self.elements_list = QListWidget()
        self.elements_list.setStyleSheet("""
            QListWidget {
                background-color: #18181C;
                border: 1px solid #282830;
                border-radius: 6px;
                padding: 4px;
                color: #D1D5DB;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: #23232C;
                color: #FFFFFF;
            }
            QListWidget::item:selected {
                background-color: #343440;
                color: #FFFFFF;
                border: none;
            }
        """)
        self.elements_list.addItems([
            "Джерело напруги (0/1)",
            "Логічний елемент AND",
            "Логічний елемент OR",
            "Логічний елемент NOT",
            "Логічний елемент XOR",
            "Логічний елемент NAND",
            "Дріт (Провідник)"
        ])
        
        btn_add = ModernSidebarButton("Додати елемент")
        btn_run = ModernSidebarButton("Запустити симуляцію")
        btn_save = ModernSidebarButton("Зберегти схему")
        btn_alu = ModernSidebarButton("4-бітне ALU")
        
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addWidget(self.elements_list)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(btn_add)
        sidebar_layout.addWidget(btn_run)
        sidebar_layout.addWidget(btn_alu)
        sidebar_layout.addWidget(btn_save)
        sidebar_layout.addStretch()
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(12, 12, 12, 12)
        
        header_layout = QHBoxLayout()
        status_label = QLabel("Стан: Готовий до побудови | Режим: Створення")
        status_label.setStyleSheet("color: #6C6C7A; font-size: 11px;")
        
        badge = QLabel(" MEDIUM ")
        badge.setStyleSheet("""
            background-color: #10B981; 
            color: #FFFFFF; 
            border-radius: 4px; 
            padding: 2px 6px;
            font-weight: bold;
            font-size: 10px;
        """)
        
        header_layout.addWidget(status_label)
        header_layout.addStretch()
        header_layout.addWidget(badge)
        
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 2000, 1500)
        self.view = CircuitGraphicsView(self.scene)
        
        self.draw_grid()
        
        right_layout.addLayout(header_layout)
        right_layout.addWidget(self.view)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(right_widget)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def draw_grid(self):
        pen = QPen(QColor("#24242A"), 1, Qt.PenStyle.DotLine)
        grid_size = 30
        for x in range(0, int(self.scene.width()), grid_size):
            for y in range(0, int(self.scene.height()), grid_size):
                self.scene.addEllipse(x, y, 1, 1, pen, QBrush(QColor("#24242A")))