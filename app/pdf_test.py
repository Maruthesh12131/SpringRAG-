import pymupdf4llm
import re


pdf_path = "data/raw/spring-boot-reference.pdf"
output_path = "data/processed/spring_boot.md"


# Extract pages 21 onwards
md_text = pymupdf4llm.to_markdown(
    pdf_path,
    pages=list(range(26, 974))
)


# Remove standalone page numbers
md_text = re.sub(r"(?m)^\s*\d+\s*$\n?", "", md_text)
print("\nSearching for possible terminal/log OCR...")

md_text = re.sub(
    r"(?s)\n?A running remote client might resemble the following listing:\s*"
    r".*?:: Spring Boot Remote :: \(v3\.2\.10\)\s*"
    r".*?seconds \(process running for 3\.411\)\s*",
    "\n",
    md_text
)

# Remove generated Javadoc index tables
md_text = re.sub(
    r"(?ms)\n*\|Configuration Class\|Links\|\n"
    r"\|---\|---\|\n"
    r"(?:\|.*?\|javadoc\|\n?)+",
    "\n",
    md_text
)

# Save cleaned Markdown
with open(output_path, "w", encoding="utf-8") as file:
    file.write(md_text)


print("Extraction completed!")
print("Cleaned Markdown saved to:", output_path)