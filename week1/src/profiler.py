from pathlib import Path
import sqlite3

def run_data_profile(db_path):
    """
    Analyzes the loaded data and prints a simple data quality report
    """
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return  # Early exit if database is missing, avoid creating a new empty database

    connection = sqlite3.connect(db_path)   # Connects to the existing database
    cursor = connection.cursor()    # Cursor executes SQL commands

    # Total rows in the jobs table
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        """
    )

    total_records = cursor.fetchone()[0]    # fetchone() returns a tuple like (total_records,) so we take the first element with [0]

    # NULL counts for job_title, company, description
    cursor.execute(
        """
        SELECT
            SUM(CASE WHEN job_title IS NULL OR job_title = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN company IS NULL OR company = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END)
        FROM jobs
        """
    )

    null_counts = cursor.fetchone()   # tuple like (missing_job_titles, missing_companies, missing_descriptions)

    # Average job descriptions length (in characters)
    cursor.execute(
        """
        SELECT AVG(LENGTH(description))
        FROM jobs
        """
    )

    avg_description_length = cursor.fetchone()[0]

    # Shortest description
    cursor.execute(
        """
        SELECT
            source_id,
            job_title,
            LENGTH(description) as desc_length
        FROM jobs
        ORDER BY desc_length ASC
        LIMIT 1
        """
    )

    shortest = cursor.fetchone()

    # Longest description
    cursor.execute(
        """
        SELECT
            source_id,
            job_title,
            LENGTH(description) as desc_length
        FROM jobs
        ORDER BY desc_length DESC
        LIMIT 1
        """
    )

    longest = cursor.fetchone()

    connection.close()

    print("\n--- 🔍 DATA QUALITY REPORT ---")

    print(f"📈 Total Records: {total_records}")

    print(
        "❓ Missing Values -> "
        f"job_title: {null_counts[0]}, "
        f"company: {null_counts[1]}, "
        f"description: {null_counts[2]}"
    )

    print(
        f"📝 Avg Description Length: "
        f"{round(avg_description_length)} chars"
    )

    print(f"⚠️ Shortest Description: {shortest[2]} chars")
    print(
        f"   ↳ source_id: {shortest[0]} | "
        f"job_title: {shortest[1]}"
    )

    print(f"🚨 Longest Description: {longest[2]} chars")
    print(
        f"   ↳ source_id: {longest[0]} | "
        f"job_title: {longest[1]}"
    )