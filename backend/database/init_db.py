from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from backend.config import settings
from backend.database.models import TABLE_SCHEMAS, TableSchema, build_create_table_sql


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def normalize_column_name(column_name: str) -> str:
    normalized = column_name.strip().lower()
    for char in (" ", "-", "/", "\\", "(", ")", "."):
        normalized = normalized.replace(char, "_")
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def load_source_file(file_path: Path) -> pd.DataFrame:
    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path)
    return pd.read_excel(file_path)


def infer_and_cast_types(frame: pd.DataFrame, schema: TableSchema) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [normalize_column_name(col) for col in frame.columns]
    frame = frame.convert_dtypes()

    for column, sqlite_type in schema.columns.items():
        if column not in frame.columns:
            frame[column] = pd.NA
        if sqlite_type == "REAL":
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        else:
            frame[column] = frame[column].astype("string")
            frame[column] = frame[column].where(frame[column].notna(), None)

    return frame[list(schema.columns.keys())]


def detect_table_for_file(file_path: Path) -> str | None:
    stem = normalize_column_name(file_path.stem)
    for table_name, schema in TABLE_SCHEMAS.items():
        if stem == table_name or stem in schema.source_aliases:
            return table_name
    return None


def create_empty_tables(connection: sqlite3.Connection) -> None:
    for schema in TABLE_SCHEMAS.values():
        connection.execute(build_create_table_sql(schema))
    connection.commit()


def load_table(connection: sqlite3.Connection, table_name: str, file_path: Path) -> int:
    schema = TABLE_SCHEMAS[table_name]
    frame = infer_and_cast_types(load_source_file(file_path), schema)
    connection.execute(f"DELETE FROM {table_name}")
    frame.to_sql(table_name, connection, if_exists="append", index=False)
    count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"Loaded {table_name}: {count} rows from {file_path.name}")
    return count


def init_db() -> dict[str, int]:
    db_path = settings.sqlite_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    data_dir = settings.data_dir

    with sqlite3.connect(db_path) as connection:
        create_empty_tables(connection)
        row_counts = {
            table_name: connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            for table_name in TABLE_SCHEMAS
        }

        if not data_dir.exists():
            print(f"Data directory not found: {data_dir}")
            print(f"Existing row counts: {row_counts}")
            return row_counts

        candidate_files = [
            path
            for path in data_dir.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        for file_path in sorted(candidate_files):
            table_name = detect_table_for_file(file_path)
            if not table_name:
                print(f"Skipping unrecognized source file: {file_path.name}")
                continue
            row_counts[table_name] = load_table(connection, table_name, file_path)

        for table_name in TABLE_SCHEMAS:
            count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            row_counts[table_name] = count
            print(f"Table {table_name}: {count} rows")

        return row_counts


if __name__ == "__main__":
    init_db()
