from pathlib import Path
import json
import sqlite3

def create_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            description TEXT NOT NULL,
            tech_stack TEXT 
        )
        """
    ) # prevents crashes if DB already exists

def load_all_jsons(input_dir, output_dir):
    print("🥇 Gold: Starting database load...\n")

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create gold directory if missing
    output_path.mkdir(parents=True, exist_ok=True)

    # Handle missing silver directory
    if not input_path.exists():
        print(f"⚠️ Input directory does not exist: {input_path}")
        return

    json_files = list(input_path.glob("*.json"))

    # Handle empty directory
    if not json_files:
        print("⚠️ No JSON files found.")
        return

    db_path = output_path / "jobs.db"

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    create_table(cursor)

    total = len(json_files)
    inserted = 0
    skipped = 0

    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            cursor.execute(
                """
                INSERT OR IGNORE INTO jobs (
                    source_id,
                    job_title,
                    company,
                    description,
                    tech_stack
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    data["source_id"],
                    data["job_title"],
                    data["company"],
                    data["description"],
                    None,
                ),
            ) # skip insertion if duplicate source_id exists

            # rowcount = 1 means inserted, else means ignored (duplicate)
            if cursor.rowcount == 1:
                print(f"✅ Inserted: {file_path.name}")
                inserted += 1
            else:
                print(f"⏭️ Skipped (duplicate): {file_path.name}")
                skipped += 1

        except Exception as error:
            print(f"❌ Failed: {file_path.name} | Error: {error}")

    connection.commit()
    connection.close()

    print("\n📊 Gold Summary:")
    print(f"Total: {total} | Inserted: {inserted} | Skipped: {skipped}")