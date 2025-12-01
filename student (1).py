"""
================================================================================
ملف واجهة الطالب - Student Interface Module (student.py)
================================================================================

الهدف من الملف:
    هذا الملف يحتوي على جميع الواجهات الرسومية (GUI) المتعلقة بالطالب.
    يوفر واجهة كاملة للطالب لعرض المقررات، التسجيل، وعرض الجدول والسجل.

البنية العامة للملف:
    ============================================================================
    1. BaseDashboard Class (كلاس لوحة التحكم الأساسية)
    ============================================================================
    - كلاس أساسي يرث من PyQt6.QWidget
    - يوفر وظائف مشتركة بين جميع لوحات التحكم
    - toggle_theme(): تبديل الوضع الليلي/النهاري
    - handle_signout(): تسجيل الخروج
    
    ============================================================================
    2. StudentDashboard Class (لوحة تحكم الطالب)
    ============================================================================
    - يرث من BaseDashboard
    - الواجهة الرئيسية للطالب
    - المناطق الرئيسية:
        * عرض المقررات المتاحة (create_available_courses_panel)
        * عرض الشعب المتاحة (create_sections_panel)
        * عرض الجدول المسجل (create_schedule_panel)
            - عرض قائمة (List View)
            - عرض أسبوعي ملون (Weekly Timetable View)
    
    ============================================================================
    3. TranscriptDialog Class (نافذة السجل الأكاديمي)
    ============================================================================
    - حوار (Dialog) لعرض السجل الأكاديمي الكامل
    - يعرض المقررات المجتازة وإجمالي الساعات

العلاقات مع الملفات الأخرى:
    - يستورد من:
        * registration_system.py (Student, RegistrationSystem, Course, Section)
        * styles.py (apply_shadow, LIGHT_MODE_QSS, DARK_MODE_QSS)
        * PyQt6 (مكتبة الواجهات الرسومية)
    - يستخدمه:
        * gui.py (MainApp.run() يستخدم StudentDashboard)
        * admin.py (AdminDashboard يرث من BaseDashboard الموجود هنا)
    
التدفق العام:
    1. MainApp.run() ينشئ StudentDashboard بعد تسجيل دخول الطالب
    2. StudentDashboard يعرض المقررات المتاحة باستخدام RegistrationSystem
    3. الطالب يختار مقرر ثم شعبة
    4. System يتحقق من المتطلبات والحدود قبل التسجيل
    5. يتم حفظ التسجيل في قاعدة البيانات عبر RegistrationSystem
    
نظام الوراثة المستخدم:
    ✅ PyQt6.QWidget → BaseDashboard → StudentDashboard
    
المكونات الرئيسية في StudentDashboard:
    - courses_list: قائمة المقررات المتاحة
    - sections_table: جدول الشعب المتاحة
    - schedule_table: جدول المقررات المسجلة
    - weekly_timetable: الجدول الأسبوعي الملون
    
مثال على الاستخدام:
    from registration_system import Student, RegistrationSystem
    from student import StudentDashboard
    
    student = StudentManager().get_student("123456")
    registration_system = RegistrationSystem()
    dashboard = StudentDashboard(student, registration_system)
    dashboard.show()  # عرض واجهة الطالب
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QListWidgetItem, QLabel, QFrame, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QStatusBar, QApplication, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from registration_system import Student, RegistrationSystem_registration_system, Course, Section
from styles import apply_shadow, LIGHT_MODE_QSS, DARK_MODE_QSS


class DashboardBase_QWidget_student(QWidget):
    """
    ============================================================================
    كلاس لوحة التحكم الأساسية - Base Dashboard Class
    ============================================================================
    
    الوظيفة:
        كلاس أساسي لجميع لوحات التحكم في النظام (الطالب والمدير).
        يرث من PyQt6.QWidget ويوفر الوظائف المشتركة بين جميع لوحات التحكم.
        يستخدم نظام الوراثة (Inheritance) لتقليل تكرار الكود.
    
    Visibility (الرموز):
        + public: يمكن الوصول من أي مكان
        _ private: للاستخدام الداخلي فقط
        # protected: للاستخدام من الكلاسات الفرعية
    
    العلاقات والربط:
        - الكلاس الأساسي (Parent Class): PyQt6.QWidget (من مكتبة PyQt6)
        - الكلاسات التي ترث منه:
            * StudentDashboard (في السطر 64) - لوحة تحكم الطالب
            * AdminDashboard (في admin.py السطر 20) - لوحة تحكم المدير
        - يتم استخدامه في:
            * StudentDashboard.__init__() (في السطر 77) - يستدعي super().__init__()
            * AdminDashboard.__init__() (في admin.py السطر 39) - يستدعي super().__init__()
    
    مهامه:
        - توفير وظيفة toggle_theme() لتبديل الوضع الليلي/النهاري
        - توفير وظيفة handle_signout() لتسجيل الخروج
        - تخزين حالة الوضع الليلي (is_dark_mode)
        
    مثال الاستخدام:
        لا يتم استخدامه مباشرة، بل يتم استخدام الكلاسات التي ترث منه.
        StudentDashboard و AdminDashboard يرثان من BaseDashboard.
    """
    
    # + public method
    def __init__(self):
        """تهيئة لوحة التحكم الأساسية"""
        super().__init__()
        # + public attribute
        self.is_dark_mode = False
    
    # + public method
    def toggle_theme(self):
        """
        تبديل الوضع الليلي/النهاري
        وظيفته: تغيير مظهر التطبيق بين الوضع الفاتح والداكن
        """
        app = QApplication.instance()
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            app.setStyleSheet(DARK_MODE_QSS)
            if hasattr(self, 'theme_button'):
                self.theme_button.setText("☀️")
        else:
            app.setStyleSheet(LIGHT_MODE_QSS)
            if hasattr(self, 'theme_button'):
                self.theme_button.setText("🌙")
    
    # + public method
    def handle_signout(self):
        """
        معالجة تسجيل الخروج
        وظيفته: إغلاق الجلسة الحالية والعودة إلى شاشة تسجيل الدخول
        """
        reply = QMessageBox.question(
            self, 'تسجيل الخروج', 'هل أنت متأكد؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            QApplication.instance().exit(100)


class StudentDashboard_DashboardBase_student(DashboardBase_QWidget_student):
    """
    ============================================================================
    كلاس لوحة تحكم الطالب - Student Dashboard Class
    ============================================================================
    
    الوظيفة:
        واجهة المستخدم الرئيسية للطالب في النظام.
    
    Visibility (الرموز):
        + public: يمكن الوصول من أي مكان
        _ private: للاستخدام الداخلي فقط
        # protected: للاستخدام من الكلاسات الفرعية
        يرث من BaseDashboard ويضيف وظائف خاصة بالطالب.
        تتفاعل مع RegistrationSystem لإدارة التسجيل والعرض.
    
    العلاقات والربط:
        - الكلاس الأساسي (Parent Class): BaseDashboard (في السطر 19)
        - الكلاسات التي ترث منه: لا يوجد
        - يتم استخدامه في:
            * gui.py - MainApp.run() (في السطر 309) - يتم إنشاء StudentDashboard للطالب
            * TranscriptDialog (في السطر 540) - يستخدم RegistrationSystem المرتبط به
        - يستخدم الكلاسات التالية:
            * Student (من registration_system) - بيانات الطالب
            * RegistrationSystem (من registration_system) - نظام التسجيل
            * Course, Section (من registration_system) - المقررات والشعب
    
    مهامه:
        - عرض المقررات المتاحة للطالب حسب مستواه وتخصصه (باستخدام LevelBasedCourseFilter)
        - عرض الشعب المتاحة لكل مقرر
        - إدارة التسجيل في المقررات (إضافة/حذف) عبر RegistrationSystem
        - عرض الجدول الأسبوعي للمقررات المسجلة (أسبوعي وقائمة)
        - عرض السجل الأكاديمي للطالب عبر TranscriptDialog
        - التحقق من المتطلبات السابقة والحدود المسموحة قبل التسجيل
        - عرض الساعات المعتمدة المجتازة والمسجلة
        
    مثال الاستخدام:
        student = StudentManager().get_student("123456")
        registration_system = RegistrationSystem()
        dashboard = StudentDashboard(student, registration_system)
        dashboard.show()  # عرض واجهة الطالب
    """
    
    # + public method
    def __init__(self, student: Student, registration_system: RegistrationSystem_registration_system):
        """
        تهيئة لوحة تحكم الطالب
        Args:
            student: كائن الطالب
            registration_system: نظام التسجيل
        """
        super().__init__()
        # + public attribute
        self.student = student
        # + public attribute
        self.registration_system = registration_system
        # قائمة لحفظ عدد الساعات لكل مادة مسجلة
        self.registered_course_credits = []  # List to store credits for each registered course
        
        self.setWindowTitle(f'نظام التسجيل - مرحباً {student.name}')
        self.setGeometry(100, 100, 1200, 700)
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
        
        # شريط تنبيه للساعات المعتمدة
        self.hours_warning_label = QLabel("")
        self.hours_warning_label.setWordWrap(True)
        self.hours_warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hours_warning_label.setStyleSheet(
            "background-color: #dc3545; color: white; font-weight: bold; padding: 10px; "
            "border-radius: 5px; margin: 5px;"
        )
        self.hours_warning_label.setVisible(False)  # مخفي افتراضياً
        layout.addWidget(self.hours_warning_label)
        
        # المحتوى الرئيسي
        main_layout = QHBoxLayout()
        
        # العمود 1: المقررات المتاحة
        courses_frame = self.create_available_courses_panel()
        main_layout.addWidget(courses_frame, 1)
        
        # العمود 2: الشعب
        sections_frame = self.create_sections_panel()
        main_layout.addWidget(sections_frame, 2)
        
        # العمود 3: الجدول المسجل
        schedule_frame = self.create_schedule_panel()
        main_layout.addWidget(schedule_frame, 2)
        
        layout.addLayout(main_layout)
    
    # + public method
    def create_available_courses_panel(self) -> QFrame:
        """
        إنشاء لوحة المقررات المتاحة
        وظيفته: عرض قائمة المقررات المتاحة للطالب حسب مستواه وتخصصه
        Returns:
            إطار يحتوي على قائمة المقررات
        """
        frame = QFrame()
        frame.setProperty("class", "card")
        apply_shadow(frame)
        
        layout = QVBoxLayout(frame)
        
        info_label = QLabel(
            f"الطالب: {self.student.name}\nالبرنامج: {self.student.program} - المستوى {self.student.level}"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # زر المستوى وQComboBox لعرض المقررات حسب المستوى
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel('المستوى:'))
        self.level_combo = QComboBox()
        self.level_combo.addItems([str(i) for i in range(1, 11)])  # المستويات من 1 إلى 10
        self.level_combo.setCurrentText(str(self.student.level))  # تعيين مستوى الطالب الحالي كافتراضي
        self.level_combo.currentTextChanged.connect(self.on_level_changed)
        level_layout.addWidget(self.level_combo)
        level_layout.addStretch()
        layout.addLayout(level_layout)
        
        layout.addWidget(QLabel('الخطوة 1: اختر مادة'))
        
        self.courses_list = QListWidget()
        self.courses_list.currentItemChanged.connect(self.on_course_selected)
        layout.addWidget(self.courses_list)
        
        # زر التحديث
        refresh_button = QPushButton('🔄 تحديث قائمة المقررات')
        refresh_button.setProperty("class", "secondary")
        refresh_button.clicked.connect(self.load_data)
        layout.addWidget(refresh_button)
        
        return frame
    
    def create_sections_panel(self) -> QFrame:
        """
        إنشاء لوحة الشعب
        وظيفته: عرض الشعب المتاحة للمقرر المحدد
        Returns:
            إطار يحتوي على جدول الشعب
        """
        frame = QFrame()
        frame.setProperty("class", "card")
        apply_shadow(frame)
        
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel('الخطوة 2: اختر شعبة'))
        
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(6)
        self.sections_table.setHorizontalHeaderLabels(
            ['المدرس', 'الوقت', 'القاعة', 'السعة', 'المسجلين', 'ID']
        )
        self.sections_table.setColumnHidden(5, True)
        self.sections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sections_table)
        
        self.add_button = QPushButton('إضافة الشعبة المحددة')
        self.add_button.clicked.connect(self.handle_add_section)
        layout.addWidget(self.add_button)
        
        return frame
    
    def create_schedule_panel(self) -> QFrame:
        """
        إنشاء لوحة الجدول المسجل
        وظيفته: عرض المقررات المسجلة في جدول أسبوعي مرئي
        Returns:
            إطار يحتوي على الجدول الأسبوعي
        """
        frame = QFrame()
        frame.setProperty("class", "card")
        apply_shadow(frame)
        
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel('جدولي الحالي'))
        
        # تبويبات للعرض القائمة والجدول الأسبوعي
        schedule_tabs = QTabWidget()
        
        # التبويب 1: عرض القائمة
        list_tab = QWidget()
        list_layout = QVBoxLayout(list_tab)
        
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels(
            ['المادة', 'المدرس', 'الوقت', 'القاعة', 'الساعات', 'ID']
        )
        self.schedule_table.setColumnHidden(5, True)
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        list_layout.addWidget(self.schedule_table)
        
        schedule_tabs.addTab(list_tab, "القائمة")
        
        # التبويب 2: الجدول الأسبوعي
        timetable_tab = QWidget()
        timetable_layout = QVBoxLayout(timetable_tab)
        
        self.weekly_timetable = QTableWidget()
        self.weekly_timetable.setColumnCount(6)  # الأحد إلى الخميس + السبت
        self.weekly_timetable.setRowCount(14)  # من 8:00 إلى 21:00 (14 ساعة)
        self.weekly_timetable.setHorizontalHeaderLabels(
            ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'السبت']
        )
        
        # تسميات الأوقات للصفوف (8:00 إلى 21:00)
        time_labels = []
        for hour in range(8, 22):
            time_labels.append(f"{hour}:00 - {hour+1}:00")
        
        self.weekly_timetable.setVerticalHeaderLabels(time_labels)
        self.weekly_timetable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.weekly_timetable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.weekly_timetable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.weekly_timetable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        
        timetable_layout.addWidget(QLabel('الجدول الأسبوعي'))
        timetable_layout.addWidget(self.weekly_timetable)
        
        schedule_tabs.addTab(timetable_tab, "الجدول الأسبوعي")
        
        layout.addWidget(schedule_tabs)
        
        # تسميات الساعات
        hours_layout = QHBoxLayout()
        self.passed_hours_label = QLabel("الساعات المجتازة: 0")
        self.registered_hours_label = QLabel("الساعات المسجلة: 0")
        self.total_hours_label = QLabel("الإجمالي: 0")
        
        hours_layout.addWidget(self.passed_hours_label)
        hours_layout.addWidget(self.registered_hours_label)
        hours_layout.addWidget(self.total_hours_label)
        layout.addLayout(hours_layout)
        
        # منطقة رسائل التحقق
        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px;")
        layout.addWidget(self.validation_label)
        
        # الأزرار
        buttons_layout = QHBoxLayout()
        self.remove_button = QPushButton('حذف الشعبة المحددة')
        self.remove_button.setProperty("class", "danger")
        self.remove_button.clicked.connect(self.handle_remove_section)
        
        self.transcript_button = QPushButton('عرض السجل الأكاديمي')
        self.transcript_button.setProperty("class", "secondary")
        self.transcript_button.clicked.connect(self.show_transcript)
        
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.transcript_button)
        layout.addLayout(buttons_layout)
        
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
        return frame
    
    def load_data(self):
        """تحميل جميع البيانات في الواجهة"""
        self.registration_system.refresh_cache()
        self.load_available_courses()
        self.load_registered_schedule()
        self.update_hours_display()
    
    def on_level_changed(self, level_text: str):
        """معالجة تغيير المستوى المختار"""
        if level_text:
            level = int(level_text)
            self.load_available_courses_for_level(level)
    
    def load_available_courses(self):
        """تحميل المقررات المتاحة للطالب (باستخدام المستوى الحالي من القائمة المنسدلة)"""
        level_text = self.level_combo.currentText()
        if level_text:
            level = int(level_text)
            self.load_available_courses_for_level(level)
        else:
            self.load_available_courses_for_level(self.student.level)
    
    def load_available_courses_for_level(self, level: int):
        """تحميل المقررات المتاحة لبرنامج ومستوى محدد"""
        self.courses_list.clear()
        available_courses = self.registration_system.get_available_courses(
            self.student.program, level
        )
        
        for course in available_courses:
            item = QListWidgetItem(f"{course.course_code} - {course.name}")
            item.setData(Qt.ItemDataRole.UserRole, course.course_code)
            self.courses_list.addItem(item)
    
    def load_registered_schedule(self):
        """تحميل الجدول المسجل للطالب"""
        self.schedule_table.setRowCount(0)
        # تحديث قائمة الساعات المعتمدة
        self.registered_course_credits = []
        
        for i, registration in enumerate(self.student.schedule):
            section_id = registration.get('id')
            section = self.registration_system.get_section(section_id)
            if not section:
                continue
            
            course = self.registration_system.get_course(section.course_code)
            if not course:
                continue
            
            # إضافة عدد الساعات إلى القائمة
            self.registered_course_credits.append(course.credits)
            
            self.schedule_table.insertRow(i)
            self.schedule_table.setItem(i, 0, QTableWidgetItem(course.course_code))
            self.schedule_table.setItem(i, 1, QTableWidgetItem(section.instructor))
            self.schedule_table.setItem(i, 2, QTableWidgetItem(f"{section.start_time}:00 - {section.end_time}:00"))
            self.schedule_table.setItem(i, 3, QTableWidgetItem(section.hall))
            self.schedule_table.setItem(i, 4, QTableWidgetItem(str(course.credits)))
            self.schedule_table.setItem(i, 5, QTableWidgetItem(section_id))
        
        # تحديث الجدول الأسبوعي
        self.update_weekly_timetable()
    
    def update_weekly_timetable(self):
        """
        تحديث الجدول الأسبوعي المرئي
        وظيفته: عرض المقررات المسجلة في جدول أسبوعي مع تلوين مختلف لكل مقرر
        """
        # مسح الجدول
        for row in range(self.weekly_timetable.rowCount()):
            for col in range(self.weekly_timetable.columnCount()):
                self.weekly_timetable.setItem(row, col, None)
        
        # لوحة ألوان للمقررات المختلفة
        colors = [
            QColor(173, 216, 230),  # أزرق فاتح
            QColor(144, 238, 144),  # أخضر فاتح
            QColor(255, 182, 193),  # وردي فاتح
            QColor(221, 160, 221),  # بنفسجي
            QColor(255, 218, 185),  # خوخي
            QColor(176, 224, 230),  # أزرق باهت
            QColor(255, 228, 196),  # بيج
        ]
        
        course_colors = {}
        color_index = 0
        
        # ملء الجدول بالشعب المسجلة
        for registration in self.student.schedule:
            section_id = registration.get('id')
            section = self.registration_system.get_section(section_id)
            if not section:
                continue
            
            course = self.registration_system.get_course(section.course_code)
            if not course:
                continue
            
            # تعيين لون للمقرر
            if course.course_code not in course_colors:
                course_colors[course.course_code] = colors[color_index % len(colors)]
                color_index += 1
            
            color = course_colors[course.course_code]
            
            # العثور على صف الوقت (8:00 = صف 0، 9:00 = صف 1، إلخ)
            start_row = section.start_time - 8
            end_row = section.end_time - 8
            
            # تحليل أيام الأسبوع من section.days
            days_str = section.days or ''
            if days_str:
                # تحويل أيام الأسبوع إلى أعمدة
                day_to_column = {
                    'الأحد': 0,
                    'الإثنين': 1,
                    'الثلاثاء': 2,
                    'الأربعاء': 3,
                    'الخميس': 4,
                    'السبت': 5
                }
                
                # تقسيم الأيام (مفصولة بفواصل)
                days_list = [day.strip() for day in days_str.split(',') if day.strip()]
                
                # ملء الجدول لكل يوم
                for day_name in days_list:
                    if day_name in day_to_column:
                        day_column = day_to_column[day_name]
                        
                        # ملء فترات الوقت لهذه الشعبة في هذا اليوم
                        for row in range(start_row, end_row):
                            if 0 <= row < self.weekly_timetable.rowCount():
                                item = QTableWidgetItem(
                                    f"{course.course_code}\n{section.instructor}\n{section.hall}"
                                )
                                item.setBackground(QBrush(color))
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                self.weekly_timetable.setItem(row, day_column, item)
            else:
                # إذا لم تكن هناك أيام محددة، نضعها في الأحد (للتوافق مع البيانات القديمة)
                day_column = 0
                for row in range(start_row, end_row):
                    if 0 <= row < self.weekly_timetable.rowCount():
                        item = QTableWidgetItem(
                            f"{course.course_code}\n{section.instructor}\n{section.hall}"
                        )
                        item.setBackground(QBrush(color))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.weekly_timetable.setItem(row, day_column, item)
    
    def update_hours_display(self):
        """تحديث عرض الساعات المعتمدة"""
        passed = self.student.get_completed_credits_registration_system(self.registration_system)
        # حساب الساعات المسجلة من القائمة
        registered = sum(self.registered_course_credits)
        total = passed + registered
        
        self.passed_hours_label.setText(f"الساعات المجتازة: {passed}")
        self.registered_hours_label.setText(f"الساعات المسجلة: {registered}")
        self.total_hours_label.setText(f"الإجمالي: {total}")
        
        # التحقق من الساعات المسجلة وعرض/إخفاء شريط التنبيه
        if registered < 12:
            # عرض شريط تنبيه أحمر إذا كان أقل من 12
            self.hours_warning_label.setText(
                f"⚠️ تحذير: عدد الساعات المسجلة ({registered}) أقل من الحد الأدنى المطلوب (12 ساعة)"
            )
            self.hours_warning_label.setVisible(True)
        elif registered >= 12 and registered <= 18:
            # إخفاء شريط التنبيه إذا كان بين 12 و 18
            self.hours_warning_label.setVisible(False)
        # إذا كان أكثر من 18، سيتم منع الإضافة في handle_add_section
    
    def on_course_selected(self, current, previous):
        """
        معالجة اختيار المقرر
        وظيفته: عرض الشعب المتاحة للمقرر المحدد
        """
        if not current:
            return
        
        course_code = current.data(Qt.ItemDataRole.UserRole)
        sections = [
            s for s in self.registration_system._section_cache.values()
            if s.course_code == course_code
        ]
        
        self.sections_table.setRowCount(0)
        for i, section in enumerate(sections):
            self.sections_table.insertRow(i)
            self.sections_table.setItem(i, 0, QTableWidgetItem(section.instructor))
            self.sections_table.setItem(i, 1, QTableWidgetItem(f"{section.start_time}:00 - {section.end_time}:00"))
            self.sections_table.setItem(i, 2, QTableWidgetItem(section.hall))
            self.sections_table.setItem(i, 3, QTableWidgetItem(str(section.max_capacity)))
            self.sections_table.setItem(i, 4, QTableWidgetItem(str(section.current_enrollment)))
            self.sections_table.setItem(i, 5, QTableWidgetItem(section.section_id))
    
    def handle_add_section(self):
        """
        معالجة إضافة شعبة
        وظيفته: تسجيل الطالب في شعبة مع التحقق من جميع القيود
        مهامه:
        - التحقق من المتطلبات السابقة
        - التحقق من حدود الساعات المعتمدة
        - التحقق من تعارض الأوقات
        - التحقق من سعة الشعبة
        """
        row = self.sections_table.currentRow()
        if row == -1:
            self.validation_label.setText("⚠️ الرجاء اختيار شعبة أولاً")
            self.validation_label.setStyleSheet("color: #ffc107; font-weight: bold; padding: 5px;")
            return
        
        section_id = self.sections_table.item(row, 5).text()
        section = self.registration_system.get_section(section_id)
        if not section:
            self.validation_label.setText("⚠️ الشعبة المحددة غير موجودة")
            self.validation_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px;")
            return
        
        # التحقق الفوري قبل التسجيل
        course_code = section.course_code
        validation_errors = []
        
        # 1. التحقق من أن المادة غير موجودة في السجل الأكاديمي (لم يتم اجتيازها مسبقاً)
        if course_code in self.student.transcript:
            validation_errors.append(
                f"المقرر {course_code} موجود في السجل الأكاديمي (تم اجتيازه مسبقاً). "
                f"لا يمكن التسجيل في مقرر تم اجتيازه"
            )
        
        # 2. التحقق من المتطلبات السابقة
        course = self.registration_system.get_course(course_code)
        if course and course.prerequisites:
            prereqs_met, missing = course.check_prerequisites_transcript(self.student.transcript)
            if not prereqs_met:
                validation_errors.append(f"متطلبات سابقة غير مستوفاة: {', '.join(missing)}")
        
        # 3. التحقق من أن الطالب لم يسجل في نفس المقرر مسبقاً
        for reg in self.student.schedule:
            existing_section = self.registration_system.get_section(reg.get('id'))
            if existing_section and existing_section.course_code == course_code:
                validation_errors.append(
                    f"مسجل بالفعل في المقرر {course_code} (الشعبة: {existing_section.section_id}). "
                    f"لا يمكن التسجيل في نفس المقرر مرتين في نفس الترم"
                )
                break
        
        # 4. التحقق من حدود الساعات المعتمدة (الحد الأقصى 18)
        current_registered_hours = sum(self.registered_course_credits)
        if course:
            new_total = current_registered_hours + course.credits
            if new_total > 18:
                validation_errors.append(
                    f"تجاوز الحد الأقصى: إضافة هذه المادة ({course.credits} ساعة) "
                    f"ستجعل مجموع الساعات ({new_total}) يتجاوز الحد الأقصى المسموح (18 ساعة)"
                )
        
        # 5. التحقق من تعارض الأوقات
        for reg in self.student.schedule:
            existing_section = self.registration_system.get_section(reg.get('id'))
            if existing_section and section.has_time_conflict_section(existing_section):
                validation_errors.append(f"تعارض في الوقت مع {existing_section.section_id}")
        
        # 4. التحقق من السعة
        if section.is_full():
            validation_errors.append(f"الشعبة {section_id} ممتلئة")
        
        # عرض أخطاء التحقق إن وجدت
        if validation_errors:
            error_msg = "❌ " + " | ".join(validation_errors)
            self.validation_label.setText(error_msg)
            self.validation_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px;")
            return
        
        # مسح رسالة التحقق إذا لم تكن هناك أخطاء
        self.validation_label.setText("")
        
        # المتابعة مع التسجيل
        success, message = self.registration_system.register_student_database_registration_system(
            self.student, [section_id]
        )
        
        if success:
            self.status_bar.showMessage(message, 3000)
            self.validation_label.setText("✅ تم التسجيل بنجاح")
            self.validation_label.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px;")
            self.load_data()  # هذا سيحدث القائمة وعرض الساعات وشريط التنبيه
        else:
            self.validation_label.setText(f"❌ {message}")
            self.validation_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px;")
            QMessageBox.warning(self, 'خطأ', message)
    
    def handle_remove_section(self):
        """معالجة حذف شعبة (إلغاء التسجيل)"""
        row = self.schedule_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'تحذير', 'الرجاء اختيار شعبة أولاً')
            return
        
        section_id = self.schedule_table.item(row, 5).text()
        success, message = self.registration_system.unregister_student_database_registration_system(
            self.student, section_id
        )
        
        if success:
            self.status_bar.showMessage(message, 3000)
            self.validation_label.setText("")  # مسح رسالة التحقق
            self.load_data()  # هذا سيحدث القائمة وعرض الساعات وشريط التنبيه
        else:
            QMessageBox.warning(self, 'خطأ', message)
    
    def show_transcript(self):
        """عرض نافذة السجل الأكاديمي"""
        dialog = TranscriptDialog(self.student, self.registration_system, self)
        dialog.exec()


class TranscriptDialog(QDialog):
    """
    كلاس نافذة السجل الأكاديمي - Transcript Dialog Class
    وظيفته: عرض السجل الأكاديمي الكامل للطالب
    مهامه:
    - عرض جميع المقررات المجتازة
    - عرض الساعات المعتمدة لكل مقرر
    - حساب إجمالي الساعات المجتازة
    """
    
    def __init__(self, student: Student, registration_system: RegistrationSystem_registration_system, parent=None):
        """
        تهيئة نافذة السجل الأكاديمي
        Args:
            student: كائن الطالب
            registration_system: نظام التسجيل
            parent: النافذة الأم
        """
        super().__init__(parent)
        self.student = student
        self.registration_system = registration_system
        
        self.setWindowTitle(f'السجل الأكاديمي - {student.name}')
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout(self)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['رمز المادة', 'اسم المادة', 'الساعات'])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        total_hours = 0
        for i, course_code in enumerate(student.transcript):
            course = registration_system.get_course(course_code)
            if course:
                table.insertRow(i)
                table.setItem(i, 0, QTableWidgetItem(course.course_code))
                table.setItem(i, 1, QTableWidgetItem(course.name))
                table.setItem(i, 2, QTableWidgetItem(str(course.credits)))
                total_hours += course.credits
        
        layout.addWidget(table)
        
        total_label = QLabel(f"إجمالي الساعات المجتازة: {total_hours}")
        total_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(total_label)

