"""ملف قاعدة البيانات - Database Module (database.py)
يحتوي على جميع عمليات قاعدة البيانات SQLite باستخدام OOP.
"""

import sqlite3
from typing import List, Tuple, Optional, Dict

# اسم ملف قاعدة البيانات
DB_NAME = "plans.db"

# البرامج المسموحة (للتأكد من صحة البيانات)
ALLOWED_PROGRAMS = ("Computer", "Comm", "Power", "Biomedical")


class DatabaseManager:
    """
    ============================================================================
    كلاس إدارة قاعدة البيانات - Database Manager Class
    ============================================================================
    
    الوظيفة:
        كلاس OOP لإدارة جميع العمليات المتعلقة بقاعدة البيانات SQLite.
        يوفر واجهة موحدة لإنشاء الجداول وإدارة الاتصالات.
    
    Visibility (الرموز):
        + public: يمكن الوصول من أي مكان
        _ private: للاستخدام الداخلي فقط
        # protected: للاستخدام من الكلاسات الفرعية
    
    العلاقات والربط:
        - الكلاس الأساسي: لا يرث من أي كلاس (كلاس مستقل)
        - الكلاسات التي ترث منه: لا يوجد
        - يتم استخدامه في:
            * database.py - _db_manager (في السطر 206) - يتم إنشاء مثيل عام واحد
            * database.py - get_connection() (في السطر 210) - يستدعي _db_manager.get_connection()
            * database.py - create_database() (في السطر 215) - يستدعي _db_manager.create_database()
            * جميع دوال database.py تستخدم get_connection() للحصول على اتصال
    
    مهامه:
        - إنشاء جميع الجداول والبنية الأساسية لقاعدة البيانات
        - إدارة اتصالات قاعدة البيانات مع تفعيل المفاتيح الخارجية
        - توفير واجهة موحدة لجميع العمليات على قاعدة البيانات
        
    مثال الاستخدام:
        db_manager = DatabaseManager()  # إنشاء مدير قاعدة البيانات
        conn = db_manager.get_connection()  # الحصول على اتصال
        db_manager.create_database()  # إنشاء/تحديث الجداول
    """
    
    def __init__(self, db_name: str = DB_NAME):
        """تهيئة مدير قاعدة البيانات."""
        self.db_name = db_name
        self._ensure_database_exists()
    
    def get_connection(self) -> sqlite3.Connection:
        """الحصول على اتصال بقاعدة البيانات مع تفعيل المفاتيح الخارجية."""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    def _ensure_database_exists(self):
        """التأكد من وجود قاعدة البيانات وإنشاء الجداول إذا لزم الأمر."""
        self.create_database()
    
    def create_database(self):
        """
        إنشاء جميع الجداول المستخدمة في النظام إذا لم تكن موجودة
        وظيفته: إنشاء البنية الأساسية لقاعدة البيانات
        """
        # التحقق من وجود max_capacity وإزالته إذا لزم الأمر
        # يجب القيام بذلك في اتصال منفصل مع تعطيل المفاتيح الخارجية
        temp_conn = sqlite3.connect(self.db_name)
        temp_cur = temp_conn.cursor()
        
        # تعطيل فحص المفاتيح الخارجية أولاً (يجب أن يكون قبل أي عمليات)
        temp_cur.execute("PRAGMA foreign_keys = OFF;")
        
        try:
            temp_cur.execute("PRAGMA table_info(courses);")
            columns = [row[1] for row in temp_cur.fetchall()]
            
            if "max_capacity" in columns:
                # حفظ البيانات
                temp_cur.execute("""
                    CREATE TABLE IF NOT EXISTS courses_backup (
                        course_code   TEXT PRIMARY KEY,
                        name          TEXT NOT NULL,
                        credits       INTEGER NOT NULL CHECK (credits > 0),
                        lecture_hours INTEGER NOT NULL CHECK (lecture_hours >= 0),
                        lab_hours     INTEGER DEFAULT 0 CHECK (lab_hours >= 0)
                    );
                """)
                temp_cur.execute("""
                    INSERT OR IGNORE INTO courses_backup (course_code, name, credits, lecture_hours, lab_hours)
                    SELECT course_code, name, credits, lecture_hours, COALESCE(lab_hours, 0)
                    FROM courses;
                """)
                
                # حذف الجدول القديم
                temp_cur.execute("DROP TABLE IF EXISTS courses;")
                
                # إنشاء الجدول الجديد
                temp_cur.execute("""
                    CREATE TABLE courses (
                        course_code   TEXT PRIMARY KEY,
                        name          TEXT NOT NULL,
                        credits       INTEGER NOT NULL CHECK (credits > 0),
                        lecture_hours INTEGER NOT NULL CHECK (lecture_hours >= 0),
                        lab_hours     INTEGER DEFAULT 0 CHECK (lab_hours >= 0)
                    );
                """)
                
                # استعادة البيانات
                temp_cur.execute("""
                    INSERT OR IGNORE INTO courses (course_code, name, credits, lecture_hours, lab_hours)
                    SELECT course_code, name, credits, lecture_hours, lab_hours
                    FROM courses_backup;
                """)
                
                # حذف النسخة الاحتياطية
                temp_cur.execute("DROP TABLE IF EXISTS courses_backup;")
                
                temp_conn.commit()
                
                # إعادة تفعيل المفاتيح الخارجية
                temp_cur.execute("PRAGMA foreign_keys = ON;")
        except Exception:
            temp_conn.rollback()
        finally:
            temp_conn.close()
        
        # الآن نستخدم الاتصال العادي لإنشاء بقية الجداول
        conn = self.get_connection()
        cur = conn.cursor()

        # -----------------------------
        # 1) جداول المقررات والمناهج
        # -----------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_code   TEXT PRIMARY KEY,
                name          TEXT NOT NULL,
                credits       INTEGER NOT NULL CHECK (credits > 0),
                lecture_hours INTEGER NOT NULL CHECK (lecture_hours >= 0),
                lab_hours     INTEGER DEFAULT 0 CHECK (lab_hours >= 0)
            );
            """
        )
        
        # إضافة عمود lab_hours إذا لم يكن موجوداً (للتوافق مع قواعد البيانات القديمة)
        cur.execute("PRAGMA table_info(courses);")
        columns = [row[1] for row in cur.fetchall()]
        if "lab_hours" not in columns:
            cur.execute("ALTER TABLE courses ADD COLUMN lab_hours INTEGER DEFAULT 0 CHECK (lab_hours >= 0);")
        
        # ملاحظة: max_capacity لم يعد موجوداً في المقررات، السعة متاحة فقط في الشعب (Section)

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS prerequisites (
                course_code TEXT NOT NULL,
                prereq_code TEXT NOT NULL,
                PRIMARY KEY (course_code, prereq_code),
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE,
                FOREIGN KEY (prereq_code) REFERENCES courses(course_code) ON DELETE RESTRICT
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS program_plans (
                program     TEXT NOT NULL,
                level       INTEGER NOT NULL,
                course_code TEXT NOT NULL,
                PRIMARY KEY (program, level, course_code),
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE RESTRICT
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sections (
                section_id         TEXT PRIMARY KEY,
                course_code        TEXT NOT NULL,
                instructor         TEXT NOT NULL,
                start_time         INTEGER NOT NULL,
                end_time           INTEGER NOT NULL,
                hall               TEXT NOT NULL,
                max_capacity       INTEGER NOT NULL CHECK (max_capacity > 0),
                current_enrollment INTEGER NOT NULL DEFAULT 0 CHECK (current_enrollment >= 0),
                days               TEXT DEFAULT '',
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE
            );
            """
        )
        
        # إضافة عمود days إذا لم يكن موجوداً (للتوافق مع قواعد البيانات القديمة)
        cur.execute("PRAGMA table_info(sections);")
        columns = [row[1] for row in cur.fetchall()]
        if "days" not in columns:
            cur.execute("ALTER TABLE sections ADD COLUMN days TEXT DEFAULT '';")

        # جدول أعضاء هيئة التدريس (Doctors/Faculty)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id          TEXT PRIMARY KEY,
                name               TEXT NOT NULL,
                email              TEXT UNIQUE NOT NULL,
                preferred_courses  TEXT DEFAULT '',
                time_availability  TEXT DEFAULT ''
            );
            """
        )

        # جدول تعيين المقررات لأعضاء هيئة التدريس
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor_assignments (
                assignment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id          TEXT NOT NULL,
                course_code        TEXT NOT NULL,
                section_id         TEXT,
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE,
                FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE SET NULL
            );
            """
        )

        # ------------------------------------------
        # 2) جداول بيانات الطلاب والسجلات الأكاديمية
        # ------------------------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                email      TEXT NOT NULL,
                program    TEXT NOT NULL,
                level      INTEGER NOT NULL,
                CHECK (program IN ('Computer', 'Comm', 'Power', 'Biomedical'))
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transcripts (
                student_id TEXT NOT NULL,
                course_code TEXT NOT NULL,
                PRIMARY KEY (student_id, course_code),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE RESTRICT
            );
            """
        )

        # Create registrations table with migration support
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registrations';")
        table_exists = cur.fetchone() is not None
        
        if table_exists:
            # Table exists - check columns for migration
            cur.execute("PRAGMA table_info(registrations);")
            columns = [row[1] for row in cur.fetchall()]
            
            # If section_id doesn't exist, recreate table with correct structure
            if "section_id" not in columns:
                # Backup old data if any
                cur.execute("DROP TABLE IF EXISTS registrations_backup;")
                cur.execute("CREATE TABLE registrations_backup AS SELECT * FROM registrations;")
                
                # Drop and recreate with correct structure
                cur.execute("DROP TABLE registrations;")
                cur.execute(
                    """
                    CREATE TABLE registrations (
                        student_id TEXT NOT NULL,
                        section_id TEXT NOT NULL,
                        registration_time TEXT NOT NULL,
                        PRIMARY KEY (student_id, section_id),
                        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                        FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
                    );
                    """
                )
            else:
                # Ensure registration_time column exists
                if "registration_time" not in columns:
                    cur.execute("ALTER TABLE registrations ADD COLUMN registration_time TEXT DEFAULT '';")
        else:
            # Create table if it doesn't exist
            cur.execute(
                """
                CREATE TABLE registrations (
                    student_id TEXT NOT NULL,
                    section_id TEXT NOT NULL,
                    registration_time TEXT NOT NULL,
                    PRIMARY KEY (student_id, section_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
                );
                """
            )

        # ------------------------------------------
        # 3) جداول المستخدمين والجلسات
        # ------------------------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id    TEXT UNIQUE,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL CHECK (role IN ('student', 'admin')),
                display_name  TEXT,
                mobile        TEXT
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id    INTEGER,
                login_time TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS access_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                success INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT
            );
            """
        )

        conn.commit()
        conn.close()


# إنشاء مثيل عام من DatabaseManager
_db_manager = DatabaseManager()


# دالة مساعدة للتوافق مع الكود القديم
def get_connection():
    """الحصول على اتصال بقاعدة البيانات (للتوافق مع الكود القديم)"""
    return _db_manager.get_connection()


# ============================================================================
# Student Management Functions
# ============================================================================

def add_student(student_id: str, name: str, email: str, program: str, level: int) -> str:
    """Insert a new student after simple validation."""
    # تحويل 'Communications' إلى 'Comm' للتوافق مع قاعدة البيانات
    if program == 'Communications':
        program = 'Comm'
    
    if program not in ALLOWED_PROGRAMS:
        return "❌ Please select a valid program."

    conn = get_connection()
    cur = conn.cursor()

    # check duplicate ID
    cur.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
    if cur.fetchone():
        conn.close()
        return "❌ Student ID already exists."

    cur.execute(
        """
        INSERT INTO students (student_id, name, email, program, level)
        VALUES (?, ?, ?, ?, ?)
        """,
        (student_id, name, email, program, level),
    )

    conn.commit()
    conn.close()
    return "✅ Student registered successfully!"


def get_transcript(student_id: str):
    """Return transcript rows for a given student_id as a list of tuples.
    Returns: list of tuples (course_code,)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT course_code
        FROM transcripts
        WHERE student_id = ?
        """,
        (student_id,),
    )

    data = cur.fetchall()
    conn.close()
    return data


def add_course_to_transcript(student_id: str, course_code: str):
    """Add a course to student transcript in database.
    If the course already exists, it will be ignored (due to PRIMARY KEY constraint).
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT OR IGNORE INTO transcripts (student_id, course_code)
            VALUES (?, ?)
            """,
            (student_id, course_code)
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def list_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.student_id, s.name, s.email, s.program, s.level
        FROM students s
        ORDER BY s.student_id
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_student_record(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM registrations WHERE student_id = ?", (student_id,))
    cur.execute("DELETE FROM transcripts WHERE student_id = ?", (student_id,))
    cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    cur.execute("DELETE FROM users WHERE user_id = ?", (student_id,))
    conn.commit()
    conn.close()


# ============================================================================
# Course & Section Management Functions
# ============================================================================

def fetch_courses_with_sections():
    """Return a nested dict of courses -> sections -> prerequisites."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT course_code, name, credits, lecture_hours, COALESCE(lab_hours, 0)
        FROM courses
        ORDER BY course_code
        """
    )
    courses = {}
    for course_code, name, credits, lecture_hours, lab_hours in cur.fetchall():
        courses[course_code] = {
            "name": name,
            "credit_hours": credits,
            "lecture_hours": lecture_hours,
            "lab_hours": lab_hours or 0,
            "prerequisites": [],
            "sections": [],
        }

    cur.execute(
        """
        SELECT course_code, prereq_code
        FROM prerequisites
        ORDER BY course_code
        """
    )
    for course_code, prereq_code in cur.fetchall():
        if course_code in courses:
            courses[course_code]["prerequisites"].append(prereq_code)

    cur.execute(
        """
        SELECT section_id,
               course_code,
               instructor,
               start_time,
               end_time,
               hall,
               max_capacity,
               current_enrollment,
               COALESCE(days, '')
        FROM sections
        ORDER BY course_code, section_id
        """
    )
    for (
        section_id,
        course_code,
        instructor,
        start_time,
        end_time,
        hall,
        max_capacity,
        current_enrollment,
        days,
    ) in cur.fetchall():
        if course_code not in courses:
            continue
        courses[course_code]["sections"].append(
            {
                "id": section_id,
                "instructor": instructor,
                "start": start_time,
                "end": end_time,
                "hall": hall,
                "max_capacity": max_capacity,
                "current_enrollment": current_enrollment,
                "days": days or '',
            }
        )

    conn.close()
    return courses


def upsert_course(course_code, name, credits, lecture_hours, lab_hours=0):
    """
    إضافة/تحديث مقرر في قاعدة البيانات.
    ملاحظة: max_capacity لم يعد موجوداً في المقررات، السعة متاحة فقط في الشعب.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO courses (course_code, name, credits, lecture_hours, lab_hours)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(course_code) DO UPDATE SET
                name = excluded.name,
                credits = excluded.credits,
                lecture_hours = excluded.lecture_hours,
                lab_hours = excluded.lab_hours
            """,
            (course_code, name, credits, lecture_hours, lab_hours or 0),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def course_exists(course_code: str) -> bool:
    """Check if a course with the given code exists."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM courses WHERE course_code = ?", (course_code,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def validate_prerequisites(prereq_codes: list[str]) -> tuple[bool, list[str]]:
    """
    Validates if all prerequisite course codes exist.
    Returns (True, []) if all exist, else (False, [missing_prereqs]).
    """
    missing_prereqs = []
    for prereq_code in prereq_codes:
        if not course_exists(prereq_code):
            missing_prereqs.append(prereq_code)
    return (True, []) if not missing_prereqs else (False, missing_prereqs)


def set_course_prerequisites(course_code: str, prereq_codes: list[str]):
    """
    Sets prerequisites for a course. Deletes existing prerequisites
    and inserts new ones.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Start a transaction
        cur.execute("BEGIN;")

        # Delete existing prerequisites for the course
        cur.execute("DELETE FROM prerequisites WHERE course_code = ?", (course_code,))

        # Insert new prerequisites
        for prereq_code in prereq_codes:
            cur.execute(
                """
                INSERT INTO prerequisites (course_code, prereq_code)
                VALUES (?, ?)
                """,
                (course_code, prereq_code)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_record(table: str, id_field: str, record_id: str):
    """Delete a record from any table (generic delete function)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE {id_field} = ?", (record_id,))
    conn.commit()
    conn.close()


def delete_course(course_code):
    """Delete a course (backward compatibility)."""
    delete_record("courses", "course_code", course_code)


def delete_section(section_id):
    """Delete a section (backward compatibility)."""
    delete_record("sections", "section_id", section_id)


def upsert_section(
    section_id,
    course_code,
    instructor,
    start_time,
    end_time,
    hall,
    max_capacity,
    current_enrollment=0,
    days='',
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sections (
            section_id, course_code, instructor, start_time,
            end_time, hall, max_capacity, current_enrollment, days
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(section_id) DO UPDATE SET
            course_code = excluded.course_code,
            instructor = excluded.instructor,
            start_time = excluded.start_time,
            end_time = excluded.end_time,
            hall = excluded.hall,
            max_capacity = excluded.max_capacity,
            current_enrollment = excluded.current_enrollment,
            days = excluded.days
        """,
        (
            section_id,
            course_code,
            instructor,
            start_time,
            end_time,
            hall,
            max_capacity,
            current_enrollment,
            days or '',
        ),
    )
    conn.commit()
    conn.close()




def update_section_enrollment(section_id: str, increment: bool = True) -> Tuple[bool, Optional[str]]:
    """Update section enrollment (increment or decrement)."""
    conn = get_connection()
    cur = conn.cursor()
    
    if increment:
        cur.execute("SELECT current_enrollment, max_capacity FROM sections WHERE section_id = ?", (section_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False, "Section not found"
        current, max_cap = row
        if current >= max_cap:
            conn.close()
            return False, "Section is already full"
        cur.execute("UPDATE sections SET current_enrollment = current_enrollment + 1 WHERE section_id = ?", (section_id,))
    else:
        cur.execute("SELECT current_enrollment FROM sections WHERE section_id = ?", (section_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False, "Section not found"
        if row[0] <= 0:
            conn.close()
            return False, "Section enrollment cannot go below zero"
        cur.execute("UPDATE sections SET current_enrollment = current_enrollment - 1 WHERE section_id = ?", (section_id,))
    
    conn.commit()
    conn.close()
    return True, None


def increment_section_enrollment(section_id):
    """Increment section enrollment (backward compatibility)."""
    return update_section_enrollment(section_id, increment=True)


def decrement_section_enrollment(section_id):
    """Decrement section enrollment (backward compatibility)."""
    return update_section_enrollment(section_id, increment=False)


# ============================================================================
# REGISTRATION MANAGEMENT
# ============================================================================

def add_registration(student_id: str, section_id: str, registration_time: str):
    """Add a new course registration for a student."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO registrations (student_id, section_id, registration_time)
            VALUES (?, ?, ?)
            """,
            (student_id, section_id, registration_time),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Registration already exists or invalid data: {e}")
    finally:
        conn.close()


def remove_registration(student_id: str, section_id: str):
    """Remove a course registration for a student."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM registrations
        WHERE student_id = ? AND section_id = ?
        """,
        (student_id, section_id),
    )
    conn.commit()
    conn.close()


def get_student_registrations(student_id: str):
    """Retrieve all registrations for a student.
    Returns: list of tuples (section_id, registration_time)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT section_id, registration_time
        FROM registrations
        WHERE student_id = ?
        ORDER BY registration_time
        """,
        (student_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# PROGRAM PLANS MANAGEMENT
def manage_program_plan(course_code: str, program: str, level: int, action: str = 'add'):
    """Add or remove a course from a program plan."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if action == 'add':
            cur.execute(
                "INSERT INTO program_plans (program, level, course_code) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                (program, level, course_code)
            )
        else:  # remove
            cur.execute(
                "DELETE FROM program_plans WHERE course_code = ? AND program = ? AND level = ?",
                (course_code, program, level)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def add_course_to_program_plan(course_code: str, program: str, level: int):
    """Add a course to a program plan (backward compatibility)."""
    manage_program_plan(course_code, program, level, 'add')

def remove_course_from_program_plan(course_code: str, program: str, level: int):
    """Remove a course from a program plan (backward compatibility)."""
    manage_program_plan(course_code, program, level, 'remove')


def get_course_program_plans(course_code: str):
    """Get all program plans for a course.
    Returns list of tuples: [(program, level), ...]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT program, level
        FROM program_plans
        WHERE course_code = ?
        ORDER BY program, level
        """,
        (course_code,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def remove_all_course_program_plans(course_code: str):
    """Remove all program plans for a course."""
    delete_record("program_plans", "course_code", course_code)


def get_courses_for_program_and_level(program: str, level: int) -> List[str]:
    """
    جلب رموز المقررات المتاحة لبرنامج ومستوى محدد من جدول program_plans.
    
    الوظيفة:
        ترجع قائمة برموز المقررات التي حددها المدير لهذا البرنامج والمستوى
        في جدول program_plans. هذا يحل محل الاعتماد على نمط الكود (مثل "110" للمستوى 1).
    
    Args:
        program: البرنامج الدراسي (Computer, Comm/Communications, Power, Biomedical)
        level: المستوى الدراسي (1-10)
    
    Returns:
        قائمة برموز المقررات (course_code) المتاحة للبرنامج والمستوى المحدد
    """
    # تحويل 'Communications' إلى 'Comm' للتوافق مع قاعدة البيانات
    if program == 'Communications':
        program = 'Comm'
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT course_code
        FROM program_plans
        WHERE program = ? AND level = ?
        ORDER BY course_code
        """,
        (program, level)
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


# ============================================================================
# DOCTOR/FACULTY MANAGEMENT FUNCTIONS
# ============================================================================

def add_doctor(doctor_id: str, name: str, email: str, preferred_courses: str = '', time_availability: str = ''):
    """Add a new doctor/faculty member."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO doctors (doctor_id, name, email, preferred_courses, time_availability)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(doctor_id) DO UPDATE SET
                name = excluded.name,
                email = excluded.email,
                preferred_courses = excluded.preferred_courses,
                time_availability = excluded.time_availability
            """,
            (doctor_id, name, email, preferred_courses, time_availability)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_doctor(doctor_id: str = None) -> Optional[Tuple] | List[Tuple]:
    """Get doctor(s) - all if doctor_id is None, specific if provided."""
    conn = get_connection()
    cur = conn.cursor()
    if doctor_id:
        cur.execute("SELECT doctor_id, name, email, preferred_courses, time_availability FROM doctors WHERE doctor_id = ?", (doctor_id,))
        row = cur.fetchone()
        conn.close()
        return row
    else:
        cur.execute("SELECT doctor_id, name, email, preferred_courses, time_availability FROM doctors ORDER BY name")
        rows = cur.fetchall()
        conn.close()
        return rows


def get_all_doctors() -> List[Tuple]:
    """Get all doctors (backward compatibility)."""
    return get_doctor()


def delete_doctor(doctor_id: str):
    """Delete a doctor/faculty member."""
    delete_record("doctors", "doctor_id", doctor_id)


def assign_course_to_doctor(doctor_id: str, course_code: str, section_id: Optional[str] = None) -> int:
    """Assign a course to a doctor. Returns assignment_id."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO doctor_assignments (doctor_id, course_code, section_id)
            VALUES (?, ?, ?)
            """,
            (doctor_id, course_code, section_id)
        )
        assignment_id = cur.lastrowid
        conn.commit()
        return assignment_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_doctor_assignments(doctor_id: str) -> List[Tuple]:
    """Get all course assignments for a doctor."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT assignment_id, doctor_id, course_code, section_id
        FROM doctor_assignments
        WHERE doctor_id = ?
        ORDER BY course_code
        """,
        (doctor_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def remove_doctor_assignment(assignment_id: int):
    """Remove a course assignment from a doctor."""
    delete_record("doctor_assignments", "assignment_id", str(assignment_id))


def get_doctor_schedule(doctor_id: str) -> List[Dict]:
    """Get the schedule (sections) for a doctor."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.section_id, s.course_code, s.start_time, s.end_time, s.hall,
               c.name as course_name, da.assignment_id
        FROM doctor_assignments da
        JOIN sections s ON da.section_id = s.section_id
        JOIN courses c ON s.course_code = c.course_code
        WHERE da.doctor_id = ?
        ORDER BY s.start_time
        """,
        (doctor_id,)
    )
    columns = [description[0] for description in cur.description]
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def check_doctor_time_conflict(doctor_id: str, start_time: int, end_time: int, exclude_section_id: Optional[str] = None) -> bool:
    """Check if a doctor has a time conflict with their existing assignments."""
    conn = get_connection()
    cur = conn.cursor()
    
    if exclude_section_id:
        cur.execute(
            """
            SELECT COUNT(*) FROM doctor_assignments da
            JOIN sections s ON da.section_id = s.section_id
            WHERE da.doctor_id = ? 
            AND s.section_id != ?
            AND NOT (s.end_time <= ? OR s.start_time >= ?)
            """,
            (doctor_id, exclude_section_id, start_time, end_time)
        )
    else:
        cur.execute(
            """
            SELECT COUNT(*) FROM doctor_assignments da
            JOIN sections s ON da.section_id = s.section_id
            WHERE da.doctor_id = ? 
            AND NOT (s.end_time <= ? OR s.start_time >= ?)
            """,
            (doctor_id, start_time, end_time)
        )
    
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


# تصدير الدوال المهمة
__all__ = [
    'DatabaseManager',
    'get_connection',
    'DB_NAME',
    'ALLOWED_PROGRAMS',
    # Student management
    'add_student',
    'get_transcript',
    'list_students',
    'delete_student_record',
    # Course & Section management
    'fetch_courses_with_sections',
    'upsert_course',
    'course_exists',
    'validate_prerequisites',
    'set_course_prerequisites',
    'delete_course',
    'upsert_section',
    'delete_section',
    'increment_section_enrollment',
    'decrement_section_enrollment',
    # Registration management
    'add_registration',
    'remove_registration',
    'get_student_registrations',
    # Program plans management
    'add_course_to_program_plan',
    'remove_course_from_program_plan',
    'get_course_program_plans',
    'remove_all_course_program_plans',
    'get_courses_for_program_and_level',
    # Doctor/Faculty management
    'add_doctor',
    'get_all_doctors',
    'get_doctor',
    'delete_doctor',
    'assign_course_to_doctor',
    'get_doctor_assignments',
    'remove_doctor_assignment',
    'get_doctor_schedule',
    'check_doctor_time_conflict',
]

