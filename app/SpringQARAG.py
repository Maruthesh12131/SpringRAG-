
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import chromadb
import re

class Chunk:
    def __init__(self, text):
        self.text = text


# --------------------------------------------------
# 1. LOAD PDF + E5 MODEL
# --------------------------------------------------

with open("data/processed/spring_boot.md", "r", encoding="utf-8") as file:
    markdown_text = file.read()

print("Markdown loaded successfully!")
print("Characters:", len(markdown_text))

tokenizer = AutoTokenizer.from_pretrained(
    "intfloat/e5-small-v2"
)

embedding_model = AutoModel.from_pretrained(
    "intfloat/e5-small-v2"
)




# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

chunk_size = 400


def count_tokens(text):

    return len(
        tokenizer(
            text,
            add_special_tokens=True,
            truncation=False
        )["input_ids"]
    )




# --------------------------------------------------
# 3. STRUCTURE-AWARE CHUNKING
# --------------------------------------------------

# Split Markdown into chapters
chapters = []
current_chapter = "General"
current_content = []

for line in markdown_text.splitlines():

    # A ## heading marks the beginning of a new chapter
    if re.match(r"^##\s+", line):

        # Save the previous chapter
        if current_content:
            chapters.append({
                "title": current_chapter,
                "content": "\n".join(current_content).strip()
            })

        # Start the new chapter
        current_chapter = re.sub(r"^##\s+", "", line).strip()
        current_content = []

    else:
        # ###, ####, etc. remain inside the current chapter
        current_content.append(line)

# Save the final chapter
if current_content:
    chapters.append({
        "title": current_chapter,
        "content": "\n".join(current_content).strip()
    })

print("Chapters found:", len(chapters))


# Create chunks chapter by chapter
chunks = []

chunk_size = 400
overlap = 50
step = chunk_size - overlap

for chapter in chapters:

    chapter_title = chapter["title"]
    chapter_content = chapter["content"]

    tokens = tokenizer.encode(
        chapter_content,
        add_special_tokens=False
    )

    start = 0

    while start < len(tokens):

        chunk_tokens = tokens[start:start + chunk_size]

        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True
        )

        chunks.append(
            Chunk(
                text=f"{chapter_title}\n\n{chunk_text}"
            )
        )

        start += step
# --------------------------------------------------
# 5. INSPECT CHUNKS BEFORE EMBEDDING
# --------------------------------------------------

print("\nTotal chunks:", len(chunks))


for i, chunk in enumerate(chunks[:10]):

    print("\n" + "=" * 80)

    print("Chunk:", i)

    print("Section:", chunk.text.split("\n\n")[0])

    print("Tokens:", count_tokens(chunk.text))

    print("Text:")

    print(chunk.text[:500])


# --------------------------------------------------
# 6. CHECK ALL CHUNK TOKEN COUNTS
# --------------------------------------------------

print(
    "\nChecking all chunk token counts..."
)

over_512 = 0

under_or_equal_512 = 0


for i, chunk in enumerate(chunks):

    token_count = count_tokens(
        "passage: " + chunk.text
    )

    if token_count > 512:

        over_512 += 1

        print(
            "Chunk:",
            i,
            "| Tokens:",
            token_count,
        )

    else:

        under_or_equal_512 += 1


print(
    "Chunks with more than 512 tokens:",
    over_512
)

print(
    "Chunks with 512 or fewer tokens:",
    under_or_equal_512
)


# --------------------------------------------------
# 7. CREATE CHROMA COLLECTION
# --------------------------------------------------

chroma_client = chromadb.PersistentClient(
    path="data/chroma"
)

try:
    chroma_client.delete_collection(
        name="spring_boot_docs"
    )
    print("Old Chroma collection deleted.")
except Exception:
    print("No existing Chroma collection found.")

collection = chroma_client.create_collection(
    name="spring_boot_docs"
)

print("New Chroma collection created.")

# --------------------------------------------------
# 8. CREATE EMBEDDINGS
# --------------------------------------------------
batch_size = 16
all_outputs = []

print(
    "\nCreating embeddings..."
)


for start in range(0, len(chunks), batch_size):

    batch_chunks = chunks[start:start + batch_size]

    batch_texts = [
        "passage: " + chunk.text
        for chunk in batch_chunks
    ]

    inputs = tokenizer(
        batch_texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    with torch.no_grad():

        outputs = embedding_model(
            **inputs
        )

        token_embeddings = outputs.last_hidden_state

        attention_mask = inputs["attention_mask"]

        mask = attention_mask.unsqueeze(-1)

        masked_embeddings = token_embeddings * mask

        sum_embeddings = masked_embeddings.sum(dim=1)

        sum_mask = mask.sum(dim=1)

        mean_embeddings = sum_embeddings / sum_mask

        normalized_embeddings = F.normalize(
            mean_embeddings,
            p=2,
            dim=1
        )

        all_outputs.extend(
            normalized_embeddings
        )

print(
    "Embeddings created:",
    len(all_outputs)
)


# --------------------------------------------------
# 9. STORE EMBEDDINGS IN CHROMA
# --------------------------------------------------

print(
    "\nStoring embeddings in Chroma..."
)

for i, chunk in enumerate(chunks):

    normalized_embedding = (
        all_outputs[i]
        .tolist()
    )

    collection.add(

        ids=[
            f"chunk_{i}"
        ],

        embeddings=[
            normalized_embedding
        ],

        documents=[
            chunk.text
        ],

        metadatas=[
            {
                "section":
                chunk.text.split(
                    "\n",
                    1
                )[0]
            }
        ]
    )

print(
    "Embeddings stored in Chroma."
)