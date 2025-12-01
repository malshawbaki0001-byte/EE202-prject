"""
================================================================================
ملف الأنماط والدوال المساعدة - Styles Module (styles.py)
================================================================================

الهدف من الملف:
    هذا الملف يحتوي على جميع الأنماط (CSS Styles) والدوال المساعدة
    المستخدمة في واجهات التطبيق. يوفر مظهر موحد ومتناسق للتطبيق.

البنية العامة للملف:
    ============================================================================
    1. LIGHT_MODE_QSS (أنماط الوضع الفاتح)
    ============================================================================
    - أنماط CSS للوضع الفاتح (النهاري)
    - يحتوي على تنسيقات لجميع العناصر:
        * QDialog, QWidget, QMainWindow: الخلفية والخطوط
        * QFrame, QLabel: البطاقات والعناوين
        * QLineEdit, QComboBox: حقول الإدخال
        * QPushButton: الأزرار بأنواعها (عادي، ثانوي، خطر)
        * QTableWidget: الجداول
        * QListWidget: القوائم
        * QStatusBar: شريط الحالة
        * QPushButton[class="theme_button"]: زر تبديل الثيم
    
    ============================================================================
    2. DARK_MODE_QSS (أنماط الوضع الداكن)
    ============================================================================
    - أنماط CSS للوضع الداكن (الليلي)
    - نفس العناصر لكن بألوان داكنة
    - ألوان مريحة للعين في الوضع الليلي
    
    ============================================================================
    3. apply_shadow() Function (دالة إضافة الظل)
    ============================================================================
    - دالة مساعدة لإضافة تأثير الظل على العناصر
    - يستخدم QGraphicsDropShadowEffect
    - يضيف عمق ووضوح للعناصر

العلاقات مع الملفات الأخرى:
    - يستورد: PyQt6.QtWidgets, PyQt6.QtGui
    - يستخدمه:
        * gui.py (LoginDialog, RegisterStudentDialog)
        * student.py (BaseDashboard, StudentDashboard)
        * admin.py (AdminDashboard)
    
التدفق العام:
    1. التطبيق يبدأ → تطبيق LIGHT_MODE_QSS افتراضياً
    2. المستخدم ينقر زر الثيم → تبديل بين LIGHT_MODE_QSS و DARK_MODE_QSS
    3. apply_shadow() يتم استدعاؤها عند إنشاء البطاقات (cards)
    
الألوان المستخدمة:
    الوضع الفاتح:
    - الخلفية: #f0f2f5
    - البطاقات: #ffffff
    - الأزرار الأساسية: #007bff
    - الأزرار الثانوية: #6c757d
    - الأزرار الخطيرة: #dc3545
    
    الوضع الداكن:
    - الخلفية: #2b2b2b
    - البطاقات: #3c3c3c
    - النصوص: #f0f0f0
    
مثال على الاستخدام:
    from styles import LIGHT_MODE_QSS, DARK_MODE_QSS, apply_shadow
    from PyQt6.QtWidgets import QWidget
    
    app = QApplication.instance()
    app.setStyleSheet(LIGHT_MODE_QSS)  # تطبيق الوضع الفاتح
    
    widget = QWidget()
    apply_shadow(widget)  # إضافة ظل للعنصر
"""

from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor


# ============================================================================
# STYLING
# ============================================================================

LIGHT_MODE_QSS = """
QDialog, QWidget, QMainWindow { background-color: #f0f2f5; font-family: "Arial", sans-serif; color: #333; }
QFrame[class="card"], QWidget[class="card"] { background-color: #ffffff; border-radius: 10px; }
QLabel { font-size: 14px; font-weight: bold; color: #333; }
QLabel#TitleLabel { font-size: 24px; font-weight: bold; color: #003366; }
QLineEdit, QComboBox {
    font-size: 14px; padding: 10px 15px; border: 1px solid #d0d0d0;
    border-radius: 5px; background-color: #fafafa; color: black;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #007bff; }
QPushButton {
    font-size: 14px; font-weight: bold; color: white;
    padding: 12px; border-radius: 5px; border: none; margin-top: 5px;
    background-color: #007bff; 
}
QPushButton:hover { background-color: #0056b3; }
QPushButton[class="secondary"] { background-color: #6c757d; }
QPushButton[class="secondary"]:hover { background-color: #5a6268; }
QPushButton[class="danger"] { background-color: #dc3545; }
QPushButton[class="danger"]:hover { background-color: #c82333; }
QTableWidget {
    background-color: #ffffff; border: 1px solid #d0d0d0;
    border-radius: 5px; font-size: 13px;
    selection-background-color: #007bff; selection-color: white;
}
QTableWidget#weekly_timetable {
    gridline-color: #d0d0d0;
    font-size: 11px;
}
QHeaderView::section {
    background-color: #f8f9fa; padding: 8px; border: none;
    border-bottom: 1px solid #d0d0d0; font-weight: bold;
}
QListWidget {
    background-color: #ffffff; border: 1px solid #d0d0d0;
    border-radius: 5px; font-size: 14px;
}
QListWidget::item { padding: 10px; }
QListWidget::item:selected { background-color: #007bff; color: white; }
QStatusBar { color: #333; font-weight: bold; }
QPushButton[class="theme_button"] {
    background-color: #e0e0e0; color: #333;
    font-size: 16px; font-weight: bold;
    min-width: 30px; max-width: 30px;
    min-height: 30px; max-height: 30px;
    border-radius: 15px;
}
"""

DARK_MODE_QSS = """
QDialog, QWidget, QMainWindow { background-color: #2b2b2b; font-family: "Arial", sans-serif; color: #f0f0f0; }
QFrame[class="card"], QWidget[class="card"] { background-color: #3c3c3c; border-radius: 10px; }
QLabel { font-size: 14px; font-weight: bold; color: #f0f0f0; }
QLabel#TitleLabel { font-size: 24px; font-weight: bold; color: #aaccff; }
QLineEdit, QComboBox {
    font-size: 14px; padding: 10px 15px; border: 1px solid #555;
    border-radius: 5px; background-color: #444; color: #f0f0f0;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #007bff; }
QPushButton {
    font-size: 14px; font-weight: bold; color: white;
    padding: 12px; border-radius: 5px; border: none; margin-top: 5px;
    background-color: #007bff;
}
QPushButton:hover { background-color: #0056b3; }
QPushButton[class="secondary"] { background-color: #6c757d; }
QPushButton[class="secondary"]:hover { background-color: #5a6268; }
QPushButton[class="danger"] { background-color: #dc3545; }
QPushButton[class="danger"]:hover { background-color: #c82333; }
QTableWidget {
    background-color: #3c3c3c; border: 1px solid #555;
    border-radius: 5px; font-size: 13px;
    selection-background-color: #007bff; selection-color: white;
}
QHeaderView::section {
    background-color: #444; padding: 8px; border: none;
    border-bottom: 1px solid #555; font-weight: bold; color: #f0f0f0;
}
QListWidget {
    background-color: #3c3c3c; border: 1px solid #555;
    border-radius: 5px; font-size: 14px;
}
QListWidget::item { padding: 10px; }
QListWidget::item:selected { background-color: #007bff; color: white; }
QStatusBar { color: #f0f0f0; font-weight: bold; }
QPushButton[class="theme_button"] {
    background-color: #555; color: #f0f0f0;
    font-size: 16px; font-weight: bold;
    min-width: 30px; max-width: 30px;
    min-height: 30px; max-height: 30px;
    border-radius: 15px;
}
"""


def apply_shadow(widget):
    """Apply shadow effect to widget."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setColor(QColor(0, 0, 0, 80))
    shadow.setOffset(0, 5)
    widget.setGraphicsEffect(shadow)

