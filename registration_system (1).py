"""
================================================================================
ملف النظام الأساسي - Registration System Module (registration_system.py)
================================================================================

الهدف من الملف:
    هذا الملف يحتوي على جميع الكلاسات الأساسية والنماذج (Models) والمنطق
    الأساسي للنظام. يعتبر القلب النابض للتطبيق حيث يحتوي على:
    - نماذج البيانات (Data Models): Course, Student, Section, User
    - كلاسات التحقق (Validators): BaseValidator, LevelValidator
    - كلاسات المستخدمين (Users): BaseUser, StudentUser, AdminUser
    - نظام التسجيل (RegistrationSystem)
    - إدارة المستخدمين (UserManager, StudentManager)
    - نظام المصادقة والجلسات (PasswordHasher, SessionManager, AccessLogger)

البنية العامة للملف:
    ============================================================================
    1. VALIDATION CLASSES (كلاسات التحقق)
    ============================================================================
    - BaseValidator: كلاس أساسي لجميع المدققات
    - LevelValidator: يتحقق من صحة مستوى الطالب (يرث من BaseValidator)
    
    ============================================================================
    2. DOMAIN MODEL CLASSES (نماذج البيانات)
    ============================================================================
    - Course: يمثل مقرر دراسي (course_code, name, credits, prerequisites)
    - Student: يمثل طالب (student_id, name, program, level, transcript, schedule)
    - Section: يمثل شعبة لمقرر (section_id, instructor, time, hall, capacity)
    - User: يمثل مستخدم في النظام (user_id, email, role, password)
    
    ============================================================================
    3. USER CLASSES WITH INHERITANCE (كلاسات المستخدمين مع الوراثة)
    ============================================================================
    - BaseUser: كلاس أساسي لجميع المستخدمين (Abstract Base Class)
    - StudentUser: يمثل مستخدم طالب (يرث من BaseUser)
    - AdminUser: يمثل مستخدم مدير (يرث من BaseUser)
    
    ============================================================================
    4. PASSWORD & SECURITY (الأمان وكلمات المرور)
    ============================================================================
    - PasswordValidator: يتحقق من قوة كلمة المرور
    - PasswordHasher: يشفر كلمات المرور
    - SessionManager: يدير الجلسات والرموز (Tokens)
    - AccessLogger: يسجل محاولات الدخول والأحداث
    
    ============================================================================
    5. REGISTRATION SYSTEM (نظام التسجيل)
    ============================================================================
    - RegistrationSystem: النظام الرئيسي للتسجيل وإدارة المقررات
    
    ============================================================================
    6. USER MANAGEMENT (إدارة المستخدمين)
    ============================================================================
    - UserManager: يدير المستخدمين والمصادقة
    - StudentManager: يدير بيانات الطلاب
    
العلاقات مع الملفات الأخرى:
    - يستورد من: database.py (لعمليات قاعدة البيانات)
    - يستخدمه: 
        * gui.py (للأدوات والكلاسات الأساسية)
        * student.py (StudentDashboard يستخدم RegistrationSystem)
        * admin.py (AdminDashboard يستخدم RegistrationSystem)
    
التدفق العام:
    1. UserManager يتحقق من المستخدمين ويستخدم PasswordHasher, SessionManager
    2. RegistrationSystem يدير المقررات والشعب باستخدام database.py
    3. StudentManager يدير بيانات الطلاب من قاعدة البيانات
    4. الكلاسات المختلفة تستخدم الوراثة لتقليل التكرار
    
نظام الوراثة المستخدم:
    ✅ BaseValidator → LevelValidator
    ✅ BaseUser → StudentUser, AdminUser
    
مثال على الاستخدام:
    # إنشاء نظام التسجيل
    registration_system = RegistrationSystem()
    
    # إنشاء مدير المستخدمين
    user_manager = UserManager()
    
    # التحقق من المستخدم
    user = user_manager.authenticate("123456", "password")
    
    # الحصول على المقررات المتاحة
    courses = registration_system.get_available_courses("Computer", 1)
"""

import sqlite3
import hashlib
import secrets
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import database 
from database import get_connection, get_courses_for_program_and_level


# ============================================================================
# VALIDATION CLASSES (OOP Design with Inheritance)
# ============================================================================

class ValidatorBase_registration_system:
    """
    ============================================================================
    كلاس المدقق الأساسي - Base Validator Class
    ============================================================================
    
    الوظيفة:
        كلاس أساسي (Abstract Base Class) لجميع المدققات في النظام.
        يستخدم نظام الوراثة (Inheritance) لتوفير واجهة موحدة للتحقق من صحة البيانات.
    
    Visibility (الرموز):
        + public: يمكن الوصول من أي مكان
        _ private: للاستخدام الداخلي فقط
        # protected: للاستخدام من الكلاسات الفرعية
    
    العلاقات والربط:
        - الكلاس الأساسي: لا يرث من أي كلاس (Base Class للتحقق)
        - الكلاسات التي ترث منه:
            * LevelValidator (في السطر 33) - يتحقق من صحة مستوى الطالب
        - يتم استخدامه في: 
            * LevelValidator (في السطر 33) - يرث جميع الوظائف الأساسية
            * Student.__post_init__() (في السطر 125) - يستخدم LevelValidator للتحقق من مستوى الطالب
    
    مهامه:
        - توفير دالة validate() يجب أن تطبقها جميع الكلاسات الفرعية
        - تحديد واجهة موحدة للتحقق من صحة البيانات
        
    الاستخدام:
        لا يتم استخدامه مباشرة، بل يتم استخدام الكلاسات التي ترث منه.
        مثال: LevelValidator يرث من BaseValidator ويمثل تحقق محدد.
    """
    
    # # protected method (يجب تطبيقه في الكلاسات الفرعية)
    def validate(self, value) -> Tuple[bool, str]:
        """Validate value - to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement validate()")


class LevelValidator_ValidatorBase_registration_system(ValidatorBase_registration_system):
    """
    ============================================================================
    كلاس التحقق من المستوى - Level Validator Class
    ============================================================================
    
    الوظيفة:
        كلاس متخصص للتحقق من صحة مستوى الطالب (يجب أن يكون بين 1 و 10).
        يرث من BaseValidator ويطبق دالة validate() للتحقق من المستوى.
    
    Visibility (الرموز):
        + public: يمكن الوصول من أي مكان
        _ private: للاستخدام الداخلي فقط
        # protected: للاستخدام من الكلاسات الفرعية
    
    العلاقات والربط:
        - الكلاس الأساسي (Parent Class): BaseValidator (في السطر 22)
        - الكلاسات التي ترث منه: لا يوجد
        - يتم استخدامه في:
            * Student.__post_init__() (في السطر 125) - للتحقق من صحة مستوى الطالب
            * LevelValidator() يتم إنشاء مثيل منه داخل Student.__post_init__()
    
    مهامه:
        - التحقق من أن المستوى هو رقم صحيح (integer)
        - التحقق من أن المستوى بين 1 و 10
        - إرجاع رسالة خطأ واضحة إذا كان المستوى غير صحيح
        
    مثال الاستخدام:
        level_validator = LevelValidator_ValidatorBase_registration_system()
        is_valid, error_msg = level_validator.validate(5)  # True, "Level is valid"
        is_valid, error_msg = level_validator.validate(15)  # False, "Level must be at most 10"
    """
    
    MIN_LEVEL = 1
    MAX_LEVEL = 10
    
    def validate(self, level: int) -> Tuple[bool, str]:
        """
        Validate student level.
        Returns: (is_valid: bool, error_message: str)
        """
        if not isinstance(level, int):
            return False, "Level must be an integer"
        
        if level < self.MIN_LEVEL:
            return False, f"Level must be at least {self.MIN_LEVEL}"
        
        if level > self.MAX_LEVEL:
            return False, f"Level must be at most {self.MAX_LEVEL}"
        
        return True, "Level is valid"


# ============================================================================
# DOMAIN MODEL CLASSES (As specified in project requirements)
# ============================================================================

@dataclass
class Course:
    """
    Course Class as per project requirements
    Attributes: course_code, name, credits, lecture_hours, lab_hours, 
                prerequisites (list)
    Methods: check_prerequisites(student_transcript)
    
    ملاحظة: max_capacity لم يعد موجوداً في المقررات، السعة متاحة فقط في الشعب (Section)
    """
    course_code: str
    name: str
    credits: int
    lecture_hours: int
    lab_hours: int
    prerequisites: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate course data on creation."""
        if self.credits <= 0:
            raise ValueError("Credit hours must be positive")
        if self.lecture_hours < 0:
            raise ValueError("Lecture hours cannot be negative")
        if self.lab_hours < 0:
            raise ValueError("Lab hours cannot be negative")
    
    def check_prerequisites_transcript(self, student_transcript: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if all prerequisites are met.
        Returns: (prerequisites_met: bool, missing_prerequisites: List[str])
        """
        missing = [prereq for prereq in self.prerequisites 
                   if prereq not in student_transcript]
        return len(missing) == 0, missing


@dataclass
class Student:
    """
    Student Class as per project requirements
    Attributes: student_id, name, email, program, level, 
                transcript (list of completed courses)
    Methods: get_completed_credits(), add_to_transcript(course)
    """
    student_id: str
    name: str
    email: str
    program: str
    level: int
    transcript: List[str] = field(default_factory=list)
    schedule: List[Dict] = field(default_factory=list)  # Registered sections
    
    def __post_init__(self):
        """Validate student data on creation."""
        allowed_programs = ['Computer', 'Comm', 'Communications', 'Power', 'Biomedical']
        if self.program not in allowed_programs:
            raise ValueError(f"Invalid program: {self.program}")
        
        # Validate level using OOP validator
        level_validator = LevelValidator_ValidatorBase_registration_system()
        is_valid, error_msg = level_validator.validate(self.level)
        if not is_valid:
            raise ValueError(error_msg)
    
    def get_completed_credits_registration_system(self, registration_system: 'RegistrationSystem') -> int:
        """Calculate total credits from completed courses."""
        total = 0
        for course_code in self.transcript:
            course = registration_system.get_course(course_code)
            if course:
                total += course.credits
        return total
    
    def add_to_transcript(self, course_code: str):
        """Add a course to the transcript."""
        if course_code not in self.transcript:
            self.transcript.append(course_code)


@dataclass
class Section:
    """Represents a specific section of a course."""
    section_id: str
    course_code: str
    instructor: str
    start_time: int
    end_time: int
    hall: str
    max_capacity: int
    current_enrollment: int = 0
    days: str = ''  # أيام الأسبوع (مثل: "الأحد,الثلاثاء,الخميس")
    
    def is_full(self) -> bool:
        """Check if section is at capacity."""
        return self.current_enrollment >= self.max_capacity
    
    def has_time_conflict_section(self, other: 'Section') -> bool:
        """Check if this section conflicts with another section's time."""
        return not (self.end_time <= other.start_time or 
                    self.start_time >= other.end_time)


# ============================================================================
# USER CLASSES WITH INHERITANCE (OOP Design)
# ============================================================================

class UserBase_registration_system:
    """
    ============================================================================
    كلاس المستخدم الأساسي - Base User Class
    ============================================================================
    
    الوظيفة:
        كلاس أساسي (Abstract Base Class) لجميع أنواع المستخدمين في النظام.
        يستخدم نظام الوراثة (Inheritance) لتمييز صلاحيات المستخدمين بناءً على دورهم.
    
    Visibility (الرموز):
        + public: يمكن الوصول من أي مكان
        _ private: للاستخدام الداخلي فقط
        # protected: للاستخدام من الكلاسات الفرعية
    
    العلاقات والربط:
        - الكلاس الأساسي: لا يرث من أي كلاس (Base Class للمستخدمين)
        - الكلاسات التي ترث منه:
            * StudentUser (في السطر 195) - يمثل مستخدم طالب
            * AdminUser (في السطر 216) - يمثل مستخدم مدير
        - يتم استخدامه في:
            * User.to_user_object() (في السطر 249) - يحول User إلى BaseUser
            * UserManager.authenticate() (في السطر 923) - يرجع BaseUser بعد المصادقة
    
    مهامه:
        - تخزين البيانات الأساسية للمستخدم (user_id, email, password_hash)
        - توفير دالة get_role() لتحديد نوع المستخدم (يجب تطبيقها في الكلاسات الفرعية)
        - توفير دالة has_permission() للتحقق من الصلاحيات
        
    الاستخدام:
        لا يتم استخدامه مباشرة، بل يتم استخدام الكلاسات التي ترث منه (StudentUser, AdminUser).
        يتم الوصول إليه عبر User.to_user_object() الذي يحول User dataclass إلى BaseUser object.
    """
    
    def __init__(self, user_id: str, email: str, password_hash: str, 
                 display_name: str = "", mobile: str = ""):
        """Initialize base user."""
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.display_name = display_name
        self.mobile = mobile
    
    def get_role(self) -> str:
        """Get user role - to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement get_role()")
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return False


class StudentUser_UserBase_registration_system(UserBase_registration_system):
    """
    ============================================================================
    كلاس مستخدم الطالب - Student User Class
    ============================================================================
    
    الوظيفة:
        كلاس يمثل مستخدم طالب في النظام. يرث من BaseUser ويطبق الصلاحيات المخصصة للطلاب.
    
    العلاقات والربط:
        - الكلاس الأساسي (Parent Class): BaseUser (في السطر 171)
        - الكلاسات التي ترث منه: لا يوجد
        - يتم استخدامه في:
            * User.to_user_object() (في السطر 255) - عندما يكون role == 'student'
            * UserManager.authenticate() (في السطر 923) - يرجع StudentUser بعد المصادقة الناجحة
            * gui.py - MainApp.run() (في السطر 303) - للتحقق من نوع المستخدم
    
    مهامه:
        - تمثيل مستخدم طالب مع صلاحيات محددة
        - إرجاع 'student' كدور
        - السماح بالصلاحيات: ['view_courses', 'register_courses', 'view_transcript']
        - رفض جميع الصلاحيات الأخرى
        
    مثال الاستخدام:
        student_user = StudentUser(user_id="123", email="s@test.com", password_hash="...")
        role = student_user.get_role()  # 'student'
        can_view = student_user.has_permission('view_courses')  # True
        can_delete = student_user.has_permission('delete_courses')  # False
    """
    
    def __init__(self, user_id: str, email: str, password_hash: str, 
                 display_name: str = "", mobile: str = ""):
        """Initialize student user."""
        super().__init__(user_id, email, password_hash, display_name, mobile)
    
    def get_role(self) -> str:
        """Get student role."""
        return 'student'
    
    def has_permission(self, permission: str) -> bool:
        """Check student permissions."""
        student_permissions = ['view_courses', 'register_courses', 'view_transcript']
        return permission in student_permissions


class AdminUser_UserBase_registration_system(UserBase_registration_system):
    """
    ============================================================================
    كلاس مستخدم المدير - Admin User Class
    ============================================================================
    
    الوظيفة:
        كلاس يمثل مستخدم مدير في النظام. يرث من BaseUser ويملك جميع الصلاحيات.
    
    العلاقات والربط:
        - الكلاس الأساسي (Parent Class): BaseUser (في السطر 171)
        - الكلاسات التي ترث منه: لا يوجد
        - يتم استخدامه في:
            * User.to_user_object() (في السطر 252) - عندما يكون role == 'admin'
            * UserManager.authenticate() (في السطر 923) - يرجع AdminUser بعد المصادقة الناجحة
            * gui.py - MainApp.run() (في السطر 319) - للتحقق من نوع المستخدم
            * admin.py - AdminDashboard.__init__() (في السطر 32) - يستقبل AdminUser
    
    مهامه:
        - تمثيل مستخدم مدير مع جميع الصلاحيات
        - إرجاع 'admin' كدور
        - السماح بجميع الصلاحيات (دالة has_permission() ترجع دائماً True)
        
    مثال الاستخدام:
        admin_user = AdminUser(user_id="admin", email="admin@test.com", password_hash="...")
        role = admin_user.get_role()  # 'admin'
        can_delete = admin_user.has_permission('delete_courses')  # True (جميع الصلاحيات)
        can_manage = admin_user.has_permission('manage_students')  # True (جميع الصلاحيات)
    """
    
    def __init__(self, user_id: str, email: str, password_hash: str, 
                 display_name: str = "", mobile: str = ""):
        """Initialize admin user."""
        super().__init__(user_id, email, password_hash, display_name, mobile)
    
    def get_role(self) -> str:
        """Get admin role."""
        return 'admin'
    
    def has_permission(self, permission: str) -> bool:
        """Check admin permissions - admins have all permissions."""
        return True


@dataclass
class User:
    """
    User class for authentication and access control.
    Compatibility wrapper that uses role-based classes.
    """
    user_id: str
    email: str
    password_hash: str
    role: str  # 'student' or 'admin'
    display_name: str = ""
    mobile: str = ""
    
    def to_user_object_userbase_registration_system(self) -> UserBase_registration_system:
        """Convert to appropriate user type object."""
        if self.role == 'admin':
            return AdminUser_UserBase_registration_system(self.user_id, self.email, self.password_hash, 
                           self.display_name, self.mobile)
        else:
            return StudentUser_UserBase_registration_system(self.user_id, self.email, self.password_hash, 
                             self.display_name, self.mobile)
    
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == 'admin'
    
    def is_student(self) -> bool:
        """Check if user is a student."""
        return self.role == 'student'


# ============================================================================
# REGISTRATION SYSTEM CLASS (As specified in project requirements)
# ============================================================================

class RegistrationSystem_registration_system:
    """
    RegistrationSystem Class as per project requirements
    Attributes: SQLite database connection and cursor
    Methods: validate_schedule(student, selected_courses),
             register_student(student, course_list),
             add_course(course),
             get_available_courses(program, level)
    
    Visibility (الرموز):
        + public: يمكن الوصول من أي مكان
        _ private: للاستخدام الداخلي فقط
        # protected: للاستخدام من الكلاسات الفرعية
    """
    
    # + public method
    def __init__(self):
        """
        تهيئة نظام التسجيل.
        
        المهام:
            1. إنشاء التخزين المؤقت (Cache) للمقررات والشعب
            2. تحميل البيانات من قاعدة البيانات
            
        ملاحظات:
            - لا نستخدم اتصال دائم بقاعدة البيانات (كل عملية لها اتصال منفصل)
            - هذا يحسن الأداء ويقلل مشاكل الاتصال والتداخل (Multi-threading)
        
        الربط:
            - يستخدم database.fetch_courses_with_sections() (من database.py) لجلب البيانات
            - يستخدم database.get_courses_for_program_and_level() لتصفية المقررات حسب البرنامج والمستوى
        """
        # التخزين المؤقت للمقررات والشعب (Cache)
        # يتم تحميله من قاعدة البيانات عند الإنشاء وعند التحديث
        # _ private attribute
        self._course_cache: Dict[str, Course] = {}
        # _ private attribute
        self._section_cache: Dict[str, Section] = {}
        
        # ملاحظة: تم إزالة حدود الساعات المعتمدة - الطلاب يمكنهم التسجيل لأي عدد من الساعات
        
        # تحميل جميع المقررات والشعب من قاعدة البيانات
        self.refresh_cache()
    
    # + public method
    def refresh_cache(self):
        """
        تحديث التخزين المؤقت للمقررات والشعب من قاعدة البيانات.
        
        الوظيفة:
            تجلب جميع المقررات والشعب من قاعدة البيانات وتخزنها في الذاكرة
            (Cache) لتحسين الأداء وتقليل عمليات قاعدة البيانات.
        
        التدفق:
            1. جلب البيانات من قاعدة البيانات عبر database.fetch_courses_with_sections()
            2. مسح التخزين المؤقت الحالي
            3. تحويل البيانات إلى كائنات Course و Section
            4. تخزينها في التخزين المؤقت
        
        الربط:
            - يستخدم database.fetch_courses_with_sections() (من database.py)
            - ينشئ كائنات Course (من السطر 133) و Section (من السطر 172)
            - يُستدعى من: __init__() و بعد إضافة/تحديث/حذف المقررات
        
        يُستدعى من:
            - __init__() (السطر 615) - عند بدء النظام
            - بعد add_course(), delete_course(), add_section(), delete_section()
            - من student.py - StudentDashboard.load_data() عند الضغط على "تحديث"
        """
        # جلب جميع المقررات والشعب والمتطلبات السابقة من قاعدة البيانات
        data = database.fetch_courses_with_sections()
        
        # مسح التخزين المؤقت الحالي
        self._course_cache.clear()
        self._section_cache.clear()
        
        # تحويل البيانات إلى كائنات Course وتخزينها في التخزين المؤقت
        for course_code, course_data in data.items():
            course = Course(
                course_code=course_code,
                name=course_data['name'],
                credits=course_data['credit_hours'],
                lecture_hours=course_data['lecture_hours'],
                lab_hours=course_data.get('lab_hours', 0),
                prerequisites=course_data.get('prerequisites', [])
            )
            self._course_cache[course_code] = course
            
            # تحويل الشعب إلى كائنات Section وتخزينها
            for section_data in course_data.get('sections', []):
                section = Section(
                    section_id=section_data['id'],
                    course_code=course_code,
                    instructor=section_data['instructor'],
                    start_time=section_data['start'],
                    end_time=section_data['end'],
                    hall=section_data['hall'],
                    max_capacity=section_data['max_capacity'],
                    current_enrollment=section_data.get('current_enrollment', 0),
                    days=section_data.get('days', '')
                )
                self._section_cache[section_data['id']] = section
    
    def get_course(self, course_code: str) -> Optional[Course]:
        """Get course by code."""
        return self._course_cache.get(course_code)
    
    def get_section(self, section_id: str) -> Optional[Section]:
        """Get section by ID."""
        return self._section_cache.get(section_id)
    
    def get_available_courses(self, program: str, level: int) -> List[Course]:
        """
        جلب المقررات المتاحة لبرنامج ومستوى محدد.
        
        الوظيفة:
            ترجع قائمة بالمقررات المتاحة للطالب بناءً على برنامجه ومستواه.
            تعتمد على جدول program_plans الذي يحدده المدير، وليس على نمط الكود.
        
        التدفق:
            1. جلب رموز المقررات من جدول program_plans للبرنامج والمستوى المحدد
            2. جلب كائنات المقررات من التخزين المؤقت بناءً على الرموز
            3. ترتيب المقررات حسب الرمز للعرض الموحد
        
        معايير التصفية:
            - يتم تحديد المقررات المتاحة لكل برنامج ومستوى من قبل المدير
            - المدير يحدد المقررات في جدول program_plans
            - لا يوجد اعتماد على نمط الكود (مثل "110" للمستوى 1)
        
        الربط:
            - يستخدم database.get_courses_for_program_and_level() لجلب المقررات من program_plans
            - يستخدم self._course_cache (التخزين المؤقت)
            - يُستدعى من: student.py - StudentDashboard.load_available_courses()
        
        Args:
            program: البرنامج الدراسي (Computer, Comm, Power, Biomedical)
            level: مستوى الطالب (1-10)
        
        Returns:
            قائمة من كائنات Course المتاحة للطالب حسب ما حدده المدير في program_plans
        """
        # تحويل 'Communications' إلى 'Comm' للتوافق مع قاعدة البيانات
        if program == 'Communications':
            program = 'Comm'
        
        # جلب رموز المقررات المتاحة للبرنامج والمستوى من جدول program_plans
        # هذا يعتمد على ما حدده المدير، وليس على نمط الكود
        available_course_codes = get_courses_for_program_and_level(program, level)
        
        # جلب كائنات المقررات من التخزين المؤقت
        filtered_courses = []
        for course_code in available_course_codes:
            course = self._course_cache.get(course_code)
            if course:
                filtered_courses.append(course)
        
        # ترتيب المقررات حسب الرمز للعرض الموحد
        return sorted(filtered_courses, key=lambda c: c.course_code)
    
    # + public method
    def add_course(self, course: Course):
        """
        Add or update a course in the database.
        Validates unique course code and prerequisites.
        As per project requirements.
        """
        # Validate prerequisites exist in the system
        if course.prerequisites:
            all_valid, invalid_codes = database.validate_prerequisites(course.prerequisites)
            if not all_valid:
                raise ValueError(f"Prerequisite '{invalid_codes[0]}' is not a valid course.")
        
        # Check if course code already exists (for new courses only)
        # Note: upsert_course uses ON CONFLICT, so we check separately for new entries
        if database.course_exists(course.course_code):
            # Course exists - this is an update, which is allowed
            pass
        
        # Save course to database
        database.upsert_course(
            course.course_code,
            course.name,
            course.credits,
            course.lecture_hours,
            course.lab_hours
        )
        
        # Save prerequisites
        if course.prerequisites:
            database.set_course_prerequisites(course.course_code, course.prerequisites)
        
        self.refresh_cache()
    
    # + public method
    def delete_course(self, course_code: str):
        """Delete a course from the database."""
        database.delete_course(course_code)
        self.refresh_cache()
    
    # + public method
    def add_section(self, section: Section):
        """Add or update a section in the database."""
        database.upsert_section(
            section.section_id,
            section.course_code,
            section.instructor,
            section.start_time,
            section.end_time,
            section.hall,
            section.max_capacity,
            section.current_enrollment,
            section.days
        )
        self.refresh_cache()
    
    # + public method
    def delete_section(self, section_id: str):
        """Delete a section from the database."""
        database.delete_section(section_id)
        self.refresh_cache()
    
    # + public method
    def validate_schedule_student_course_registration_system(self, student: Student, selected_courses: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate student's selected courses against all constraints.
        As per project requirements.
        
        Returns: (is_valid: bool, error_messages: List[str])
        """
        errors = []
        
        # ملاحظة: تم إزالة التحقق من حدود الساعات المعتمدة (الحد الأدنى والأقصى)
        
        # 1. Check if course is already in transcript (already completed)
        for course_code in selected_courses:
            if course_code in student.transcript:
                errors.append(
                    f"Cannot register for {course_code}: Course already completed (exists in transcript)"
                )
        
        # 2. Check prerequisites
        for course_code in selected_courses:
            course = self._course_cache.get(course_code)
            if course:
                prereqs_met, missing = course.check_prerequisites_transcript(student.transcript)
                if not prereqs_met:
                    errors.append(
                        f"Cannot register for {course_code}: Missing prerequisites {', '.join(missing)}"
                    )
        
        # 3. Check if courses match student level (using course code pattern)
        # Level validation is done in get_available_courses, so courses here should already be valid
        # But we can add additional validation if needed
        
        # 4. Check for time conflicts (if sections are specified)
        # This would need section IDs, handled in register_student method
        
        return len(errors) == 0, errors
    
    # + public method
    def register_student_database_registration_system(self, student: Student, course_list: List[str]) -> Tuple[bool, str]:
        """
        Register student for a list of courses (section IDs).
        As per project requirements.
        
        Returns: (success: bool, message: str)
        """
        # Validate schedule first
        course_codes = []
        sections = []
        
        for section_id in course_list:
            section = self.get_section(section_id)
            if not section:
                return False, f"Section {section_id} not found"
            sections.append(section)
            course_codes.append(section.course_code)
        
        # Check if any course is already in transcript (already completed)
        for section in sections:
            if section.course_code in student.transcript:
                return False, f"Cannot register for {section.course_code}: Course already completed (exists in transcript)"
        
        # Check prerequisites and constraints
        is_valid, errors = self.validate_schedule_student_course_registration_system(student, course_codes)
        if not is_valid:
            return False, "; ".join(errors)
        
        # Check section capacities
        for section in sections:
            if section.is_full():
                return False, f"Section {section.section_id} is full"
        
        # Check time conflicts
        for i, section1 in enumerate(sections):
            for section2 in sections[i+1:]:
                if section1.has_time_conflict_section(section2):
                    return False, f"Time conflict: {section1.section_id} overlaps with {section2.section_id}"
        
        # Check if already registered in the same section
        for section in sections:
            if any(reg.get('id') == section.section_id for reg in student.schedule):
                return False, f"Already registered for {section.section_id}"
        
        # Check if already registered in the same course (different section)
        for section in sections:
            course_code = section.course_code
            for reg in student.schedule:
                existing_section = self.get_section(reg.get('id'))
                if existing_section and existing_section.course_code == course_code:
                    return False, f"Already registered for course {course_code} (section: {existing_section.section_id}). Cannot register for the same course twice in the same term"
        
        # All validations passed - register student
        registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for section in sections:
            # Increment enrollment
            success, error = database.increment_section_enrollment(section.section_id)
            if not success:
                # Rollback any previous registrations
                for prev_section in sections:
                    if prev_section.section_id != section.section_id:
                        database.remove_registration(student.student_id, prev_section.section_id)
                        database.decrement_section_enrollment(prev_section.section_id)
                return False, error or "Failed to update enrollment"
            
            # Save registration to database
            try:
                database.add_registration(student.student_id, section.section_id, registration_time)
            except Exception as e:
                # Rollback enrollment increment
                database.decrement_section_enrollment(section.section_id)
                # Rollback previous registrations
                for prev_section in sections:
                    if prev_section.section_id != section.section_id:
                        database.remove_registration(student.student_id, prev_section.section_id)
                        database.decrement_section_enrollment(prev_section.section_id)
                return False, f"Failed to save registration: {str(e)}"
            
            # Add to student schedule
            student.schedule.append({
                'id': section.section_id,
                'registration_time': registration_time
            })
        
        self.refresh_cache()
        return True, "Registration successful"
    
    # + public method
    def unregister_student_database_registration_system(self, student: Student, section_id: str) -> Tuple[bool, str]:
        """
        Unregister student from a section.
        
        Returns: (success: bool, message: str)
        """
        # Check if student is registered
        item_to_remove = None
        for item in student.schedule:
            if item.get('id') == section_id:
                item_to_remove = item
                break
        
        if not item_to_remove:
            return False, "Student not registered in this section"
        
        # Remove registration from database
        try:
            database.remove_registration(student.student_id, section_id)
        except Exception as e:
            return False, f"Failed to remove registration: {str(e)}"
        
        # Decrement enrollment
        success, error = database.decrement_section_enrollment(section_id)
        if not success:
            # Try to restore registration if enrollment decrement failed
            try:
                database.add_registration(student.student_id, section_id, item_to_remove.get('registration_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            except:
                pass
            return False, error or "Failed to update enrollment"
        
        # Remove from schedule
        student.schedule.remove(item_to_remove)
        
        self.refresh_cache()
        return True, "Unregistration successful"


# ============================================================================
# PASSWORD VALIDATION & HASHING (OOP Design)
# ============================================================================

class PasswordValidator_registration_system:
    """
    Password Validator Class - Validates password strength
    Using OOP design for easy extension
    """
    
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    
    def validate(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        Returns: (is_valid: bool, error_message: str)
        """
        if len(password) < self.MIN_LENGTH:
            return False, f"Password must be at least {self.MIN_LENGTH} characters long"
        
        if self.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if self.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if self.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if self.REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"


class PasswordHasher_registration_system:
    """
    Password Hasher Class - Handles password hashing and verification
    Using OOP design for password security
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using SHA-256 with salt.
        Note: In production, use bcrypt library for better security.
        """
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash.
        """
        try:
            if ":" not in password_hash:
                # Legacy plain text passwords - for backward compatibility
                return password == password_hash
            
            salt, stored_hash = password_hash.split(":", 1)
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return secrets.compare_digest(computed_hash, stored_hash)
        except Exception:
            return False


# ============================================================================
# SESSION MANAGEMENT (OOP Design)
# ============================================================================

class SessionManager_registration_system:
    """
    Session Manager Class - Manages user sessions
    Using OOP design for session handling
    """
    
    def __init__(self):
        """Initialize session manager."""
        self._sessions: Dict[str, Dict] = {}
    
    def create_session(self, user_id: str, role: str) -> str:
        """
        Create a new session for user.
        Returns: session_token (str)
        """
        session_token = secrets.token_urlsafe(32)
        self._sessions[session_token] = {
            'user_id': user_id,
            'role': role,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        self._manage_session_db(session_token, user_id, 'save')
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Get session information by token."""
        return self._sessions.get(session_token)
    
    def invalidate_session(self, session_token: str):
        """Invalidate a session."""
        if session_token in self._sessions:
            del self._sessions[session_token]
        self._manage_session_db(session_token, action='remove')
    
    # _ private method
    def _manage_session_db(self, session_token: str, user_id: str = None, action: str = 'save'):
        """Manage session in database (save or remove)."""
        conn = get_connection()
        cur = conn.cursor()
        if action == 'save':
            cur.execute(
                "INSERT OR REPLACE INTO sessions (session_id, user_id, login_time) VALUES (?, (SELECT user_id FROM users WHERE student_id = ?), ?)",
                (session_token, user_id, datetime.now().isoformat())
            )
        else:  # remove
            cur.execute("DELETE FROM sessions WHERE session_id = ?", (session_token,))
        conn.commit()
        conn.close()
    
    def _save_session_to_db(self, session_token: str, user_id: str):
        """Save session to database (backward compatibility)."""
        self._manage_session_db(session_token, user_id, 'save')
    
    def _remove_session_from_db(self, session_token: str):
        """Remove session from database (backward compatibility)."""
        self._manage_session_db(session_token, action='remove')


# ============================================================================
# ACCESS LOGGING (OOP Design)
# ============================================================================

class AccessLogger_registration_system:
    """
    Access Logger Class - Logs user access attempts
    Using OOP design for logging functionality
    """
    
    def __init__(self):
        """Initialize access logger."""
        self._ensure_log_table()
    
    def log_login_attempt(self, user_id: str, success: bool, ip_address: str = ""):
        """
        Log login attempt.
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO access_logs (user_id, action, success, timestamp, ip_address)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, 'login', success, datetime.now().isoformat(), ip_address)
        )
        conn.commit()
        conn.close()
    
    def log_access(self, user_id: str, action: str, success: bool = True):
        """
        Log general access action.
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO access_logs (user_id, action, success, timestamp)
               VALUES (?, ?, ?, ?)""",
            (user_id, action, success, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    # _ private method
    def _ensure_log_table(self):
        """Ensure access_logs table exists."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                success INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT
            )
        """)
        conn.commit()
        conn.close()


# ============================================================================
# USER MANAGEMENT (Enhanced with OOP)
# ============================================================================

class UserManager_registration_system:
    """
    User Manager Class - Manages user authentication and creation
    Using OOP design with password validation and hashing
    """
    
    def __init__(self):
        """Initialize user manager with validators and hashers."""
        self.password_validator = PasswordValidator_registration_system()
        self.password_hasher = PasswordHasher_registration_system()
        self.session_manager = SessionManager_registration_system()
        self.access_logger = AccessLogger_registration_system()
        self._ensure_bootstrap_admin()
    
    # _ private method
    def _ensure_bootstrap_admin(self):
        """Ensure default admin account exists."""
        # Check if admin exists first
        if not self.user_exists("2666666"):
            success, _ = self.create_user_passwordvalidator_passwordhasher_registration_system("2666666", "admin@odus.local", "AA123@123@", "admin", "Super Admin", validate_password=False)
    
    def create_user_passwordvalidator_passwordhasher_registration_system(self, user_id: str, email: str, password: str, 
                   role: str, display_name: str = "", mobile: str = "", 
                   validate_password: bool = True) -> Tuple[bool, str]:
        """
        Create or update user account.
        Returns: (success: bool, message: str)
        """
        # Validate password strength if required
        if validate_password and role == 'student':
            is_valid, error_msg = self.password_validator.validate(password)
            if not is_valid:
                return False, error_msg
        
        # Check for duplicate email/ID
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT user_id FROM users 
               WHERE (student_id = ? AND student_id IS NOT NULL) 
                  OR (email = ? AND email IS NOT NULL)""",
            (user_id, email)
        )
        row = cur.fetchone()
        
        if row:
            conn.close()
            return False, "Duplicate email or Student ID during sign-up"
        
        # Hash password
        password_hash = self.password_hasher.hash_password(password)
        
        # Insert new user
        try:
            cur.execute(
                """INSERT INTO users (student_id, email, password_hash, role, display_name, mobile) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, email, password_hash, role, display_name, mobile)
            )
            conn.commit()
            conn.close()
            return True, "User created successfully"
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Duplicate email or Student ID during sign-up"
    
    def authenticate_user_passwordhasher_accesslogger_registration_system(self, user_id: str, password: str) -> Optional[User]:
        """
        Authenticate user and return User object.
        Logs access attempts.
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT student_id, email, password_hash, role, 
                      COALESCE(display_name, ''), COALESCE(mobile, '')
               FROM users WHERE student_id = ? OR email = ?""",
            (user_id, user_id)
        )
        row = cur.fetchone()
        conn.close()
        
        if not row:
            try:
                self.access_logger.log_login_attempt(user_id, False)
            except Exception:
                pass  # Ignore logging errors for failed logins
            return None
        
        # Verify password
        stored_hash = row[2]
        if not self.password_hasher.verify_password(password, stored_hash):
            try:
                self.access_logger.log_login_attempt(user_id, False)
            except Exception:
                pass  # Ignore logging errors
            return None
        
        # Log successful login
        try:
            self.access_logger.log_login_attempt(row[0], True)
        except Exception:
            pass  # Continue even if logging fails
        
        return User(
            user_id=row[0],
            email=row[1],
            password_hash=row[2],
            role=row[3],
            display_name=row[4],
            mobile=row[5]
        )
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user ID exists."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE student_id = ? OR email = ?", (user_id, user_id))
        exists = cur.fetchone() is not None
        conn.close()
        return exists
    
    def create_session_sessionmanager_registration_system(self, user: User) -> str:
        """Create session for authenticated user."""
        return self.session_manager.create_session(user.user_id, user.role)
    
    def get_session_sessionmanager_registration_system(self, session_token: str) -> Optional[Dict]:
        """Get session information."""
        return self.session_manager.get_session(session_token)


# ============================================================================
# STUDENT MANAGEMENT
# ============================================================================

class StudentManager_registration_system:
    """Manages student data and operations."""
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """Get student by ID from database."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT student_id, name, email, program, level FROM students WHERE student_id = ?",
            (student_id,)
        )
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return None
        
        student_id, name, email, program, level = row
        transcript = self._get_transcript_database(student_id)
        schedule = self._get_schedule_database(student_id)
        
        # إذا كان مستوى الطالب أكبر من 1، إضافة جميع المواد من المستويات السابقة
        if level > 1:
            # حفظ البرنامج الأصلي للاستخدام مع get_courses_for_program_and_level
            program_for_query = program  # 'Comm' أو 'Computer' إلخ
            
            # جمع جميع المواد من المستويات السابقة (من 1 إلى level - 1)
            for prev_level in range(1, level):
                courses_for_level = get_courses_for_program_and_level(program_for_query, prev_level)
                # إضافة المواد إلى transcript في قاعدة البيانات إذا لم تكن موجودة بالفعل
                for course_code in courses_for_level:
                    if course_code not in transcript:
                        # إضافة المادة إلى قاعدة البيانات
                        database.add_course_to_transcript(student_id, course_code)
                        # إضافة المادة إلى قائمة transcript في الذاكرة
                        transcript.append(course_code)
        
        # تحويل 'Comm' إلى 'Communications' للتوافق مع الواجهة
        if program == 'Comm':
            program = 'Communications'
        
        return Student(
            student_id=student_id,
            name=name,
            email=email,
            program=program,
            level=level,
            transcript=transcript,
            schedule=schedule
        )
    
    def _get_transcript_database(self, student_id: str) -> List[str]:
        """Get completed course codes for student."""
        transcript_data = database.get_transcript(student_id)
        return [row[0] for row in transcript_data]  # course_code is first (and only) column
    
    # _ private method
    def _get_schedule_database(self, student_id: str) -> List[Dict]:
        """Get student's registered sections from database."""
        registrations = database.get_student_registrations(student_id)
        schedule = []
        for section_id, registration_time in registrations:
            schedule.append({
                'id': section_id,
                'registration_time': registration_time
            })
        return schedule
    
    def save_student_database(self, student: Student) -> str:
        """Save student to database."""
        return database.add_student(
            student.student_id,
            student.name,
            student.email,
            student.program,
            student.level
        )
    
    def get_all_students_database(self) -> List[Tuple]:
        """Get all students."""
        return database.list_students()
    
    def delete_student_database(self, student_id: str):
        """Delete student record."""
        database.delete_student_record(student_id)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_student_id_usermanager_registration_system(user_manager: UserManager_registration_system) -> str:
    """Generate unique student ID."""
    import random
    while True:
        candidate = f"S{random.randint(1000, 9999)}"
        if not user_manager.user_exists(candidate):
            return candidate


def generate_password() -> str:
    """Generate random password."""
    import random
    digits = ''.join(str(random.randint(0, 9)) for _ in range(7))
    return f"Ar@{digits}"

