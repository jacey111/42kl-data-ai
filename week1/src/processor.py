from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError
import json

class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str

def clean_text(element):
    if not element:
        return ""

    return element.get_text(separator=" ", strip=True)

def extract_source_id(soup):
    og_url = soup.find("meta", property="og:url")

    if not og_url:
        return ""

    url = og_url.get("content", "")

    if not url:
        return ""

    return url.rstrip("/").split("/")[-1]

def process_all_html(input_dir, output_dir): 
    print("🥈 Silver: Starting processing...\n")

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create silver directory if missing
    output_path.mkdir(parents=True, exist_ok=True)

    # Handle missing directory
    if not input_path.exists():
        print(f"⚠️ Input directory does not exist: {input_path}")
        return

    html_files = list(input_path.glob("*.html"))

    # Handle empty directory
    if not html_files:
        print("⚠️ No HTML files found.")
        return

    total = len(html_files)
    processed = 0
    skipped = 0

    for file_path in html_files:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")

            # Extract field
            source_id = extract_source_id(soup)

            title_element = soup.find(attrs={"data-automation": "job-detail-title"})
            company_element = soup.find(attrs={"data-automation": "advertiser-name"})
            description_element = soup.find(attrs={"data-automation": "jobAdDetails"})

            job_title = clean_text(title_element)
            company = clean_text(company_element)
            description = clean_text(description_element)

            # Check validation
            missing_fields = []

            if not source_id:
                missing_fields.append("source_id")

            if not job_title:
                missing_fields.append("job_title")

            if not company:
                missing_fields.append("company")

            if not description:
                missing_fields.append("description")

            if missing_fields:
                print(
                    f"⚠️ Missing {', '.join(missing_fields)} in: {file_path.name}"
                )
                skipped += 1
                continue

            # Pydantic validation
            job_listing = JobListing(
                source_id=source_id,
                job_title=job_title,
                company=company,
                description=description,
            )

            output_file = output_path / f"{file_path.stem}.json"

            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(
                    job_listing.model_dump(),
                    json_file,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"✅ Processed: {file_path.name}")
            processed += 1

        except ValidationError as error:
            print(f"❌ Validation failed: {file_path.name}")
            print(error)
            skipped += 1

        except Exception as error:
            print(f"❌ Failed: {file_path.name} | Error: {error}")
            skipped += 1

    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")