import re

markdown_path = "data/processed/spring_boot.md"

with open(markdown_path, "r", encoding="utf-8") as file:
    md_text = file.read()

lines = md_text.splitlines()

tables = []
i = 0

while i < len(lines) - 1:
    # Markdown table header + separator
    if (
        lines[i].strip().startswith("|")
        and i + 1 < len(lines)
        and re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", lines[i + 1])
    ):
        start = i
        header = lines[i].strip()

        i += 2

        while i < len(lines) and lines[i].strip().startswith("|"):
            i += 1

        end = i - 1

        tables.append({
            "start": start + 1,
            "end": end + 1,
            "rows": end - start,
            "header": header
        })
    else:
        i += 1

print("Total tables found:", len(tables))

print("\n" + "=" * 100)
print("TABLE SUMMARY")
print("=" * 100)

for index, table in enumerate(tables, start=1):
    print(
        f"Table {index:3} | "
        f"Lines {table['start']:5}-{table['end']:5} | "
        f"Rows: {table['rows']:4} | "
        f"Header: {table['header'][:150]}"
    )