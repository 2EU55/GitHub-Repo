import json
import sqlite3
from datetime import datetime
from io import StringIO
from pathlib import Path

import pandas as pd


def _db_path():
    return Path(__file__).resolve().parents[1] / "analyst.db"


def init_db():
    path = _db_path()
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                params_json TEXT NOT NULL,
                data_json TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def list_scenarios():
    conn = sqlite3.connect(_db_path())
    try:
        rows = conn.execute("SELECT name FROM scenarios ORDER BY created_at DESC").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def save_scenario(name, params, df):
    if not name or not str(name).strip():
        raise ValueError("方案名称不能为空")
    params_json = json.dumps(params, ensure_ascii=False)
    data_json = df.to_json(orient="records", force_ascii=False)
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    conn = sqlite3.connect(_db_path())
    try:
        conn.execute(
            "INSERT OR REPLACE INTO scenarios(name, created_at, params_json, data_json) VALUES (?, ?, ?, ?)",
            (str(name).strip(), created_at, params_json, data_json),
        )
        conn.commit()
    finally:
        conn.close()


def load_scenario(name):
    conn = sqlite3.connect(_db_path())
    try:
        row = conn.execute(
            "SELECT params_json, data_json FROM scenarios WHERE name = ?",
            (name,),
        ).fetchone()
        if not row:
            raise ValueError("未找到该方案")
        params = json.loads(row[0])
        df = pd.read_json(StringIO(row[1]), orient="records")
        return params, df
    finally:
        conn.close()


def delete_scenario(name):
    conn = sqlite3.connect(_db_path())
    try:
        conn.execute("DELETE FROM scenarios WHERE name = ?", (name,))
        conn.commit()
    finally:
        conn.close()
