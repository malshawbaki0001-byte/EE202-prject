# EE202-prject

# التوثيق الشامل للمشروع - Project Documentation

## 📁 نظرة عامة على الملفات

### 1. `registration_system.py` - الملف الأساسي للنظام
**الهدف**: يحتوي على جميع الكلاسات الأساسية والنماذج والمنطق الأساسي

**الكلاسات الرئيسية**:
- `BaseValidator` → `LevelValidator` (نظام التحقق)
- `BaseUser` → `StudentUser`, `AdminUser` (نظام المستخدمين)
- `BaseCourseFilter` → `LevelBasedCourseFilter` (نظام التصفية)
- `RegistrationSystem` (نظام التسجيل الرئيسي)
- `UserManager` (إدارة المستخدمين)
- `StudentManager` (إدارة الطلاب)

**الربط**:
- يستورد: `database.py`
- يُستخدم في: `gui.py`, `student.py`, `admin.py`

---

### 2. `database.py` - ملف قاعدة البيانات
**الهدف**: جميع عمليات قاعدة البيانات SQLite

**الكلاسات الرئيسية**:
- `DatabaseManager` (إدارة قاعدة البيانات)

**الدوال الرئيسية**:
- إدارة الطلاب: `add_student()`, `list_students()`, `get_transcript()`
- إدارة المقررات: `upsert_course()`, `validate_prerequisites()`
- إدارة الشعب: `upsert_section()`, `increment_section_enrollment()`
- إدارة التسجيلات: `add_registration()`, `get_student_registrations()`
- إدارة خطط البرامج: `add_course_to_program_plan()`, `get_course_program_plans()`

**الربط**:
- يستورد: `sqlite3`
- يُستخدم في: `registration_system.py`, `admin.py`

---

### 3. `student.py` - واجهة الطالب
**الهدف**: جميع واجهات المستخدم المتعلقة بالطالب

**الكلاسات الرئيسية**:
- `BaseDashboard` (يرث من `PyQt6.QWidget`)
- `StudentDashboard` (يرث من `BaseDashboard`)
- `TranscriptDialog` (يرث من `PyQt6.QDialog`)

**الربط**:
- يستورد: `registration_system.py`, `styles.py`
- يُستخدم في: `gui.py` (MainApp.run())
- يرث منه: `admin.py` (AdminDashboard يرث من BaseDashboard)

---

### 4. `admin.py` - واجهة المدير
**الهدف**: جميع واجهات المستخدم المتعلقة بالمدير

**الكلاسات الرئيسية**:
- `AdminDashboard` (يرث من `BaseDashboard` من `student.py`)

**الربط**:
- يستورد: `student.py` (BaseDashboard), `registration_system.py`, `database.py`, `styles.py`
- يُستخدم في: `gui.py` (MainApp.run())

---

### 5. `gui.py` - الواجهة الرئيسية
**الهدف**: نقطة الدخول الرئيسية ونافذة تسجيل الدخول

**الكلاسات الرئيسية**:
- `LoginDialog` (يرث من `PyQt6.QDialog`)
- `RegisterStudentDialog` (يرث من `PyQt6.QDialog`)
- `MainApp` (يرث من `PyQt6.QApplication`)
- `MainWindow` (يرث من `PyQt6.QMainWindow`)

**الربط**:
- يستورد: `registration_system.py`, `student.py`, `admin.py`, `styles.py`
- نقطة الدخول: `python gui.py`

---

### 6. `styles.py` - الأنماط
**الهدف**: أنماط CSS والدوال المساعدة

**المحتوى**:
- `LIGHT_MODE_QSS`: أنماط الوضع الفاتح
- `DARK_MODE_QSS`: أنماط الوضع الداكن
- `apply_shadow()`: دالة لإضافة الظل

**الربط**:
- يُستخدم في: `gui.py`, `student.py`, `admin.py`

---

## 🔗 مخطط العلاقات بين الملفات

```
gui.py
    ├── يستورد من: registration_system.py
    ├── يستورد من: student.py (StudentDashboard)
    ├── يستورد من: admin.py (AdminDashboard)
    └── يستورد من: styles.py (التنسيقات)

student.py (BaseDashboard)
    ├── يرث من: PyQt6.QWidget
    ├── يستورد من: registration_system.py
    ├── يستورد من: styles.py
    └── يرث منه: AdminDashboard (في admin.py)

admin.py (AdminDashboard)
    ├── يرث من: BaseDashboard (من student.py)
    ├── يستورد من: registration_system.py
    ├── يستورد من: database.py
    └── يستورد من: styles.py

registration_system.py
    ├── يستورد من: database.py
    └── يحتوي على: جميع الكلاسات الأساسية

database.py
    └── مستقل (يستخدم sqlite3 فقط)
```

---

## 🎯 نظام الوراثة (Inheritance) الكامل

### 1. Validators (المدققات)
```
BaseValidator (Abstract Base Class)
    └── LevelValidator
```

### 2. Users (المستخدمين)
```
BaseUser (Abstract Base Class)
    ├── StudentUser
    └── AdminUser
```

### 3. Course Filters (مرشحات المقررات)
```
BaseCourseFilter (Abstract Base Class)
    └── LevelBasedCourseFilter
```

### 4. Dashboards (لوحات التحكم)
```
PyQt6.QWidget
    └── BaseDashboard (في student.py)
            ├── StudentDashboard (في student.py)
            └── AdminDashboard (في admin.py)
```

---

## 📊 التدفق العام للتطبيق

### 1. بدء التطبيق
```
python gui.py
    ↓
MainApp.__init__()
    ↓
MainApp.run()
```

### 2. تسجيل الدخول
```
LoginDialog
    ↓
UserManager.authenticate()
    ↓
[نجاح] → عرض Dashboard المناسب
[فشل] → رسالة خطأ
```

### 3. واجهة الطالب
```
StudentDashboard (يرث من BaseDashboard)
    ↓
RegistrationSystem.get_available_courses()
    ↓
LevelBasedCourseFilter.filter() (يرث من BaseCourseFilter)
    ↓
عرض المقررات المتاحة
```

### 4. واجهة المدير
```
AdminDashboard (يرث من BaseDashboard)
    ↓
RegistrationSystem.add_course()
    ↓
database.upsert_course()
```

---

## 🔐 نظام المصادقة والأمان

### 1. Password Validation
```
PasswordValidator
    ↓
التحقق من قوة كلمة المرور
    ↓
PasswordHasher.hash_password()
```

### 2. User Authentication
```
UserManager.authenticate()
    ↓
PasswordHasher.verify_password()
    ↓
BaseUser (StudentUser أو AdminUser)
```

### 3. Session Management
```
SessionManager
    ↓
إنشاء Token
    ↓
حفظ في قاعدة البيانات
```

---

## 📚 أمثلة على استخدام الكلاسات

### مثال 1: استخدام نظام الوراثة
```python
# BaseUser (كلاس أساسي)
base_user = BaseUser(...)  # ❌ لا يمكن استخدامه مباشرة (Abstract)

# StudentUser (يرث من BaseUser)
student_user = StudentUser(user_id="123", ...)
role = student_user.get_role()  # "student"

# AdminUser (يرث من BaseUser)
admin_user = AdminUser(user_id="admin", ...)
role = admin_user.get_role()  # "admin"
```

### مثال 2: استخدام نظام التصفية
```python
# BaseCourseFilter (كلاس أساسي)
base_filter = BaseCourseFilter()  # ❌ لا يمكن استخدامه مباشرة (Abstract)

# LevelBasedCourseFilter (يرث من BaseCourseFilter)
level_filter = LevelBasedCourseFilter()
filtered = level_filter.filter(all_courses, level=1)  # مقررات تحتوي "110"
```

### مثال 3: استخدام لوحات التحكم
```python
# BaseDashboard (كلاس أساسي)
base_dashboard = BaseDashboard()  # ✅ يمكن استخدامه لكن محدود

# StudentDashboard (يرث من BaseDashboard)
student_dashboard = StudentDashboard(student, registration_system)
student_dashboard.toggle_theme()  # ✅ يستخدم دالة من BaseDashboard

# AdminDashboard (يرث من BaseDashboard)
admin_dashboard = AdminDashboard(user, registration_system)
admin_dashboard.toggle_theme()  # ✅ يستخدم دالة من BaseDashboard
```

---

## ✅ الخلاصة

### استخدام OOP والوراثة:
✅ **4 سلاسل وراثة رئيسية**:
1. Validators: BaseValidator → LevelValidator
2. Users: BaseUser → StudentUser, AdminUser
3. Filters: BaseCourseFilter → LevelBasedCourseFilter
4. Dashboards: QWidget → BaseDashboard → StudentDashboard, AdminDashboard

### التعليقات العربية:
✅ **جميع الكلاسات موثقة بالعربية** مع شرح:
- الوظيفة والمهام
- العلاقات والوراثة
- أماكن الربط والاستخدام
- أمثلة على الاستخدام

### البنية المنظمة:
✅ **6 ملفات منظمة**:
1. `registration_system.py` - المنطق الأساسي
2. `database.py` - قاعدة البيانات
3. `student.py` - واجهة الطالب
4. `admin.py` - واجهة المدير
5. `gui.py` - الواجهة الرئيسية
6. `styles.py` - التنسيقات

---

**جميع الملفات تحتوي على تعليقات عربية شاملة تشرح كل كلاس وعلاقاته وأماكن استخدامه!**

