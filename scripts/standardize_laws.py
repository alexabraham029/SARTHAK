"""
Data Standardization Script for KanoonGPT
Converts all law JSON files to a unified format with unique IDs
"""

import json
import os
from pathlib import Path

# Define the base directory
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Ensure processed directory exists
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Law metadata
LAW_METADATA = {
    "ipc": {"name": "Indian Penal Code", "abbreviation": "IPC", "year": 1860},
    "crpc": {"name": "Code of Criminal Procedure", "abbreviation": "CrPC", "year": 1973},
    "cpc": {"name": "Code of Civil Procedure", "abbreviation": "CPC", "year": 1908},
    "iea": {"name": "Indian Evidence Act", "abbreviation": "IEA", "year": 1872},
    "mva": {"name": "Motor Vehicles Act", "abbreviation": "MVA", "year": 1988},
    "nia": {"name": "Negotiable Instruments Act", "abbreviation": "NIA", "year": 1881},
    "ida": {"name": "Indian Divorce Act", "abbreviation": "IDA", "year": 1869},
    "hma": {"name": "Hindu Marriage Act", "abbreviation": "HMA", "year": 1955},
}


def standardize_ipc(data, law_code):
    """Standardize IPC format"""
    standardized = []
    for item in data:
        section_num = item.get("Section", "")
        standardized.append({
            "id": f"{law_code.lower()}_{section_num}",
            "law": law_code,
            "law_name": LAW_METADATA[law_code.lower()]["name"],
            "chapter": str(item.get("chapter", "")),
            "chapter_title": item.get("chapter_title", ""),
            "section": str(section_num),
            "title": item.get("section_title", ""),
            "text": item.get("section_desc", ""),
            "type": "law_section"
        })
    return standardized


def standardize_crpc(data, law_code):
    """Standardize CrPC format"""
    standardized = []
    for item in data:
        section_num = item.get("section", "")
        standardized.append({
            "id": f"{law_code.lower()}_{section_num}",
            "law": law_code,
            "law_name": LAW_METADATA[law_code.lower()]["name"],
            "chapter": str(item.get("chapter", "")),
            "chapter_title": "",
            "section": str(section_num),
            "title": item.get("section_title", ""),
            "text": item.get("section_desc", ""),
            "type": "law_section"
        })
    return standardized


def standardize_cpc(data, law_code):
    """Standardize CPC format"""
    standardized = []
    for item in data:
        section_num = item.get("section", "")
        standardized.append({
            "id": f"{law_code.lower()}_{section_num}",
            "law": law_code,
            "law_name": LAW_METADATA[law_code.lower()]["name"],
            "chapter": "",
            "chapter_title": "",
            "section": str(section_num),
            "title": item.get("title", ""),
            "text": item.get("description", ""),
            "type": "law_section"
        })
    return standardized


def standardize_iea(data, law_code):
    """Standardize IEA format"""
    standardized = []
    for item in data:
        section_num = item.get("section", "")
        standardized.append({
            "id": f"{law_code.lower()}_{section_num}",
            "law": law_code,
            "law_name": LAW_METADATA[law_code.lower()]["name"],
            "chapter": str(item.get("chapter", "")),
            "chapter_title": "",
            "section": str(section_num),
            "title": item.get("section_title", ""),
            "text": item.get("section_desc", ""),
            "type": "law_section"
        })
    return standardized


def standardize_mva(data, law_code):
    """Standardize MVA format"""
    standardized = []
    for item in data:
        section_num = item.get("section", "")
        standardized.append({
            "id": f"{law_code.lower()}_{section_num}",
            "law": law_code,
            "law_name": LAW_METADATA[law_code.lower()]["name"],
            "chapter": "",
            "chapter_title": "",
            "section": str(section_num),
            "title": item.get("title", ""),
            "text": item.get("description", ""),
            "type": "law_section"
        })
    return standardized


def standardize_nia(data, law_code):
    """Standardize NIA format"""
    standardized = []
    for item in data:
        section_num = item.get("section", "")
        standardized.append({
            "id": f"{law_code.lower()}_{section_num}",
            "law": law_code,
            "law_name": LAW_METADATA[law_code.lower()]["name"],
            "chapter": str(item.get("chapter", "")),
            "chapter_title": "",
            "section": str(section_num),
            "title": item.get("section_title", ""),
            "text": item.get("section_desc", ""),
            "type": "law_section"
        })
    return standardized


def standardize_ida(data, law_code):
    """Standardize IDA format"""
    standardized = []
    for item in data:
        section_num = item.get("section", "")
        standardized.append({
            "id": f"{law_code.lower()}_{section_num}",
            "law": law_code,
            "law_name": LAW_METADATA[law_code.lower()]["name"],
            "chapter": "",
            "chapter_title": "",
            "section": str(section_num),
            "title": item.get("title", ""),
            "text": item.get("description", ""),
            "type": "law_section"
        })
    return standardized


def standardize_hma(data, law_code):
    """Standardize HMA format (needs special handling due to malformed data)"""
    standardized = []
    # HMA has malformed structure - skip for now or handle specially
    print(f"⚠️  Warning: {law_code} has malformed structure. Skipping...")
    return standardized


# Dispatcher for different law formats
STANDARDIZERS = {
    "ipc": standardize_ipc,
    "crpc": standardize_crpc,
    "cpc": standardize_cpc,
    "iea": standardize_iea,
    "mva": standardize_mva,
    "nia": standardize_nia,
    "ida": standardize_ida,
    "hma": standardize_hma,
}


def process_law_file(law_code):
    """Process a single law file"""
    input_file = RAW_DIR / f"{law_code.lower()}.json"
    output_file = PROCESSED_DIR / f"{law_code.lower()}_standardized.json"
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        return
    
    print(f"📄 Processing {law_code.upper()}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get the appropriate standardizer
        standardizer = STANDARDIZERS.get(law_code.lower())
        if not standardizer:
            print(f"❌ No standardizer found for {law_code}")
            return
        
        # Standardize the data
        standardized_data = standardizer(data, law_code.upper())
        
        if not standardized_data:
            print(f"⚠️  No data standardized for {law_code}")
            return
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standardized_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {law_code.upper()} standardized: {len(standardized_data)} sections")
        print(f"   Saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error processing {law_code}: {str(e)}")


def create_combined_dataset():
    """Combine all standardized laws into a single dataset"""
    print("\n📦 Creating combined dataset...")
    
    combined = []
    for law_code in LAW_METADATA.keys():
        standardized_file = PROCESSED_DIR / f"{law_code}_standardized.json"
        if standardized_file.exists():
            with open(standardized_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                combined.extend(data)
    
    output_file = PROCESSED_DIR / "all_laws_combined.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Combined dataset created: {len(combined)} total sections")
    print(f"   Saved to: {output_file}")


def main():
    """Main execution"""
    print("=" * 60)
    print("KanoonGPT - Data Standardization Script")
    print("=" * 60)
    
    # Process each law
    for law_code in LAW_METADATA.keys():
        process_law_file(law_code)
        print()
    
    # Create combined dataset
    create_combined_dataset()
    
    print("\n" + "=" * 60)
    print("✅ Data standardization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
