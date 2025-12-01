"""
================================================================================
ملف الواجهة الرئيسية - GUI Module (gui.py)
================================================================================

الهدف من الملف:
    هذا الملف يحتوي على الواجهات الأساسية للنظام وهو نقطة الدخول الرئيسية
    للتطبيق. يحتوي على شاشة تسجيل الدخول والتحكم في تدفق التطبيق.

البنية العامة للملف:
    ============================================================================
    1. STYLING (التنسيقات)
    ============================================================================
    - LIGHT_MODE_QSS: أنماط الوضع الفاتح
    - DARK_MODE_QSS: أنماط الوضع الداكن
    - apply_shadow(): دالة لإضافة تأثير الظل
    
    ============================================================================
    2. LoginDialog Class (نافذة تسجيل الدخول)
    ============================================================================
    - نافذة تسجيل الدخول الرئيسية
    - يحتوي على:
        * حقول إدخال (المعرف، كلمة المرور)
        * زر تسجيل الدخول
        * زر إنشاء حساب طالب جديد
        * زر تبديل الثيم (الليلي/النهاري)
    
    ============================================================================
    3. RegisterStudentDialog Class (نافذة تسجيل طالب جديد)
    ============================================================================
    - نافذة لتسجيل طالب جديد
    - يحتوي على:
        * الاسم، البريد الإلكتروني، البرنامج، المستوى
        * التحقق من صحة البيانات
        * إنشاء معرف وكلمة مرور تلقائياً
    
    ============================================================================
    4. MainApp Class (التطبيق الرئيسي)
    ============================================================================
    - يرث من PyQt6.QApplication
    - نقطة الدخول الرئيسية للتطبيق
    - يدير دورة حياة التطبيق:
        1. عرض LoginDialog
        2. التحقق من المستخدم
        3. عرض Dashboard المناسب (StudentDashboard أو AdminDashboard)
        4. العودة لتسجيل الدخول بعد تسجيل الخروج

العلاقات مع الملفات الأخرى:
    - يستورد من:
        * registration_system.py (User, RegistrationSystem, UserManager, StudentManager)
        * student.py (StudentDashboard)
        * admin.py (AdminDashboard)
        * database.py (get_connection, add_student)
        * styles.py (apply_shadow, LIGHT_MODE_QSS, DARK_MODE_QSS)
        * PyQt6 (مكتبة الواجهات الرسومية)
    - يستخدمه:
        * المستخدم مباشرة (python gui.py)
    
التدفق العام للتطبيق:
    1. المستخدم يشغل التطبيق → MainApp.run()
    2. عرض LoginDialog (نافذة تسجيل الدخول)
    3. المستخدم يسجل دخول → UserManager.authenticate()
    4. حسب نوع المستخدم:
        - إذا كان طالب → عرض StudentDashboard
        - إذا كان مدير → عرض AdminDashboard
    5. المستخدم يسجل خروج → العودة لتسجيل الدخول
    
نظام الوراثة المستخدم:
    ✅ PyQt6.QApplication → MainApp
    ✅ PyQt6.QDialog → LoginDialog, RegisterStudentDialog
    
الملفات المرتبطة:
    - StudentDashboard موجود في student.py
    - AdminDashboard موجود في admin.py
    - جميع الأنماط موجودة في styles.py
    
مثال على الاستخدام:
    python gui.py  # تشغيل التطبيق
    
أو برمجياً:
    from gui import MainApp
    import sys
    app = MainApp_QApplication_gui(sys.argv)
    app.run()
"""

import sys
import random
import re
import time
import bcrypt
import smtplib
from email.message import EmailMessage

from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame,
    QMessageBox, QDialog, QLineEdit, QFormLayout,
    QComboBox
)
from PyQt6.QtCore import Qt, QRegularExpression, QTimer
from PyQt6.QtGui import QRegularExpressionValidator

# Import OOP core module
from registration_system import (
    User,
    RegistrationSystem_registration_system, UserManager_registration_system, StudentManager_registration_system
)

# Import database functions
from database import (
    get_connection, add_student
)

# Import styles and utilities
from styles import apply_shadow, LIGHT_MODE_QSS, DARK_MODE_QSS

# Import dashboard modules
from student import StudentDashboard_DashboardBase_student
from admin import AdminDashboard_DashboardBase_admin


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def login_user_database_passwordhasher(academic_id, email, password):
    """محاولة تسجيل الدخول من قاعدة بيانات SQLite.
    ترجع dict فيها (id, role, name, email, program, level) أو None إذا فشلت.
    يدعم كلا النوعين من التشفير: bcrypt و SHA-256 (PasswordHasher).
    """
    from registration_system import PasswordHasher_registration_system
    
    conn = get_connection()
    cur = conn.cursor()
    # البحث بالمعرف أو البريد (مثل UserManager.authenticate)
    # يمكن البحث بالمعرف في حقل المعرف أو البريد، أو بالبريد في أي من الحقلين
    cur.execute(
        """
        SELECT u.student_id,
               u.role,
               u.password_hash,
               COALESCE(s.name, u.display_name),
               COALESCE(s.email, u.email),
               s.program,
               s.level
        FROM users u
        LEFT JOIN students s ON u.student_id = s.student_id
        WHERE (u.student_id = ? OR u.email = ? OR u.student_id = ? OR u.email = ?)
        """, (academic_id, academic_id, email, email)
    )
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
    
    user_id, role, stored_password_hash, name, db_email, program, level = row
    
    # التحقق من كلمة المرور - دعم كلا النوعين
    password_valid = False
    try:
        # محاولة التحقق باستخدام bcrypt (للكلمات القديمة)
        if stored_password_hash.startswith('$2b$') or stored_password_hash.startswith('$2a$'):
            password_valid = bcrypt.checkpw(password.encode(), stored_password_hash.encode())
        else:
            # استخدام PasswordHasher (SHA-256) للكلمات الجديدة
            password_hasher = PasswordHasher_registration_system()
            password_valid = password_hasher.verify_password(password, stored_password_hash)
    except Exception:
        return None
    
    if not password_valid:
        return None
    
    return {
        "id": user_id,
        "role": role,
        "name": name or "",
        "email": db_email or "",
        "program": program,
        "level": level,
    }


def user_identifier_exists(identifier):
    """التحقق من وجود معرف في قاعدة البيانات."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE student_id = ? OR email = ?", (identifier, identifier))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def generate_unique_identifier(prefix=""):
    """توليد معرف فريد."""
    while True:
        identifier = f"{prefix}{random.randint(100000, 999999)}"
        if not user_identifier_exists(identifier):
            return identifier


# ============================================================================
# FORGOT PASSWORD DIALOG
# ============================================================================

class ForgotPasswordDialog_QDialog_gui(QDialog):
    """نافذة استعادة كلمة المرور مع OTP."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("استعادة كلمة المرور")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.otp = None
        self.user_id = None
        self.email = None
        self.otp_expiry = None
        self.timer = QTimer(self)
        self.timer.setInterval(60000)  # 1 دقيقة
        self.timer.timeout.connect(self.allow_resend_otp)
        self.timer.setSingleShot(True)
        
        self.init_ui()
    
    def init_ui(self):
        """تهيئة واجهة المستخدم."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("المعرف")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("البريد الإلكتروني")
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("رمز OTP")
        self.otp_input.setEnabled(False)
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("كلمة مرور جديدة")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setEnabled(False)
        
        self.send_otp_btn = QPushButton("إرسال OTP")
        self.send_otp_btn.clicked.connect(self.send_otp)
        self.verify_otp_btn = QPushButton("تحقق من OTP")
        self.verify_otp_btn.clicked.connect(self.verify_otp)
        self.verify_otp_btn.setEnabled(False)
        self.reset_btn = QPushButton("تحديث كلمة المرور")
        self.reset_btn.clicked.connect(self.reset_password)
        self.reset_btn.setEnabled(False)
        
        layout.addWidget(QLabel("المعرف:"))
        layout.addWidget(self.id_input)
        layout.addWidget(QLabel("البريد الإلكتروني:"))
        layout.addWidget(self.email_input)
        layout.addWidget(self.send_otp_btn)
        layout.addWidget(QLabel("رمز OTP:"))
        layout.addWidget(self.otp_input)
        layout.addWidget(self.verify_otp_btn)
        layout.addWidget(QLabel("كلمة المرور الجديدة:"))
        layout.addWidget(self.new_password_input)
        layout.addWidget(self.reset_btn)
        
        self.setLayout(layout)
    
    def send_otp(self):
        """إرسال OTP إلى البريد الإلكتروني."""
        self.user_id = self.id_input.text().strip()
        self.email = self.email_input.text().strip()
        
        if not self.user_id or not self.email:
            QMessageBox.warning(self, "خطأ", "أدخل المعرف والبريد!")
            return
        
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, self.email):
            QMessageBox.warning(self, "خطأ", "البريد الإلكتروني غير صالح!")
            return
        
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE student_id=? AND email=?", (self.user_id, self.email))
            user = c.fetchone()
            conn.close()
            
            if not user:
                QMessageBox.warning(self, "خطأ", "المعرف أو البريد غير صحيحين!")
                return
            
            self.otp = str(random.randint(100000, 999999))
            self.otp_expiry = time.time() + 180  # 3 دقائق
            
            self.send_email(self.email, self.otp)
            self.otp_input.setEnabled(True)
            self.verify_otp_btn.setEnabled(True)
            self.send_otp_btn.setEnabled(False)
            self.timer.start()
            QMessageBox.information(self, "نجاح", f"تم إرسال OTP إلى {self.email}.")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل العملية: {e}")
    
    def allow_resend_otp(self):
        """السماح بإعادة إرسال OTP بعد انتهاء الوقت."""
        self.send_otp_btn.setEnabled(True)
    
    def verify_otp(self):
        """التحقق من OTP."""
        if not self.otp_expiry or time.time() > self.otp_expiry:
            QMessageBox.warning(self, "خطأ", "انتهت صلاحية OTP!")
            return
        
        if self.otp_input.text() == self.otp:
            self.new_password_input.setEnabled(True)
            self.reset_btn.setEnabled(True)
            QMessageBox.information(self, "نجاح", "أدخل كلمة مرور جديدة.")
        else:
            QMessageBox.warning(self, "خطأ", "OTP خاطئ!")
    
    def reset_password(self):
        """تحديث كلمة المرور."""
        new_pw = self.new_password_input.text()
        
        if not new_pw or len(new_pw) < 8:
            QMessageBox.warning(self, "خطأ", "كلمة المرور يجب أن تحتوي على 8+ خانات!")
            return
        
        if not (any(c.isdigit() for c in new_pw) and any(c.isalpha() for c in new_pw)):
            QMessageBox.warning(self, "خطأ", "كلمة المرور تحتاج أرقام + حروف!")
            return
        
        if not self.user_id:
            QMessageBox.warning(self, "خطأ", "أعد المحاولة من البداية!")
            return
        
        try:
            # استخدام PasswordHasher لتشفير كلمة المرور (مثل UserManager)
            from registration_system import PasswordHasher_registration_system
            password_hasher = PasswordHasher_registration_system()
            hashed_pw = password_hasher.hash_password(new_pw)
            
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE users SET password_hash=? WHERE student_id=?", (hashed_pw, self.user_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "نجاح", "تم تحديث كلمة المرور!")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل التحديث: {e}")
    
    def send_email(self, to_email, otp):
        """إرسال بريد إلكتروني يحتوي على OTP."""
        EMAIL = 'ie201team2kau@hotmail.com'
        PASSWORD = 'vpgwoxratjbak77895jtt'
        
        msg = EmailMessage()
        msg['From'] = EMAIL
        msg['To'] = to_email
        msg['Subject'] = 'OTP كلمة المرور لمرة واحدة'
        msg.set_content(f"رمز OTP الخاص بك: {otp}\n\nهذا الرمز صالح لمدة 3 دقائق.")
        
        try:
            with smtplib.SMTP("smtp.office365.com", 587) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.send_message(msg)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل إرسال البريد: {e}")


# ============================================================================
# LOGIN DIALOG (As specified in project requirements)
# ============================================================================

class LoginDialog_QDialog_gui(QDialog):
    """
    LoginDialog (PyQt QDialog) as per project requirements
    Handles user authentication
    """
    
    def __init__(self, user_manager: UserManager_registration_system, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.current_user = None
        self.is_dark_mode = False
        
        self.setWindowTitle('تسجيل الدخول - نظام ODUS')
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setGeometry(0, 0, 800, 600)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        window_layout = QVBoxLayout(self)
        
        # Theme button
        top_bar = QHBoxLayout()
        self.theme_button = QPushButton("🌙")
        self.theme_button.setProperty("class", "theme_button")
        self.theme_button.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_button)
        top_bar.addStretch()
        window_layout.addLayout(top_bar)
        
        # Login card
        main_layout = QHBoxLayout()
        login_frame = QWidget()
        login_frame.setProperty("class", "card")
        login_frame.setFixedSize(450, 520)
        apply_shadow(login_frame)
        
        card_layout = QVBoxLayout(login_frame)
        card_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("نظام التسجيل الجامعي")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        card_layout.addSpacing(20)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText('المعرف (مثال: 1678910)')
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@domain.com")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText('كلمة المرور')
        
        form_layout.addRow(QLabel("المعرف:"), self.id_input)
        form_layout.addRow(QLabel("البريد الإلكتروني:"), self.email_input)
        form_layout.addRow(QLabel("كلمة المرور:"), self.pass_input)
        card_layout.addLayout(form_layout)
        card_layout.addStretch()
        
        # Buttons
        self.forgot_password_btn = QPushButton("نسيت كلمة المرور؟")
        self.forgot_password_btn.setProperty("class", "secondary")
        self.forgot_password_btn.setStyleSheet("border: none; text-decoration: underline;")
        self.forgot_password_btn.clicked.connect(self.handle_forgot_password)
        
        self.login_button = QPushButton('تسجيل الدخول')
        self.register_button = QPushButton('إنشاء حساب طالب جديد')
        self.register_button.setProperty("class", "secondary")
        
        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.handle_register)
        
        card_layout.addWidget(self.forgot_password_btn)
        card_layout.addWidget(self.login_button)
        card_layout.addWidget(self.register_button)
        
        main_layout.addStretch()
        main_layout.addWidget(login_frame)
        main_layout.addStretch()
        
        window_layout.addLayout(main_layout)
        window_layout.addStretch()
    
    def toggle_theme(self):
        """Toggle theme."""
        app = QApplication.instance()
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            app.setStyleSheet(DARK_MODE_QSS)
            self.theme_button.setText("☀️")
        else:
            app.setStyleSheet(LIGHT_MODE_QSS)
            self.theme_button.setText("🌙")
    
    def handle_forgot_password(self):
        """فتح نافذة نسيان كلمة المرور."""
        forgot_dialog = ForgotPasswordDialog_QDialog_gui(parent=self)
        forgot_dialog.exec()
    
    def handle_login(self):
        """Handle login attempt."""
        academic_id = self.id_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_input.text()
        
        if not password:
            QMessageBox.warning(self, 'خطأ', 'الرجاء إدخال كلمة المرور!')
            return
        
        # يجب إدخال المعرف أو البريد (أو كليهما)
        if not academic_id and not email:
            QMessageBox.warning(self, 'خطأ', 'الرجاء إدخال المعرف أو البريد الإلكتروني!')
            return
        
        # التحقق من صيغة البريد إذا تم إدخاله
        if email:
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, email):
                QMessageBox.warning(self, 'خطأ', 'البريد الإلكتروني غير صالح!')
                return
        
        # محاولة تسجيل الدخول باستخدام UserManager (يدعم البحث بالمعرف أو البريد)
        # نستخدم المعرف إذا كان موجوداً، وإلا نستخدم البريد
        identifier = academic_id if academic_id else email
        user = self.user_manager.authenticate_user_passwordhasher_accesslogger_registration_system(identifier, password)
        if user:
            self.current_user = user
            self.accept()
            return
        
        # محاولة تسجيل الدخول من قاعدة البيانات (للتوافق مع الكود القديم)
        if academic_id and email:
            db_user = login_user_database_passwordhasher(academic_id, email, password)
            if db_user is not None:
                # إنشاء كائن User من البيانات
                user = User(
                    user_id=db_user["id"],
                    email=db_user["email"],
                    password_hash="",  # لا نحتاج كلمة المرور بعد التحقق
                    role=db_user["role"] or "student",
                    display_name=db_user.get("name", ""),
                    mobile=""
                )
                self.current_user = user
                self.accept()
                return
        
        QMessageBox.warning(self, 'خطأ', 'المعرف أو البريد الإلكتروني أو كلمة المرور غير صحيحة')
    
    def handle_register(self):
        """Handle student registration."""
        dialog = RegisterWindow_QDialog_gui(role='student', user_manager=self.user_manager, parent=self)
        dialog.exec()


class RegisterWindow_QDialog_gui(QDialog):
    """نافذة تسجيل حساب جديد مع دعم أدوار متعددة (طالب، دكتور)."""
    
    def __init__(self, role='student', user_manager: UserManager_registration_system = None, parent=None):
        super().__init__(parent)
        self.role = role
        self.user_manager = user_manager or UserManager_registration_system()
        self.student_manager = StudentManager_registration_system()
        
        self.setWindowTitle(f'إنشاء حساب {self.role} جديد')
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setModal(True)
        self.setGeometry(0, 0, 600, 500)
        
        self.init_ui()
    
    def init_ui(self):
        """تهيئة واجهة المستخدم."""
        card_widget = QWidget()
        card_widget.setProperty("class", "card")
        card_widget.setFixedWidth(400)
        card_widget.setFixedHeight(450)
        apply_shadow(card_widget)
        
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)
        
        title = QLabel(f'إنشاء حساب {self.role} جديد')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("TitleLabel")
        card_layout.addWidget(title)
        
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.mobile_input = QLineEdit()
        
        # Set up mobile input validation: must start with 05, only numbers, max 10 digits
        mobile_validator = QRegularExpressionValidator(QRegularExpression("^05[0-9]{8}$"))
        self.mobile_input.setValidator(mobile_validator)
        self.mobile_input.setPlaceholderText("05XXXXXXXX")
        self.mobile_input.setMaxLength(10)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow('الاسم الكامل:', self.name_input)
        form_layout.addRow('البريد الإلكتروني:', self.email_input)
        form_layout.addRow('رقم الجوال:', self.mobile_input)
        form_layout.addRow('كلمة المرور:', self.password_input)
        
        if self.role == 'student':
            self.program_combo = QComboBox()
            self.program_combo.addItems(['Computer', 'Communications', 'Power', 'Biomedical'])
            form_layout.addRow('البرنامج:', self.program_combo)
            
            self.level_combo = QComboBox()
            self.level_combo.addItems(['Level 1', 'Level 2'])
            form_layout.addRow('المستوى الحالي:', self.level_combo)
        
        card_layout.addLayout(form_layout)
        card_layout.addStretch()
        
        self.register_button = QPushButton('إنشاء الحساب')
        self.register_button.clicked.connect(self.create_account)
        card_layout.addWidget(self.register_button)
        
        main_layout = QHBoxLayout(self)
        main_layout.addStretch()
        main_layout.addWidget(card_widget)
        main_layout.addStretch()
    
    def create_account(self):
        """إنشاء الحساب الجديد."""
        new_password = self.password_input.text()
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        
        if not name or not email or not mobile or not new_password:
            QMessageBox.warning(self, 'خطأ', 'الرجاء ملء جميع الحقول')
            return
        
        # Validate mobile number format
        if not mobile.startswith('05') or len(mobile) != 10 or not mobile.isdigit():
            QMessageBox.warning(self, 'خطأ', 'رقم الجوال يجب أن يبدأ بـ 05 ويتكون من 10 أرقام فقط')
            return
        
        if self.role == 'student':
            # Generate unique student ID (7 digits, starts with 16 or 27)
            user_id = None
            max_attempts = 1000
            attempts = 0
            while user_id is None and attempts < max_attempts:
                # Generate ID starting with 16 or 27
                prefix = random.choice(['16', '27'])
                candidate_id = f"{prefix}{random.randint(10000, 99999)}"
                if not user_identifier_exists(candidate_id):
                    user_id = candidate_id
                attempts += 1
            
            if user_id is None:
                QMessageBox.critical(self, 'خطأ', 'فشل توليد معرف فريد. يرجى المحاولة مرة أخرى.')
                return
            
            # Validate password
            if not (len(new_password) >= 8 and any(c.isdigit() for c in new_password) and any(c.isalpha() for c in new_password)):
                QMessageBox.warning(self, 'خطأ', 'كلمة المرور يجب أن تحتوي على 8+ خانات، أرقام، وحروف.')
                return
            
            # Validate email
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, email):
                QMessageBox.warning(self, 'خطأ', 'البريد الإلكتروني غير صالح!')
                return
            
            program = self.program_combo.currentText()
            program_for_db = 'Comm' if program == 'Communications' else program
            level_label = self.level_combo.currentText()
            
            # Convert level label to integer
            try:
                level_int = int(level_label.split()[-1])
            except Exception:
                level_int = 1
            
            # Add student to database
            db_message = add_student(user_id, name, email, program_for_db, level_int)
            if not db_message.startswith("✅"):
                QMessageBox.critical(self, 'خطأ في التسجيل', db_message)
                return
            
            # Create user account using UserManager (to ensure consistent password hashing)
            success, message = self.user_manager.create_user_passwordvalidator_passwordhasher_registration_system(user_id, email, new_password, "student", name, mobile)
            if not success:
                QMessageBox.critical(self, 'خطأ', f'فشل إنشاء الحساب: {message}')
                return
            
            msg = (f"المعرف الجامعي: {user_id}\nكلمة المرور: {new_password}\n"
                   f"البرنامج: {program} - {level_label}\n"
                   f"{db_message}")
        
        elif self.role == 'doctor':
            new_academic_id = generate_unique_identifier("dr_")
            success, message = self.user_manager.create_user_passwordvalidator_passwordhasher_registration_system(new_academic_id, email, new_password, "doctor", name, mobile, validate_password=False)
            if not success:
                QMessageBox.critical(self, 'خطأ', f'فشل إنشاء الحساب: {message}')
                return
            msg = (f"معرف الدكتور: {new_academic_id}\nكلمة المرور: {new_password}")
        
        QMessageBox.information(self, 'تم إنشاء الحساب بنجاح', msg)
        self.accept()


# ============================================================================
# MAIN APP (As specified in project requirements)
# ============================================================================

class MainApp_QApplication_gui(QApplication):
    """
    MainApp (PyQt QApplication) as per project requirements
    The entry point of the application, responsible for initializing 
    the main window and starting the event loop
    """
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setStyleSheet(LIGHT_MODE_QSS)
        
        self.registration_system = RegistrationSystem_registration_system()
        self.user_manager = UserManager_registration_system()
        self.student_manager = StudentManager_registration_system()
    
    def run(self):
        """Main application loop."""
        while True:
            # Show login dialog
            login = LoginDialog_QDialog_gui(self.user_manager)
            result = login.exec()
            
            if result != QDialog.DialogCode.Accepted:
                break
            
            user = login.current_user
            is_dark = login.is_dark_mode
            
            # Show appropriate dashboard based on role
            if user.is_student():
                student = self.student_manager.get_student(user.user_id)
                if not student:
                    QMessageBox.critical(None, "خطأ", "تعذر تحميل بيانات الطالب")
                    continue
                
                dashboard = StudentDashboard_DashboardBase_student(student, self.registration_system)
                dashboard.is_dark_mode = is_dark
                if is_dark:
                    dashboard.theme_button.setText("☀️")
                dashboard.show()
                exit_code = self.exec()
                
                if exit_code != 100:  # Not logout
                    break
            
            elif user.is_admin():
                dashboard = AdminDashboard_DashboardBase_admin(user, self.registration_system)
                dashboard.is_dark_mode = is_dark
                if is_dark:
                    dashboard.theme_button.setText("☀️")
                dashboard.show()
                exit_code = self.exec()
                
                if exit_code != 100:  # Not logout
                    break
        
        sys.exit(0)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    app = MainApp_QApplication_gui(sys.argv)
    app.run()
