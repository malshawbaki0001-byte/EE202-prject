"""
================================================================================
ملف واجهة المدير - Admin Interface Module (admin.py)
================================================================================

الهدف من الملف:
    هذا الملف يحتوي على جميع الواجهات الرسومية (GUI) المتعلقة بالمدير.
    يوفر واجهة كاملة للمدير لإدارة المقررات، الشعب، والطلاب.

البنية العامة للملف:
    ============================================================================
    AdminDashboard Class (لوحة تحكم المدير)
    ============================================================================
    - يرث من BaseDashboard (المستورد من student.py)
    - الواجهة الرئيسية للمدير
    - علامات التبويب الرئيسية:
        
        1. تبويب المقررات (create_courses_tab):
            - جدول قائمة المقررات
            - نموذج إضافة/تعديل مقرر:
                * رمز المقرر، الاسم، الساعات، ساعات المحاضرة/المعمل
                * السعة القصوى
                * المتطلبات السابقة
                * المستوى (1-10)
                * التخصص (All, Computer, Communications, Power, Biomedical)
                * زر "All" لإضافة المقرر لجميع التخصصات
        
        2. تبويب الشعب (create_sections_tab):
            - قائمة منسدلة لاختيار المقرر
            - جدول الشعب المتاحة
            - نموذج إضافة/تعديل شعبة:
                * معرف الشعبة، المدرس، الوقت، القاعة، السعة
        
        3. تبويب المستخدمين (create_users_tab):
            - جدول جميع الطلاب المسجلين
            - إمكانية حذف الطلاب

العلاقات مع الملفات الأخرى:
    - يستورد من:
        * student.py (BaseDashboard - للوراثة)
        * registration_system.py (User, RegistrationSystem, Course, Section, StudentManager)
        * styles.py (apply_shadow, LIGHT_MODE_QSS, DARK_MODE_QSS)
        * database.py (لعمليات program_plans مباشرة)
        * PyQt6 (مكتبة الواجهات الرسومية)
    - يستخدمه:
        * gui.py (MainApp.run() يستخدم AdminDashboard)
    
التدفق العام:
    1. MainApp.run() ينشئ AdminDashboard بعد تسجيل دخول المدير
    2. AdminDashboard يعرض البيانات من RegistrationSystem و StudentManager
    3. المدير يضيف/يعدل/يحذف المقررات عبر RegistrationSystem
    4. المدير يضيف/يعدل/يحذف الشعب عبر RegistrationSystem
    5. عند اختيار "All" في التخصص، يتم إضافة المقرر لجميع التخصصات
    6. جميع التغييرات تُحفظ في قاعدة البيانات
    
نظام الوراثة المستخدم:
    ✅ BaseDashboard (من student.py) → AdminDashboard
    
المكونات الرئيسية:
    - courses_table: جدول المقررات
    - sections_table: جدول الشعب
    - students_table: جدول الطلاب
    - course_program_input: قائمة التخصصات (تحتوي على "All")
    
الوظائف الخاصة:
    - handle_save_course(): يحفظ المقرر ويدعم "All" لإضافة لجميع التخصصات
    - on_course_selected(): يعرض "All" إذا كان المقرر موجود في جميع التخصصات
    
مثال على الاستخدام:
    from registration_system import User, RegistrationSystem
    from admin import AdminDashboard
    
    user = UserManager().authenticate("admin", "password")
    registration_system = RegistrationSystem()
    dashboard = AdminDashboard(user, registration_system)
    dashboard.show()  # عرض واجهة المدير
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QLineEdit, QFormLayout, QComboBox, QApplication
)

from PyQt6.QtCore import Qt

from registration_system import User, RegistrationSystem_registration_system, Course, Section, StudentManager_registration_system
from student import DashboardBase_QWidget_student
from styles import apply_shadow, LIGHT_MODE_QSS, DARK_MODE_QSS
import database
import database


class AdminDashboard_DashboardBase_admin(DashboardBase_QWidget_student):
    """
    ============================================================================
    كلاس لوحة تحكم المدير - Admin Dashboard Class
    ============================================================================
    
    الوظيفة:
        واجهة المستخدم الرئيسية للمدير في النظام.
    
    Visibility (الرموز):
        + public: يمكن الوصول من أي مكان
        _ private: للاستخدام الداخلي فقط
        # protected: للاستخدام من الكلاسات الفرعية
        يرث من BaseDashboard (المستوردة من student.py) ويضيف وظائف خاصة بالمدير.
        تتفاعل مع RegistrationSystem و StudentManager لإدارة جميع بيانات النظام.
    
    العلاقات والربط:
        - الكلاس الأساسي (Parent Class): BaseDashboard (من student.py السطر 19)
        - الكلاسات التي ترث منه: لا يوجد
        - يتم استخدامه في:
            * gui.py - MainApp.run() (في السطر 320) - يتم إنشاء AdminDashboard للمدير
        - يستخدم الكلاسات التالية:
            * User (من registration_system) - بيانات المدير
            * RegistrationSystem (من registration_system) - نظام التسجيل
            * StudentManager (من registration_system) - إدارة الطلاب
            * Course, Section (من registration_system) - المقررات والشعب
            * database (من database.py) - عمليات قاعدة البيانات مباشرة
    
    مهامه:
        - إدارة المقررات (إضافة/تعديل/حذف) عبر RegistrationSystem.add_course()
        - إدارة الشعب (إضافة/تعديل/حذف) عبر RegistrationSystem.add_section()
        - إدارة الطلاب (عرض/حذف) عبر StudentManager
        - تحديد المستوى والتخصص لكل مقرر عبر database.add_course_to_program_plan()
        - إدارة المتطلبات السابقة للمقررات عبر RegistrationSystem
        - إضافة المقررات لجميع التخصصات عند اختيار "All"
        
    مثال الاستخدام:
        user = UserManager().authenticate("admin", "password")
        registration_system = RegistrationSystem()
        dashboard = AdminDashboard(user, registration_system)
        dashboard.show()  # عرض واجهة المدير
        
    ملاحظة:
        هذا الكلاس يرث من BaseDashboard الموجود في student.py، مما يعني أنه يستفيد
        من وظائف تبديل الثيم وتسجيل الخروج المشتركة بين جميع لوحات التحكم.
    """
    
    # + public method
    def __init__(self, user: User, registration_system: RegistrationSystem_registration_system):
        """
        تهيئة لوحة تحكم المدير
        Args:
            user: كائن المستخدم (المدير)
            registration_system: نظام التسجيل
        """
        super().__init__()
        # + public attribute
        self.user = user
        # + public attribute
        self.registration_system = registration_system
        # + public attribute
        self.student_manager = StudentManager_registration_system()
        
        self.setWindowTitle(f'لوحة تحكم المدير - {user.display_name}')
        self.setGeometry(100, 100, 1100, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.init_ui()
        self.load_data()
    
    # + public method
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout(self)
        
        # شريط علوي
        top_bar = QHBoxLayout()
        self.theme_button = QPushButton("🌙")
        self.theme_button.setProperty("class", "theme_button")
        self.theme_button.clicked.connect(self.toggle_theme)
        
        self.signout_button = QPushButton("تسجيل الخروج")
        self.signout_button.setProperty("class", "secondary")
        self.signout_button.clicked.connect(self.handle_signout)
        
        top_bar.addWidget(self.theme_button)
        top_bar.addWidget(self.signout_button)
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        # تبويبات
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_courses_tab(), "المقررات")
        self.tab_widget.addTab(self.create_sections_tab(), "الشعب")
        self.tab_widget.addTab(self.create_users_tab(), "المستخدمون")
        self.tab_widget.addTab(self.create_doctors_tab(), "Doctor")
        layout.addWidget(self.tab_widget)
    
    def create_courses_tab(self) -> QWidget:
        """
        إنشاء تبويب إدارة المقررات
        وظيفته: إدارة المقررات (إضافة/تعديل/حذف)
        Returns:
            ويدجت يحتوي على تبويب المقررات
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        
        # الجانب الأيسر - قائمة المقررات
        list_frame = QFrame()
        list_frame.setProperty("class", "card")
        apply_shadow(list_frame)
        list_layout = QVBoxLayout(list_frame)
        
        list_layout.addWidget(QLabel("قائمة المقررات"))
        
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(5)
        self.courses_table.setHorizontalHeaderLabels([
            'الرمز', 'الاسم', 'الساعات', 'ساعات المحاضرة', 'ساعات المعمل'
        ])
        self.courses_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.courses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.courses_table.itemSelectionChanged.connect(self.on_course_selected)
        list_layout.addWidget(self.courses_table)
        
        layout.addWidget(list_frame, 2)
        
        # الجانب الأيمن - نموذج المقرر
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        apply_shadow(form_frame)
        form_layout = QVBoxLayout(form_frame)
        
        form_layout.addWidget(QLabel("إضافة / تعديل مقرر"))
        
        form = QFormLayout()
        self.course_code_input = QLineEdit()
        self.course_name_input = QLineEdit()
        self.course_credits_input = QLineEdit()
        self.course_lecture_hours_input = QLineEdit()
        self.course_lab_hours_input = QLineEdit()
        self.course_prerequisites_input = QLineEdit()
        self.course_prerequisites_input.setPlaceholderText('مثال: COE200, MATH201 (مفصولة بفواصل)')
        
        # اختيار المستوى والتخصص
        self.course_level_input = QComboBox()
        self.course_level_input.addItems([str(i) for i in range(1, 11)])  # المستويات من 1 إلى 10
        
        self.course_program_input = QComboBox()
        self.course_program_input.addItems(['All', 'Computer', 'Communications', 'Power', 'Biomedical'])
        
        form.addRow("رمز المقرر:", self.course_code_input)
        form.addRow("اسم المقرر:", self.course_name_input)
        form.addRow("الساعات المعتمدة:", self.course_credits_input)
        form.addRow("ساعات المحاضرة:", self.course_lecture_hours_input)
        form.addRow("ساعات المعمل:", self.course_lab_hours_input)
        form.addRow("المستوى:", self.course_level_input)
        form.addRow("التخصص:", self.course_program_input)
        form.addRow("المتطلبات السابقة:", self.course_prerequisites_input)
        form_layout.addLayout(form)
        
        # الأزرار
        save_btn = QPushButton("حفظ المقرر")
        save_btn.clicked.connect(self.handle_save_course)
        form_layout.addWidget(save_btn)
        
        delete_btn = QPushButton("حذف المقرر")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(self.handle_delete_course)
        form_layout.addWidget(delete_btn)
        
        clear_btn = QPushButton("تفريغ الحقول")
        clear_btn.setProperty("class", "secondary")
        clear_btn.clicked.connect(self.clear_course_form)
        form_layout.addWidget(clear_btn)
        
        form_layout.addStretch()
        
        layout.addWidget(form_frame, 1)
        
        return container
    
    def create_sections_tab(self) -> QWidget:
        """
        إنشاء تبويب إدارة الشعب
        وظيفته: إدارة الشعب (إضافة/تعديل/حذف)
        Returns:
            ويدجت يحتوي على تبويب الشعب
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        
        # الجانب الأيسر - قائمة الشعب
        list_frame = QFrame()
        list_frame.setProperty("class", "card")
        apply_shadow(list_frame)
        list_layout = QVBoxLayout(list_frame)
        
        list_layout.addWidget(QLabel("اختر مادة لعرض شعبها"))
        
        self.sections_course_combo = QComboBox()
        self.sections_course_combo.currentTextChanged.connect(self.on_sections_course_changed)
        list_layout.addWidget(self.sections_course_combo)
        
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(7)
        self.sections_table.setHorizontalHeaderLabels([
            'المعرف', 'المدرس', 'البدء', 'الانتهاء', 'القاعة', 'السعة', 'المسجلين'
        ])
        self.sections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sections_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sections_table.itemSelectionChanged.connect(self.on_section_selected)
        list_layout.addWidget(self.sections_table)
        
        layout.addWidget(list_frame, 2)
        
        # الجانب الأيمن - نموذج الشعبة
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        apply_shadow(form_frame)
        form_layout = QVBoxLayout(form_frame)
        
        form_layout.addWidget(QLabel("إضافة / تعديل شعبة"))
        
        form = QFormLayout()
        self.section_id_input = QLineEdit()
        self.section_instructor_input = QLineEdit()
        
        # قائمة منسدلة لاختيار الوقت (بدلاً من الإدخال اليدوي)
        self.section_time_combo = QComboBox()
        self.section_time_combo.addItem("اختر الوقت...", None)
        self.section_time_combo.addItem("الأحد والثلاثاء والخميس من 8 إلى 9", (8, 9))
        self.section_time_combo.addItem("الأحد والثلاثاء والخميس من 10 إلى 11", (10, 11))
        self.section_time_combo.addItem("الإثنين والأربعاء من 10 إلى 11", (10, 11))
        self.section_time_combo.addItem("الإثنين والأربعاء من 2 إلى 4", (2, 4))
        self.section_time_combo.addItem("الإثنين والأربعاء من 12 إلى 1", (12, 1))
        self.section_time_combo.currentIndexChanged.connect(self.on_time_selected)
                
        # حقول مخفية لتخزين الأوقات
        self.section_start_input = QLineEdit()
        self.section_start_input.setVisible(False)
        self.section_end_input = QLineEdit()
        self.section_end_input.setVisible(False)
        
        self.section_hall_input = QLineEdit()
        self.section_capacity_input = QLineEdit()
        
        form.addRow("معرف الشعبة:", self.section_id_input)
        form.addRow("المدرس:", self.section_instructor_input)
        form.addRow("الوقت:", self.section_time_combo)
        form.addRow("القاعة:", self.section_hall_input)
        form.addRow("السعة القصوى:", self.section_capacity_input)
        form_layout.addLayout(form)
        
        # الأزرار
        save_btn = QPushButton("حفظ الشعبة")
        save_btn.clicked.connect(self.handle_save_section)
        form_layout.addWidget(save_btn)
        
        delete_btn = QPushButton("حذف الشعبة")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(self.handle_delete_section)
        form_layout.addWidget(delete_btn)
        
        clear_btn = QPushButton("تفريغ الحقول")
        clear_btn.setProperty("class", "secondary")
        clear_btn.clicked.connect(self.clear_section_form)
        form_layout.addWidget(clear_btn)
        
        form_layout.addStretch()
        
        layout.addWidget(form_frame, 1)
        
        return container
    
    def create_users_tab(self) -> QWidget:
        """
        إنشاء تبويب إدارة المستخدمين
        وظيفته: عرض وإدارة الطلاب
        Returns:
            ويدجت يحتوي على تبويب المستخدمين
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # قسم الطلاب
        students_frame = QFrame()
        students_frame.setProperty("class", "card")
        apply_shadow(students_frame)
        students_layout = QVBoxLayout(students_frame)
        
        students_layout.addWidget(QLabel("الطلاب"))
        
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels([
            'المعرف', 'الاسم', 'البريد', 'البرنامج', 'المستوى'
        ])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        students_layout.addWidget(self.students_table)
        
        delete_student_btn = QPushButton("حذف الطالب المحدد")
        delete_student_btn.setProperty("class", "danger")
        delete_student_btn.clicked.connect(self.handle_delete_student)
        students_layout.addWidget(delete_student_btn)
        
        layout.addWidget(students_frame)
        
        return container
    
    def create_doctors_tab(self) -> QWidget:
        """
        إنشاء تبويب إدارة الأطباء/أعضاء هيئة التدريس
        وظيفته: إدارة الأطباء وتعيين المقررات لهم مع فحص التعارضات
        Returns:
            ويدجت يحتوي على تبويب الأطباء
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        
        # الجانب الأيسر - قائمة الأطباء والتعيينات
        left_frame = QFrame()
        left_frame.setProperty("class", "card")
        apply_shadow(left_frame)
        left_layout = QVBoxLayout(left_frame)
        
        left_layout.addWidget(QLabel("قائمة Doctor"))
        
        # جدول الأطباء
        self.doctors_table = QTableWidget()
        self.doctors_table.setColumnCount(3)
        self.doctors_table.setHorizontalHeaderLabels(['المعرف', 'الاسم', 'البريد'])
        self.doctors_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.doctors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.doctors_table.itemSelectionChanged.connect(self.on_doctor_selected)
        left_layout.addWidget(self.doctors_table)
        
        # نموذج إضافة/تعديل دكتور
        doctor_form_frame = QFrame()
        doctor_form_layout = QVBoxLayout(doctor_form_frame)
        doctor_form_layout.addWidget(QLabel("إضافة / تعديل Doctor"))
        
        form = QFormLayout()
        self.doctor_id_input = QLineEdit()
        self.doctor_name_input = QLineEdit()
        self.doctor_email_input = QLineEdit()
        self.doctor_preferred_courses_input = QLineEdit()
        self.doctor_preferred_courses_input.setPlaceholderText('مثال: COE200, MATH201 (مفصولة بفواصل)')
        self.doctor_time_availability_input = QLineEdit()
        self.doctor_time_availability_input.setPlaceholderText('مثال: Sunday-Tuesday 8-10, Wednesday-Thursday 14-16')
        
        form.addRow("معرف Doctor:", self.doctor_id_input)
        form.addRow("الاسم:", self.doctor_name_input)
        form.addRow("البريد:", self.doctor_email_input)
        form.addRow("المقررات المفضلة:", self.doctor_preferred_courses_input)
        form.addRow("التوفر الزمني:", self.doctor_time_availability_input)
        doctor_form_layout.addLayout(form)
        
        buttons_layout = QHBoxLayout()
        save_doctor_btn = QPushButton("حفظ Doctor")
        save_doctor_btn.clicked.connect(self.handle_save_doctor)
        delete_doctor_btn = QPushButton("حذف Doctor")
        delete_doctor_btn.setProperty("class", "danger")
        delete_doctor_btn.clicked.connect(self.handle_delete_doctor)
        buttons_layout.addWidget(save_doctor_btn)
        buttons_layout.addWidget(delete_doctor_btn)
        doctor_form_layout.addLayout(buttons_layout)
        
        left_layout.addWidget(doctor_form_frame)
        
        # جدول التعيينات
        assignments_label = QLabel("التعيينات الحالية:")
        left_layout.addWidget(assignments_label)
        
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(3)
        self.assignments_table.setHorizontalHeaderLabels(['المقرر', 'الشعبة', 'الإجراء'])
        self.assignments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.assignments_table)
        
        layout.addWidget(left_frame, 1)
        
        # الجانب الأيمن - تعيين مقرر و الجدول الزمني
        right_frame = QFrame()
        right_frame.setProperty("class", "card")
        apply_shadow(right_frame)
        right_layout = QVBoxLayout(right_frame)
        
        right_layout.addWidget(QLabel("تعيين مقرر للـ Doctor"))
        
        assign_form = QFormLayout()
        self.assign_course_combo = QComboBox()
        self.assign_course_combo.currentTextChanged.connect(self.update_sections_combo)
        self.assign_section_combo = QComboBox()
        
        assign_form.addRow("المقرر:", self.assign_course_combo)
        assign_form.addRow("الشعبة:", self.assign_section_combo)
        right_layout.addLayout(assign_form)
        
        assign_btn = QPushButton("تعيين")
        assign_btn.clicked.connect(self.handle_assign_course)
        right_layout.addWidget(assign_btn)
        
        remove_assignment_btn = QPushButton("إزالة التعيين المحدد")
        remove_assignment_btn.setProperty("class", "danger")
        remove_assignment_btn.clicked.connect(self.handle_remove_assignment)
        right_layout.addWidget(remove_assignment_btn)
        
        # الجدول الزمني البصري
        right_layout.addWidget(QLabel("الجدول الزمني للـ Doctor"))
        
        self.doctor_schedule_table = QTableWidget()
        self.doctor_schedule_table.setColumnCount(4)
        self.doctor_schedule_table.setHorizontalHeaderLabels(['المقرر', 'الوقت', 'القاعة', 'الحالة'])
        self.doctor_schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.doctor_schedule_table)
        
        layout.addWidget(right_frame, 1)
        
        return container
    
    def load_data(self):
        """تحميل جميع البيانات في الواجهة"""
        self.load_courses()
        self.load_sections_courses()
        self.load_students()
        self.load_doctors()
    
    def load_courses(self):
        """تحميل المقررات في الجدول"""
        self.courses_table.setRowCount(0)
        courses = self.registration_system._course_cache
        
        for i, course in enumerate(courses.values()):
            self.courses_table.insertRow(i)
            self.courses_table.setItem(i, 0, QTableWidgetItem(course.course_code))
            self.courses_table.setItem(i, 1, QTableWidgetItem(course.name))
            self.courses_table.setItem(i, 2, QTableWidgetItem(str(course.credits)))
            self.courses_table.setItem(i, 3, QTableWidgetItem(str(course.lecture_hours)))
            self.courses_table.setItem(i, 4, QTableWidgetItem(str(course.lab_hours)))
    
    def load_sections_courses(self):
        """تحميل المقررات في القائمة المنسدلة للشعب"""
        self.sections_course_combo.clear()
        courses = self.registration_system._course_cache
        for code in sorted(courses.keys()):
            self.sections_course_combo.addItem(code)
    
    def load_sections(self, course_code: str):
        """تحميل الشعب للمقرر المحدد"""
        self.sections_table.setRowCount(0)
        sections = [
            s for s in self.registration_system._section_cache.values()
            if s.course_code == course_code
        ]
        
        for i, section in enumerate(sections):
            self.sections_table.insertRow(i)
            self.sections_table.setItem(i, 0, QTableWidgetItem(section.section_id))
            self.sections_table.setItem(i, 1, QTableWidgetItem(section.instructor))
            self.sections_table.setItem(i, 2, QTableWidgetItem(str(section.start_time)))
            self.sections_table.setItem(i, 3, QTableWidgetItem(str(section.end_time)))
            self.sections_table.setItem(i, 4, QTableWidgetItem(section.hall))
            self.sections_table.setItem(i, 5, QTableWidgetItem(str(section.max_capacity)))
            self.sections_table.setItem(i, 6, QTableWidgetItem(str(section.current_enrollment)))
    
    def load_students(self):
        """تحميل الطلاب في الجدول"""
        self.students_table.setRowCount(0)
        students = self.student_manager.get_all_students_database()
        
        for i, (sid, name, email, program, level) in enumerate(students):
            self.students_table.insertRow(i)
            self.students_table.setItem(i, 0, QTableWidgetItem(sid))
            self.students_table.setItem(i, 1, QTableWidgetItem(name))
            self.students_table.setItem(i, 2, QTableWidgetItem(email))
            self.students_table.setItem(i, 3, QTableWidgetItem(program))
            self.students_table.setItem(i, 4, QTableWidgetItem(str(level)))
    
    def on_course_selected(self):
        """
        معالجة اختيار المقرر
        وظيفته: تحميل بيانات المقرر المحدد في النموذج
        """
        row = self.courses_table.currentRow()
        if row >= 0:
            course_code = self.courses_table.item(row, 0).text()
            self.course_code_input.setText(course_code)
            self.course_name_input.setText(self.courses_table.item(row, 1).text())
            self.course_credits_input.setText(self.courses_table.item(row, 2).text())
            self.course_lecture_hours_input.setText(self.courses_table.item(row, 3).text())
            self.course_lab_hours_input.setText(self.courses_table.item(row, 4).text())
            
            # تحميل المتطلبات السابقة للمقرر المحدد
            course = self.registration_system.get_course(course_code)
            if course and course.prerequisites:
                self.course_prerequisites_input.setText(', '.join(course.prerequisites))
            else:
                self.course_prerequisites_input.clear()
            
            # تحميل المستوى والتخصص من program_plans
            program_plans = database.get_course_program_plans(course_code)
            if program_plans:
                # التحقق من وجود المقرر في جميع التخصصات (All)
                all_programs = ['Computer', 'Comm', 'Power', 'Biomedical']
                programs_in_plans = [prog for prog, lev in program_plans]
                
                # إذا كان المقرر موجود في جميع التخصصات الأربعة بنفس المستوى
                if len(program_plans) == 4:
                    # التحقق من أن جميع البرامج موجودة ونفس المستوى
                    levels = [lev for prog, lev in program_plans]
                    if len(set(levels)) == 1 and all(prog in programs_in_plans for prog in all_programs):
                        # المقرر مضافة لجميع التخصصات
                        self.course_program_input.setCurrentIndex(0)  # "All" هو أول عنصر
                        level = program_plans[0][1]  # نفس المستوى لجميع البرامج
                        index = self.course_level_input.findText(str(level))
                        if index >= 0:
                            self.course_level_input.setCurrentIndex(index)
                    else:
                        # استخدام أول خطة برنامج موجودة
                        program, level = program_plans[0]
                        if program == 'Comm':
                            program = 'Communications'
                        index = self.course_program_input.findText(program)
                        if index >= 0:
                            self.course_program_input.setCurrentIndex(index)
                        index = self.course_level_input.findText(str(level))
                        if index >= 0:
                            self.course_level_input.setCurrentIndex(index)
                else:
                    # استخدام أول خطة برنامج موجودة
                    program, level = program_plans[0]
                    # تحويل 'Comm' إلى 'Communications' إذا لزم الأمر
                    if program == 'Comm':
                        program = 'Communications'
                    index = self.course_program_input.findText(program)
                    if index >= 0:
                        self.course_program_input.setCurrentIndex(index)
                    index = self.course_level_input.findText(str(level))
                    if index >= 0:
                        self.course_level_input.setCurrentIndex(index)
    
    def on_sections_course_changed(self, course_code: str):
        """معالجة تغيير اختيار المقرر في تبويب الشعب"""
        if course_code:
            self.load_sections(course_code)
    
    def on_section_selected(self):
        """معالجة اختيار الشعبة"""
        row = self.sections_table.currentRow()
        if row >= 0:
            # الأعمدة: 0=section_id, 1=instructor, 2=start_time, 3=end_time, 4=hall, 5=max_capacity, 6=current_enrollment
            section_id = self.sections_table.item(row, 0).text()
            self.section_id_input.setText(section_id)
            self.section_instructor_input.setText(self.sections_table.item(row, 1).text())
            start_time = int(self.sections_table.item(row, 2).text())
            end_time = int(self.sections_table.item(row, 3).text())
            
            # الحصول على كائن section للحصول على days
            section = self.registration_system.get_section(section_id)
            days_str = section.days if section else ''
            
            # تحديد الخيار في القائمة المنسدلة بناءً على الأوقات والأيام
            time_data = (start_time, end_time)
            found_index = 0
            
            # البحث عن الخيار المناسب بناءً على الأوقات والأيام
            for i in range(1, self.section_time_combo.count()):
                combo_text = self.section_time_combo.itemText(i)
                combo_data = self.section_time_combo.itemData(i)
                if combo_data == time_data:
                    # التحقق من أن الأيام متطابقة
                    combo_days = self.extract_days_from_time_text(combo_text)
                    if combo_days == days_str or (not days_str and i <= 2):  # للتوافق مع البيانات القديمة
                        found_index = i
                        break
            
            self.section_time_combo.setCurrentIndex(found_index)
            # ملء الحقول المخفية
            self.section_start_input.setText(str(start_time))
            self.section_end_input.setText(str(end_time))
            
            self.section_hall_input.setText(self.sections_table.item(row, 4).text())
            self.section_capacity_input.setText(self.sections_table.item(row, 5).text())
    
    def handle_save_course(self):
        """
        حفظ المقرر في قاعدة البيانات مع التحقق
        وظيفته: حفظ أو تحديث بيانات المقرر مع التحقق من صحة البيانات
        """
        # التحقق من جميع الحقول الإلزامية
        course_code = self.course_code_input.text().strip()
        name = self.course_name_input.text().strip()
        credits_text = self.course_credits_input.text().strip()
        lecture_hours_text = self.course_lecture_hours_input.text().strip()
        
        # التحقق من الحقول الإلزامية
        if not course_code:
            QMessageBox.warning(self, 'خطأ', 'رمز المقرر مطلوب')
            return
        if not name:
            QMessageBox.warning(self, 'خطأ', 'اسم المقرر مطلوب')
            return
        if not credits_text:
            QMessageBox.warning(self, 'خطأ', 'الساعات المعتمدة مطلوبة')
            return
        if not lecture_hours_text:
            QMessageBox.warning(self, 'خطأ', 'ساعات المحاضرة مطلوبة')
            return
        
        # تحليل المتطلبات السابقة
        prereq_text = self.course_prerequisites_input.text().strip()
        prerequisites = []
        if prereq_text:
            prerequisites = [p.strip() for p in prereq_text.split(',') if p.strip()]
        
        try:
            course = Course(
                course_code=course_code,
                name=name,
                credits=int(credits_text),
                lecture_hours=int(lecture_hours_text),
                lab_hours=int(self.course_lab_hours_input.text().strip() or 0),
                prerequisites=prerequisites
            )
            
            self.registration_system.add_course(course)
            
            # حفظ المستوى والتخصص في program_plans
            # أولاً، إزالة خطط البرنامج القديمة لهذا المقرر إذا كان التحديث
            old_plans = database.get_course_program_plans(course_code)
            for old_program, old_level in old_plans:
                database.remove_course_from_program_plan(course_code, old_program, old_level)
            
            # إضافة خطة برنامج جديدة
            level = int(self.course_level_input.currentText())
            program = self.course_program_input.currentText()
            
            # إذا تم اختيار "All"، إضافة المقرر لجميع التخصصات
            if program == 'All':
                all_programs = ['Computer', 'Comm', 'Power', 'Biomedical']
                for prog in all_programs:
                    database.add_course_to_program_plan(course_code, prog, level)
            else:
                # تحويل 'Communications' إلى 'Comm' للتوافق مع قاعدة البيانات
                if program == 'Communications':
                    program = 'Comm'
                database.add_course_to_program_plan(course_code, program, level)
            
            self.load_courses()
            self.load_sections_courses()
            QMessageBox.information(self, 'نجاح', 'تم حفظ المقرر بنجاح')
            self.clear_course_form()
        except ValueError as e:
            error_msg = str(e)
            # تحسين رسالة الخطأ لرمز المقرر المكرر
            if 'already exists' in error_msg.lower() or 'unique' in error_msg.lower():
                QMessageBox.warning(self, 'خطأ', f"رمز المقرر '{course_code}' موجود بالفعل")
            else:
                QMessageBox.warning(self, 'خطأ', error_msg)
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'فشل حفظ المقرر: {str(e)}')
    
    def handle_delete_course(self):
        """حذف المقرر المحدد"""
        course_code = self.course_code_input.text().strip()
        if not course_code:
            QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار مقرر أولاً')
            return
        
        reply = QMessageBox.question(
            self, 'تأكيد الحذف',
            f'هل أنت متأكد من حذف المقرر {course_code}؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.registration_system.delete_course(course_code)
                self.load_courses()
                self.load_sections_courses()
                self.clear_course_form()
                QMessageBox.information(self, 'نجاح', 'تم حذف المقرر بنجاح')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'فشل الحذف: {str(e)}')
    
    def clear_course_form(self):
        """تفريغ حقول نموذج المقرر"""
        self.course_code_input.clear()
        self.course_name_input.clear()
        self.course_credits_input.clear()
        self.course_lecture_hours_input.clear()
        self.course_lab_hours_input.clear()
        self.course_prerequisites_input.clear()
        self.course_level_input.setCurrentIndex(0)  # إعادة تعيين إلى المستوى 1
        self.course_program_input.setCurrentIndex(0)  # إعادة تعيين إلى أول برنامج
    
    def handle_save_section(self):
        """حفظ الشعبة في قاعدة البيانات"""
        try:
            course_code = self.sections_course_combo.currentText()
            if not course_code:
                QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار مادة أولاً')
                return
            
            # التحقق من اختيار الوقت
            if not self.section_start_input.text().strip() or not self.section_end_input.text().strip():
                QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار الوقت من القائمة')
                return
            
            # استخراج الأيام من النص المختار
            time_text = self.section_time_combo.currentText()
            days = self.extract_days_from_time_text(time_text)
            
            section = Section(
                section_id=self.section_id_input.text().strip(),
                course_code=course_code,
                instructor=self.section_instructor_input.text().strip(),
                start_time=int(self.section_start_input.text().strip()),
                end_time=int(self.section_end_input.text().strip()),
                hall=self.section_hall_input.text().strip(),
                max_capacity=int(self.section_capacity_input.text().strip()),
                days=days
            )
            
            self.registration_system.add_section(section)
            self.load_sections(course_code)
            QMessageBox.information(self, 'نجاح', 'تم حفظ الشعبة بنجاح')
            self.clear_section_form()
        except ValueError as e:
            QMessageBox.warning(self, 'خطأ', str(e))
    
    def handle_delete_section(self):
        """حذف الشعبة المحددة"""
        section_id = self.section_id_input.text().strip()
        if not section_id:
            QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار شعبة أولاً')
            return
        
        reply = QMessageBox.question(
            self, 'تأكيد الحذف',
            f'هل أنت متأكد من حذف الشعبة {section_id}؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.registration_system.delete_section(section_id)
                course_code = self.sections_course_combo.currentText()
                self.load_sections(course_code)
                self.clear_section_form()
                QMessageBox.information(self, 'نجاح', 'تم حذف الشعبة بنجاح')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'فشل الحذف: {str(e)}')
    
    def on_time_selected(self, index):
        """ملء الأوقات تلقائياً عند اختيار الوقت من القائمة"""
        time_data = self.section_time_combo.itemData(index)
        if time_data:
            start_time, end_time = time_data
            self.section_start_input.setText(str(start_time))
            self.section_end_input.setText(str(end_time))
            
            # استخراج الأيام من النص المختار
            time_text = self.section_time_combo.currentText()
            days = self.extract_days_from_time_text(time_text)
            # حفظ الأيام في حقل مخفي (سنستخدم section_id_input مؤقتاً أو نضيف حقل جديد)
            if not hasattr(self, 'section_days_input'):
                # سنستخدم طريقة أخرى - سنحفظها مباشرة في handle_save_section
                pass
        else:
            self.section_start_input.clear()
            self.section_end_input.clear()
    
    def extract_days_from_time_text(self, time_text: str) -> str:
        """استخراج أيام الأسبوع من نص الوقت"""
        days_map = {
            'الأحد': 'الأحد',
            'الإثنين': 'الإثنين',
            'الثلاثاء': 'الثلاثاء',
            'الأربعاء': 'الأربعاء',
            'الخميس': 'الخميس',
            'السبت': 'السبت'
        }
        found_days = []
        for day_ar, day_ar_key in days_map.items():
            if day_ar in time_text:
                found_days.append(day_ar)
        return ','.join(found_days)
    
    def clear_section_form(self):
        """تفريغ حقول نموذج الشعبة"""
        self.section_id_input.clear()
        self.section_instructor_input.clear()
        self.section_time_combo.setCurrentIndex(0)  # إعادة تعيين القائمة
        self.section_start_input.clear()
        self.section_end_input.clear()
        self.section_hall_input.clear()
        self.section_capacity_input.clear()
    
    def handle_delete_student(self):
        """حذف الطالب المحدد"""
        row = self.students_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار طالب أولاً')
            return
        
        student_id = self.students_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, 'تأكيد الحذف',
            f'هل أنت متأكد من حذف الطالب {student_id}؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.student_manager.delete_student(student_id)
                self.load_students()
                QMessageBox.information(self, 'نجاح', 'تم حذف الطالب بنجاح')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'فشل الحذف: {str(e)}')
    
    # ============================================================================
    # Doctor/Faculty Management Functions
    # ============================================================================
    
    def load_doctors(self):
        """تحميل قائمة الأطباء في الجدول"""
        self.doctors_table.setRowCount(0)
        doctors = database.get_all_doctors()
        
        for i, (doctor_id, name, email, preferred_courses, time_availability) in enumerate(doctors):
            self.doctors_table.insertRow(i)
            self.doctors_table.setItem(i, 0, QTableWidgetItem(doctor_id))
            self.doctors_table.setItem(i, 1, QTableWidgetItem(name))
            self.doctors_table.setItem(i, 2, QTableWidgetItem(email))
        
        # تحميل قائمة المقررات في assign_course_combo
        self.assign_course_combo.clear()
        courses = self.registration_system._course_cache
        for code in sorted(courses.keys()):
            self.assign_course_combo.addItem(code)
    
    def on_doctor_selected(self):
        """معالجة اختيار دكتور من الجدول"""
        row = self.doctors_table.currentRow()
        if row >= 0:
            doctor_id = self.doctors_table.item(row, 0).text()
            doctor = database.get_doctor(doctor_id)
            
            if doctor:
                self.doctor_id_input.setText(doctor[0])
                self.doctor_name_input.setText(doctor[1])
                self.doctor_email_input.setText(doctor[2])
                self.doctor_preferred_courses_input.setText(doctor[3] or '')
                self.doctor_time_availability_input.setText(doctor[4] or '')
                
                # تحميل التعيينات والجدول الزمني
                self.load_doctor_assignments(doctor_id)
                self.load_doctor_schedule(doctor_id)
    
    def handle_save_doctor(self):
        """حفظ بيانات Doctor"""
        doctor_id = self.doctor_id_input.text().strip()
        name = self.doctor_name_input.text().strip()
        email = self.doctor_email_input.text().strip()
        
        if not doctor_id:
            QMessageBox.warning(self, 'خطأ', 'معرف Doctor مطلوب')
            return
        if not name:
            QMessageBox.warning(self, 'خطأ', 'اسم Doctor مطلوب')
            return
        if not email:
            QMessageBox.warning(self, 'خطأ', 'البريد الإلكتروني مطلوب')
            return
        
        try:
            preferred_courses = self.doctor_preferred_courses_input.text().strip()
            time_availability = self.doctor_time_availability_input.text().strip()
            
            database.add_doctor(doctor_id, name, email, preferred_courses, time_availability)
            
            self.load_doctors()
            QMessageBox.information(self, 'نجاح', 'تم حفظ Doctor بنجاح')
            self.clear_doctor_form()
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'فشل حفظ Doctor: {str(e)}')
    
    def handle_delete_doctor(self):
        """حذف Doctor"""
        doctor_id = self.doctor_id_input.text().strip()
        if not doctor_id:
            QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار Doctor أولاً')
            return
        
        reply = QMessageBox.question(
            self, 'تأكيد الحذف',
            f'هل أنت متأكد من حذف Doctor {doctor_id}؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                database.delete_doctor(doctor_id)
                self.load_doctors()
                self.clear_doctor_form()
                QMessageBox.information(self, 'نجاح', 'تم حذف Doctor بنجاح')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'فشل الحذف: {str(e)}')
    
    def update_sections_combo(self, course_code: str):
        """تحديث قائمة الشعب عند اختيار مقرر"""
        self.assign_section_combo.clear()
        if course_code:
            sections = [
                s for s in self.registration_system._section_cache.values()
                if s.course_code == course_code
            ]
            for section in sections:
                self.assign_section_combo.addItem(section.section_id)
    
    def handle_assign_course(self):
        """تعيين مقرر للـ Doctor مع فحص التعارضات"""
        row = self.doctors_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار Doctor أولاً')
            return
        
        doctor_id = self.doctors_table.item(row, 0).text()
        course_code = self.assign_course_combo.currentText()
        section_id = self.assign_section_combo.currentText()
        
        if not course_code:
            QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار مقرر')
            return
        if not section_id:
            QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار شعبة')
            return
        
        try:
            # الحصول على بيانات الشعبة
            section = self.registration_system.get_section(section_id)
            if not section:
                QMessageBox.warning(self, 'خطأ', 'الشعبة المحددة غير موجودة')
                return
            
            # التحقق من أن الشعبة تابعة للمقرر المحدد
            if section.course_code != course_code:
                QMessageBox.warning(self, 'خطأ', 'الشعبة المحددة لا تنتمي لهذا المقرر')
                return
            
            # فحص التعارضات الزمنية
            has_conflict = database.check_doctor_time_conflict(
                doctor_id, section.start_time, section.end_time
            )
            
            if has_conflict:
                reply = QMessageBox.question(
                    self, 'تعارض زمني',
                    'يوجد تعارض زمني مع التعيينات الموجودة. هل تريد المتابعة؟',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # تعيين المقرر
            database.assign_course_to_doctor(doctor_id, course_code, section_id)
            
            self.load_doctor_assignments(doctor_id)
            self.load_doctor_schedule(doctor_id)
            QMessageBox.information(self, 'نجاح', 'تم تعيين المقرر بنجاح')
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'فشل التعيين: {str(e)}')
    
    def handle_remove_assignment(self):
        """إزالة تعيين من Doctor"""
        row = self.assignments_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'خطأ', 'الرجاء اختيار تعيين أولاً')
            return
        
        assignment_id_item = self.assignments_table.item(row, 3)  # assignment_id مخفي في العمود 3
        if not assignment_id_item:
            QMessageBox.warning(self, 'خطأ', 'تعيين غير صحيح')
            return
        
        assignment_id = int(assignment_id_item.text())
        
        try:
            database.remove_doctor_assignment(assignment_id)
            
            # إعادة تحميل البيانات
            doctor_row = self.doctors_table.currentRow()
            if doctor_row >= 0:
                doctor_id = self.doctors_table.item(doctor_row, 0).text()
                self.load_doctor_assignments(doctor_id)
                self.load_doctor_schedule(doctor_id)
            
            QMessageBox.information(self, 'نجاح', 'تم إزالة التعيين بنجاح')
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'فشل الإزالة: {str(e)}')
    
    def load_doctor_assignments(self, doctor_id: str):
        """تحميل تعيينات Doctor في الجدول"""
        self.assignments_table.setRowCount(0)
        assignments = database.get_doctor_assignments(doctor_id)
        
        for i, (assignment_id, doc_id, course_code, section_id) in enumerate(assignments):
            self.assignments_table.insertRow(i)
            self.assignments_table.setItem(i, 0, QTableWidgetItem(course_code))
            self.assignments_table.setItem(i, 1, QTableWidgetItem(section_id or 'N/A'))
            
            # زر الحذف
            remove_btn = QPushButton("حذف")
            remove_btn.setProperty("class", "danger")
            remove_btn.clicked.connect(lambda checked, aid=assignment_id: self.remove_assignment_by_id(aid))
            self.assignments_table.setCellWidget(i, 2, remove_btn)
            
            # حفظ assignment_id في عمود مخفي
            self.assignments_table.setItem(i, 3, QTableWidgetItem(str(assignment_id)))
            self.assignments_table.setColumnHidden(3, True)
    
    def remove_assignment_by_id(self, assignment_id: int):
        """إزالة تعيين بواسطة ID"""
        try:
            database.remove_doctor_assignment(assignment_id)
            
            # إعادة تحميل البيانات
            doctor_row = self.doctors_table.currentRow()
            if doctor_row >= 0:
                doctor_id = self.doctors_table.item(doctor_row, 0).text()
                self.load_doctor_assignments(doctor_id)
                self.load_doctor_schedule(doctor_id)
            
            QMessageBox.information(self, 'نجاح', 'تم إزالة التعيين بنجاح')
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'فشل الإزالة: {str(e)}')
    
    def load_doctor_schedule(self, doctor_id: str):
        """تحميل الجدول الزمني للـ Doctor"""
        self.doctor_schedule_table.setRowCount(0)
        schedule = database.get_doctor_schedule(doctor_id)
        
        for i, item in enumerate(schedule):
            self.doctor_schedule_table.insertRow(i)
            self.doctor_schedule_table.setItem(i, 0, QTableWidgetItem(item.get('course_name', '')))
            
            # تنسيق الوقت
            start_time = item.get('start_time', 0)
            end_time = item.get('end_time', 0)
            time_str = f"{start_time}:00 - {end_time}:00"
            self.doctor_schedule_table.setItem(i, 1, QTableWidgetItem(time_str))
            
            self.doctor_schedule_table.setItem(i, 2, QTableWidgetItem(item.get('hall', '')))
            
            # التحقق من التعارضات
            has_conflict = database.check_doctor_time_conflict(
                doctor_id, start_time, end_time, item.get('section_id')
            )
            status = "⚠️ تعارض" if has_conflict else "✅ جيد"
            self.doctor_schedule_table.setItem(i, 3, QTableWidgetItem(status))
    
    def clear_doctor_form(self):
        """تفريغ حقول نموذج Doctor"""
        self.doctor_id_input.clear()
        self.doctor_name_input.clear()
        self.doctor_email_input.clear()
        self.doctor_preferred_courses_input.clear()
        self.doctor_time_availability_input.clear()
        self.assignments_table.setRowCount(0)
        self.doctor_schedule_table.setRowCount(0)

