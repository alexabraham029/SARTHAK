"""
Supreme Court Judgments Ingestion Script
Downloads the Indian Supreme Court Judgments dataset from Kaggle
and ingests it into the Pinecone vector database.

Usage:
    set KAGGLE_API_TOKEN=your_api_key_here
  python scripts/ingest_judgments.py

Or pass the token as an argument:
    python scripts/ingest_judgments.py --kaggle-token YOUR_KEY

Or point to an already-downloaded dataset folder:
    python scripts/ingest_judgments.py --dataset-path C:/path/to/indian-supreme-court-judgments
"""

import json
import os
import sys
import argparse
import hashlib
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)


def clean_value(value) -> str:
    """Normalize missing dataframe values to a clean string."""
    if value is None:
        return ""

    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def load_kaggle_token(kaggle_token: str = None):
    """Load Kaggle API token from args or environment for latest kagglehub."""
    token = kaggle_token or os.getenv("KAGGLE_API_TOKEN") or os.getenv("KAGGLE_KEY")

    if token:
        os.environ["KAGGLE_API_TOKEN"] = token

    return token


def download_dataset(
    kaggle_token: str = None,
    dataset_path: str = None,
) -> Path:
    """Download the dataset using kagglehub"""
    if dataset_path:
        resolved_path = Path(dataset_path).expanduser().resolve()
        if not resolved_path.exists():
            print(f"[ERROR] Dataset path does not exist: {resolved_path}")
            sys.exit(1)
        print(f"[OK] Using local dataset at: {resolved_path}")
        return resolved_path

    token = load_kaggle_token(kaggle_token)
    if not token:
        print("[ERROR] Kaggle API token not found.")
        print("\nProvide one of the following before running the script:")
        print("  1. Set KAGGLE_API_TOKEN environment variable")
        print("  2. Add KAGGLE_API_TOKEN to backend/.env")
        print("  3. Pass --kaggle-token on the command line")
        print("  4. Use --dataset-path with a previously downloaded dataset folder")
        sys.exit(1)

    try:
        import kagglehub
        print("[*] Downloading Indian Supreme Court Judgments dataset...")
        print("    This may take a while on first download...\n")
        path = kagglehub.dataset_download("vangap/indian-supreme-court-judgments")
        dataset_path = Path(path)
        print(f"[OK] Dataset downloaded to: {dataset_path}")
        return dataset_path
    except Exception as e:
        print(f"[ERROR] Failed to download dataset: {e}")
        print("\nMake sure you have:")
        print("  1. Set KAGGLE_API_TOKEN environment variable, or")
        print("  2. Passed --kaggle-token argument, or")
        print("  3. Used --dataset-path with a local dataset")
        sys.exit(1)


def find_metadata_file(dataset_path: Path) -> Path:
    """Find the CSV or Parquet metadata file in the dataset"""
    # Look for parquet files first (more efficient)
    parquet_files = list(dataset_path.rglob("*.parquet"))
    if parquet_files:
        print(f"[OK] Found Parquet file: {parquet_files[0].name}")
        return parquet_files[0]

    # Fall back to CSV
    csv_files = list(dataset_path.rglob("*.csv"))
    if csv_files:
        print(f"[OK] Found CSV file: {csv_files[0].name}")
        return csv_files[0]

    # List what we found
    all_files = list(dataset_path.rglob("*"))
    print("[ERROR] No CSV or Parquet metadata file found.")
    print(f"  Files in dataset directory ({len(all_files)}):")
    for f in all_files[:20]:
        print(f"    {f.relative_to(dataset_path)}")
    if len(all_files) > 20:
        print(f"    ... and {len(all_files) - 20} more")
    sys.exit(1)


def load_metadata(file_path: Path):
    """Load metadata from CSV or Parquet"""
    import pandas as pd

    print(f"[*] Loading metadata from {file_path.name}...")

    if file_path.suffix == ".parquet":
        df = pd.read_parquet(file_path)
    else:
        df = pd.read_csv(file_path, low_memory=False)

    print(f"[OK] Loaded {len(df)} records")
    print(f"    Columns: {list(df.columns)}")
    return df


def make_case_id(row, index: int) -> str:
    """Generate a stable unique ID for a case"""
    raw = "|".join(filter(None, [
        clean_value(row.get("diary_no", "")),
        clean_value(row.get("case_no", "")),
        clean_value(row.get("temp_link", "")),
    ])) or f"case_{index}"
    return f"sc_{hashlib.md5(raw.encode()).hexdigest()[:12]}"


def extract_year(row) -> int:
    """Extract year from available date fields"""
    # Try explicit year-like columns first
    if "year" in row and row["year"] is not None:
        try:
            return int(row["year"])
        except (ValueError, TypeError):
            pass

    # Try judgment_dates from the Kaggle Supreme Court dataset
    for date_column in ["judgment_dates", "decision_date"]:
        if date_column not in row or row[date_column] is None:
            continue

        try:
            date_str = str(row[date_column])
            # Try common formats
            for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y", "%Y"]:
                try:
                    from datetime import datetime
                    return datetime.strptime(date_str[:11], fmt).year
                except ValueError:
                    continue
            # Just grab the 4-digit year
            import re
            match = re.search(r"\b(19|20)\d{2}\b", date_str)
            if match:
                return int(match.group())
        except Exception:
            pass

    return None


def derive_case_name(row) -> str:
    """Build a readable case name from available metadata."""
    case_no = clean_value(row.get("case_no", ""))
    petitioner = clean_value(row.get("pet", ""))
    respondent = clean_value(row.get("res", ""))

    if petitioner and respondent:
        return f"{petitioner} v. {respondent}"
    if case_no:
        return case_no
    if petitioner:
        return petitioner
    return "Untitled Case"


def extract_pdf_excerpt(dataset_path: Path, row, max_chars: int = 4000) -> str:
    """Extract a short excerpt from the downloaded PDF if available."""
    if max_chars <= 0:
        return ""

    relative_pdf_path = clean_value(row.get("temp_link", ""))
    if not relative_pdf_path:
        return ""

    pdf_path = dataset_path / relative_pdf_path
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        return ""

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        extracted_pages = []
        current_length = 0

        for page in reader.pages[:5]:
            page_text = (page.extract_text() or "").strip()
            if not page_text:
                continue

            remaining = max_chars - current_length
            if remaining <= 0:
                break

            clipped_text = page_text[:remaining]
            extracted_pages.append(clipped_text)
            current_length += len(clipped_text)

            if current_length >= max_chars:
                break

        return "\n\n".join(extracted_pages).strip()
    except Exception:
        return ""


def build_judgment_text(row, pdf_excerpt: str = "") -> str:
    """Build a rich text representation for embedding"""
    parts = []

    title = derive_case_name(row)
    if title:
        parts.append(f"Case: {title}")

    case_no = clean_value(row.get("case_no", ""))
    if case_no:
        parts.append(f"Case Number: {case_no}")

    diary_no = clean_value(row.get("diary_no", ""))
    if diary_no:
        parts.append(f"Diary Number: {diary_no}")

    petitioner = clean_value(row.get("pet", ""))
    respondent = clean_value(row.get("res", ""))
    if petitioner:
        parts.append(f"Petitioner: {petitioner}")
    if respondent:
        parts.append(f"Respondent: {respondent}")

    petitioner_advocate = clean_value(row.get("pet_adv", ""))
    respondent_advocate = clean_value(row.get("res_adv", ""))
    if petitioner_advocate:
        parts.append(f"Petitioner Advocate: {petitioner_advocate}")
    if respondent_advocate:
        parts.append(f"Respondent Advocate: {respondent_advocate}")

    bench = clean_value(row.get("bench", ""))
    if bench:
        parts.append(f"Bench: {bench}")

    judgment_by = clean_value(row.get("judgement_by", ""))
    if judgment_by:
        parts.append(f"Judgment By: {judgment_by}")

    judgment_date = clean_value(row.get("judgment_dates", ""))
    if judgment_date:
        parts.append(f"Judgment Date: {judgment_date}")

    judgment_type = clean_value(row.get("Judgement_type", ""))
    if judgment_type:
        parts.append(f"Judgment Type: {judgment_type}")

    language = clean_value(row.get("language", ""))
    if language:
        parts.append(f"Language: {language}")

    pdf_link = clean_value(row.get("temp_link", ""))
    if pdf_link:
        parts.append(f"PDF Path: {pdf_link}")

    if pdf_excerpt:
        parts.append(f"Judgment Excerpt:\n{pdf_excerpt}")

    return "\n".join(parts) if parts else ""


def main():
    parser = argparse.ArgumentParser(description="Ingest Supreme Court Judgments into Pinecone")
    parser.add_argument("--kaggle-token", type=str, help="Kaggle API token for latest kagglehub")
    parser.add_argument("--dataset-path", type=str, help="Path to an already-downloaded Kaggle dataset folder")
    parser.add_argument("--batch-size", type=int, default=100, help="Upsert batch size")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records (None = all)")
    parser.add_argument("--start-index", type=int, default=0, help="Resume ingestion from this zero-based row index")
    parser.add_argument("--include-pdf-text", action="store_true", help="Extract a short text excerpt from each judgment PDF")
    parser.add_argument("--pdf-chars", type=int, default=2500, help="Max PDF characters to embed when --include-pdf-text is used")
    args = parser.parse_args()

    print("=" * 70)
    print("Sarthak — Supreme Court Judgments Ingestion")
    print("=" * 70)

    # Step 1: Download
    dataset_path = download_dataset(
        kaggle_token=args.kaggle_token,
        dataset_path=args.dataset_path,
    )

    # Step 2: Find metadata
    metadata_file = find_metadata_file(dataset_path)

    # Step 3: Load
    df = load_metadata(metadata_file)

    if args.limit:
        df = df.head(args.limit)
        print(f"[*] Limited to {args.limit} records")

    if args.start_index:
        if args.start_index >= len(df):
            print(f"[ERROR] start-index {args.start_index} is beyond dataset length {len(df)}")
            return
        df = df.iloc[args.start_index:]
        print(f"[*] Resuming from row index {args.start_index} ({len(df)} records remaining)")

    # Step 4: Initialize Pinecone
    print("\n[*] Initializing Pinecone...")
    from backend.app.services.pinecone_service import pinecone_service

    try:
        pinecone_service.initialize_index()
        print("[OK] Pinecone initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Pinecone: {e}")
        return

    # Check current index stats (Pinecone free tier = 2GB storage)
    try:
        stats = pinecone_service.get_index_stats()
        current_count = stats.get("total_vector_count", 0)
        print(f"[*] Current vectors in index: {current_count}")
        print(f"[*] Free-tier limit: 2GB storage — will ingest all and stop if storage is full")
    except Exception:
        print("[WARN] Could not check index stats, proceeding anyway")

    # Step 5: Process and upsert
    print(f"\n{'=' * 70}")
    print(f"Processing {len(df)} Supreme Court judgments...")
    print(f"{'=' * 70}\n")

    vectors = []
    skipped = 0
    processed = 0
    storage_full = False

    for idx, row in df.iterrows():
        pdf_excerpt = ""
        if args.include_pdf_text:
            pdf_excerpt = extract_pdf_excerpt(dataset_path, row, max_chars=args.pdf_chars)

        # Build judgment text for embedding
        judgment_text = build_judgment_text(row, pdf_excerpt=pdf_excerpt)
        if not judgment_text or len(judgment_text) < 20:
            skipped += 1
            continue

        # Generate ID
        case_id = make_case_id(row, idx)

        # Extract fields
        title = derive_case_name(row)

        petitioner = clean_value(row.get("pet", ""))
        respondent = clean_value(row.get("res", ""))
        facts_parts = []
        if petitioner:
            facts_parts.append(f"Petitioner: {petitioner}")
        if respondent:
            facts_parts.append(f"vs Respondent: {respondent}")
        petitioner_advocate = clean_value(row.get("pet_adv", ""))
        respondent_advocate = clean_value(row.get("res_adv", ""))
        if petitioner_advocate:
            facts_parts.append(f"Petitioner Advocate: {petitioner_advocate}")
        if respondent_advocate:
            facts_parts.append(f"Respondent Advocate: {respondent_advocate}")
        facts = " ".join(facts_parts) if facts_parts else None

        description_parts = []
        judgment_type = clean_value(row.get("Judgement_type", ""))
        if judgment_type:
            description_parts.append(f"Judgment Type: {judgment_type}")
        judgment_date = clean_value(row.get("judgment_dates", ""))
        if judgment_date:
            description_parts.append(f"Date: {judgment_date}")
        bench = clean_value(row.get("bench", ""))
        if bench:
            description_parts.append(f"Bench: {bench}")
        if pdf_excerpt:
            description_parts.append(pdf_excerpt)
        description = "\n".join(description_parts)

        citation_parts = [clean_value(row.get("case_no", "")), clean_value(row.get("diary_no", ""))]
        citation = " | ".join([part for part in citation_parts if part]) or None

        judge = clean_value(row.get("judgement_by", "")) or clean_value(row.get("bench", "")) or None

        year = extract_year(row)

        # Generate embedding
        # Truncate text for embedding (model has token limits)
        embed_text = judgment_text[:2000]
        try:
            embedding = pinecone_service.generate_embedding(embed_text)
        except Exception as e:
            print(f"  [WARN] Embedding failed for {case_id}: {e}")
            skipped += 1
            continue

        # Build metadata (keep under 40KB for Pinecone)
        metadata = {
            "id": case_id,
            "case_name": title[:500],
            "court": "Supreme Court of India",
            "judgment": description[:1500] if description else judgment_text[:1500],
            "type": "sc_judgment",
        }

        if year:
            metadata["year"] = year
        if citation:
            metadata["citation"] = citation[:300]
        if facts:
            metadata["facts"] = facts[:500]
        if judge:
            metadata["judge"] = judge[:300]
        if petitioner and petitioner != "nan":
            metadata["petitioner"] = petitioner[:250]
        if respondent and respondent != "nan":
            metadata["respondent"] = respondent[:250]
        pdf_link = clean_value(row.get("temp_link", ""))
        if pdf_link:
            metadata["pdf_path"] = pdf_link[:500]

        vectors.append({
            "id": case_id,
            "values": embedding,
            "metadata": metadata,
        })

        processed += 1

        # Upsert in batches
        if len(vectors) >= args.batch_size:
            try:
                pinecone_service.index.upsert(vectors=vectors, namespace="cases")
                print(f"  [OK] Upserted batch — {processed} processed so far")
            except Exception as e:
                error_msg = str(e).lower()
                if "exceed" in error_msg or "storage" in error_msg or "quota" in error_msg or "limit" in error_msg:
                    print(f"\n[STOP] Pinecone free-tier storage limit reached!")
                    print(f"       Successfully ingested {processed - len(vectors)} judgments.")
                    storage_full = True
                    break
                print(f"  [ERROR] Batch upsert failed: {e}")
            vectors = []

    # Upsert remaining
    if vectors and not storage_full:
        try:
            pinecone_service.index.upsert(vectors=vectors, namespace="cases")
            print(f"  [OK] Upserted final batch")
        except Exception as e:
            error_msg = str(e).lower()
            if "exceed" in error_msg or "storage" in error_msg or "quota" in error_msg or "limit" in error_msg:
                print(f"\n[STOP] Pinecone free-tier storage limit reached on final batch!")
            else:
                print(f"  [ERROR] Final batch upsert failed: {e}")

    # Stats
    print(f"\n{'=' * 70}")
    print(f"INGESTION COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Total:     {len(df)}")

    try:
        stats = pinecone_service.get_index_stats()
        print(f"\n  Pinecone Index Stats:")
        print(f"    Total vectors: {stats.get('total_vector_count', 0)}")
        namespaces = stats.get("namespaces", {})
        for ns, info in namespaces.items():
            print(f"    Namespace '{ns}': {info.get('vector_count', 0)} vectors")
    except Exception as e:
        print(f"  [WARN] Could not retrieve stats: {e}")

    print(f"\n{'=' * 70}")
    print("Done! The judgments are now searchable via /api/cases/ endpoints.")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
