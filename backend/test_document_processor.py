from app.services.document_processor import extract_text


file_path = input("Enter the path of your PDF/DOCX file: ").strip()

try:
    text = extract_text(file_path)

    print("\n========== EXTRACTED TEXT ==========\n")
    print(text[:5000])

    print("\n====================================")
    print(f"Total characters extracted: {len(text)}")

except Exception as error:
    print(f"\nERROR: {error}")