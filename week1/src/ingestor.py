from email import message_from_binary_file
from pathlib import Path
import quopri

def ingest_all_mhtml(input_dir, output_dir):
    print("🥉 Bronze: Starting ingestion...\n")

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create bronze directory if missing
    output_path.mkdir(parents=True, exist_ok=True)

    # Handle missing source directory
    if not input_path.exists():
        print(f"⚠️ Source directory does not exist: {input_path}")
        return

    mhtml_files = list(input_path.glob("*.mhtml"))

    # Handle empty source directory
    if not mhtml_files:
        print("⚠️ No MHTML files found.")
        return

    total = len(mhtml_files)
    extracted = 0
    failed = 0

    for file_path in mhtml_files:
        try:
            with open(file_path, "rb") as file:
                msg = message_from_binary_file(file)

            html_content = None

            # Loops through every section of the MHTML file / multipart message
            for part in msg.walk():
                content_type = part.get_content_type()

                if content_type == "text/html":
                    payload = part.get_payload(decode=True)

                    if payload:
                        html_content = quopri.decodestring(payload).decode(
                            "utf-8",
                            errors="ignore"
                        )   # Decode quoted printable
                        break

            if not html_content:
                print(f"⚠️ No HTML content found in: {file_path.name}")
                failed += 1
                continue

            output_file = output_path / f"{file_path.stem}.html"

            with open(output_file, "w", encoding="utf-8") as out_file:
                out_file.write(html_content)

            print(f"✅ Extracted: {file_path.name}")
            extracted += 1

        except Exception as error:
            print(f"❌ Failed: {file_path.name} | Error: {error}")
            failed += 1

    print("\n📊 Bronze Summary:")
    print(f"Total: {total} | Extracted: {extracted} | Failed: {failed}")
