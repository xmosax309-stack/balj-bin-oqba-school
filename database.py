# -*- coding: utf-8 -*-
"""طبقة قاعدة البيانات (SQLite) لتطبيق بيانات مدرسة بلج بن عقبة."""
import sqlite3
from pathlib import Path

import pandas as pd

import seed_data as seed

DB_PATH = Path(__file__).resolve().parent / "school.db"

DDL = """
CREATE TABLE IF NOT EXISTS school_info (
    key   TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS stats (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    label    TEXT NOT NULL,
    value    INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS staff (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category    TEXT NOT NULL,
    section     TEXT NOT NULL,
    full_name   TEXT NOT NULL,
    job_title   TEXT,
    file_number TEXT,
    phone       TEXT,
    hire_date   TEXT,
    civil_id    TEXT,
    notes       TEXT
);
CREATE TABLE IF NOT EXISTS buses (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_number     INTEGER,
    driver_name    TEXT,
    driver_phone   TEXT,
    owner_name     TEXT,
    students_trip1 INTEGER,
    students_trip2 INTEGER,
    notes          TEXT
);
CREATE TABLE IF NOT EXISTS special_buses (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    program          TEXT,
    driver_name      TEXT,
    driver_phone     TEXT,
    supervisor_name  TEXT,
    supervisor_phone TEXT,
    students_count   INTEGER,
    notes            TEXT
);
CREATE TABLE IF NOT EXISTS cooperative (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_name TEXT,
    civil_id    TEXT,
    phone       TEXT
);
"""

# أسماء الأعمدة العربية المعروضة في الواجهة (الترتيب مهم)
COLUMN_LABELS = {
    "staff": {
        "category": "الفئة",
        "section": "القسم",
        "full_name": "الاسم",
        "job_title": "الوظيفة",
        "file_number": "رقم الملف",
        "phone": "رقم الهاتف",
        "hire_date": "تاريخ التعيين",
        "civil_id": "الرقم المدني",
        "notes": "ملاحظات",
    },
    "buses": {
        "bus_number": "رقم الحافلة",
        "driver_name": "اسم السائق",
        "driver_phone": "هاتف السائق",
        "owner_name": "اسم المالك",
        "students_trip1": "طلبة النقلة الأولى",
        "students_trip2": "طلبة النقلة الثانية",
        "notes": "ملاحظات",
    },
    "special_buses": {
        "program": "البرنامج",
        "driver_name": "اسم السائق",
        "driver_phone": "هاتف السائق",
        "supervisor_name": "اسم المشرف",
        "supervisor_phone": "هاتف المشرف",
        "students_count": "عدد الطلبة",
        "notes": "ملاحظات",
    },
    "cooperative": {
        "tenant_name": "اسم المستأجر",
        "civil_id": "الرقم المدني",
        "phone": "رقم الهاتف",
    },
}

TABLE_TITLES = {
    "staff": "الهيئة التعليمية والإدارية (الكادر)",
    "buses": "الحافلات المدرسية وسائقوها",
    "special_buses": "حافلات التربية الخاصة",
    "cooperative": "الجمعية التعاونية",
}


def connect():
    return sqlite3.connect(DB_PATH)


def db_version():
    """إصدار قاعدة البيانات (زمن آخر تعديل) — يُستخدم لإبطال التخزين المؤقت."""
    try:
        return DB_PATH.stat().st_mtime_ns
    except OSError:
        return 0


def _clean(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _insert(conn, table, rows):
    if not rows:
        return
    cols = list(COLUMN_LABELS[table].keys())
    placeholders = ", ".join(f":{c}" for c in cols)
    conn.executemany(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})",
        [{c: _clean(r.get(c)) for c in cols} for r in rows],
    )


def _seed(conn):
    conn.executemany("INSERT INTO school_info (key, value) VALUES (:key, :value)", seed.SCHOOL_INFO)
    conn.executemany("INSERT INTO stats (category, label, value) VALUES (:category, :label, :value)", seed.STATS)
    _insert(conn, "staff", seed.STAFF)
    _insert(conn, "buses", seed.BUSES)
    _insert(conn, "special_buses", seed.SPECIAL_BUSES)
    _insert(conn, "cooperative", seed.COOPERATIVE)


def init_db(force=False):
    """إنشاء قاعدة البيانات وتغذيتها إن كانت فارغة."""
    if force and DB_PATH.exists():
        DB_PATH.unlink()
    conn = connect()
    try:
        with conn:
            conn.executescript(DDL)
        count = conn.execute("SELECT COUNT(*) FROM staff").fetchone()[0]
        if count == 0:
            with conn:
                _seed(conn)
    finally:
        conn.close()


def load_table(table, version=0):  # version لإبطال الذاكرة المؤقتة عند التعديل
    conn = connect()
    try:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY id", conn)
    finally:
        conn.close()
    if "id" in df.columns:
        df = df.drop(columns=["id"])
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].fillna("")
    return df.rename(columns=COLUMN_LABELS[table])


def save_table(table, df_display):
    """استبدال كامل بيانات الجدول بعد التحرير في الواجهة."""
    reverse = {v: k for k, v in COLUMN_LABELS[table].items()}
    df = df_display.rename(columns=reverse)
    cols = list(COLUMN_LABELS[table].keys())
    for col in cols:
        if col not in df.columns:
            df[col] = None
    df = df.reindex(columns=cols)
    records = [{c: _clean(r[c]) for c in cols} for _, r in df.iterrows()]
    conn = connect()
    try:
        with conn:
            conn.execute(f"DELETE FROM {table}")
            _insert(conn, table, records)
    finally:
        conn.close()


def reseed_table(table):
    """استعادة البيانات الأصلية لجدول واحد من ملف البيانات."""
    source = {
        "staff": seed.STAFF,
        "buses": seed.BUSES,
        "special_buses": seed.SPECIAL_BUSES,
        "cooperative": seed.COOPERATIVE,
    }[table]
    conn = connect()
    try:
        with conn:
            conn.execute(f"DELETE FROM {table}")
            _insert(conn, table, source)
    finally:
        conn.close()


def load_school_info(version=0):
    conn = connect()
    try:
        rows = conn.execute("SELECT key, value FROM school_info").fetchall()
    finally:
        conn.close()
    return {k: v for k, v in rows}


def save_school_info(data):
    conn = connect()
    try:
        with conn:
            conn.executemany(
                "INSERT INTO school_info (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                list(data.items()),
            )
    finally:
        conn.close()


def load_stats(version=0):
    conn = connect()
    try:
        df = pd.read_sql("SELECT category, label, value FROM stats ORDER BY id", conn)
    finally:
        conn.close()
    return df.rename(columns={"category": "الفئة", "label": "البند", "value": "القيمة"})


def reset_db():
    init_db(force=True)
