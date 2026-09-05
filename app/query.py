import torch
import torch.nn.functional as F
import chromadb
from transformers import AutoTokenizer, AutoModel
from generation import generate_answer

# --------------------------------------------------
# 8. RETRIEVAL
# --------------------------------------------------

query = input("Ask your Spring boot questions here:")
tokenizer = AutoTokenizer.from_pretrained(
    "intfloat/e5-small-v2"
)

embedding_model = AutoModel.from_pretrained(
    "intfloat/e5-small-v2"
)

chroma_client = chromadb.PersistentClient(
    path="data/chroma"
)

collection = chroma_client.get_collection(
    name="spring_boot_docs"
)

print("Vectors in Chroma:", collection.count())

# Add E5 query prefix
query_text = "query: " + query


# Tokenize query
query_inputs = tokenizer(
    query_text,
    return_tensors="pt"
)


print(
    "\nQuery tokens:",
    len(query_inputs["input_ids"][0])
)


# Generate query hidden states
with torch.no_grad():

    query_outputs = embedding_model(
        **query_inputs
    )


# --------------------------------------------------
# 9. MEAN POOLING FOR QUERY
# --------------------------------------------------

query_token_embeddings = (
    query_outputs.last_hidden_state
)

query_attention_mask = (
    query_inputs["attention_mask"]
)

query_mask = (
    query_attention_mask.unsqueeze(-1)
)

query_masked_embeddings = (
    query_token_embeddings * query_mask
)

query_sum_embeddings = (
    query_masked_embeddings.sum(dim=1)
)

query_sum_mask = (
    query_mask.sum(dim=1)
)

query_mean_embeddings = (
    query_sum_embeddings / query_sum_mask
)


# --------------------------------------------------
# 10. NORMALIZE QUERY EMBEDDING
# --------------------------------------------------

query_embedding = F.normalize(
    query_mean_embeddings,
    p=2,
    dim=1
)


# Convert [1, 384] → [384]
query_embedding = (
    query_embedding
    .squeeze(0)
    .tolist()
)


# --------------------------------------------------
# 11. SEARCH CHROMA
# --------------------------------------------------

results = collection.query(

    query_embeddings=[
        query_embedding
    ],

    n_results=10
)

retrieved_ids = results["ids"][0]

retrieved_distances = results["distances"][0]
retrieved_documents = results["documents"][0]
retrieved_metadatas = results["metadatas"][0]

print("\nOriginal retrieved chunks:")

print("\nOriginal retrieved chunks:")

for i in range(len(retrieved_ids)):

    print("\n" + "=" * 80)

    print("Rank:", i + 1)

    print("ID:", retrieved_ids[i])

    print("Distance:", retrieved_distances[i])

    print("Metadata:", retrieved_metadatas[i])

    print("Text:")
    print(retrieved_documents[i][:1000])

# --------------------------------------------------
# 8. EXPAND EACH CHUNK WITH NEIGHBORS
# --------------------------------------------------

expanded_chunk_ids = set()

for chunk_id in retrieved_ids[:3]:

    # Example:
    # chunk_39 → 39

    chunk_number = int(
        chunk_id.split("_")[1]
    )

    previous_chunk = chunk_number - 1
    next_chunk = chunk_number + 1

    # Add previous chunk
    if previous_chunk >= 0:

        expanded_chunk_ids.add(
            f"chunk_{previous_chunk}"
        )

    # Add retrieved chunk
    expanded_chunk_ids.add(
        f"chunk_{chunk_number}"
    )

    # Add next chunk
    expanded_chunk_ids.add(
        f"chunk_{next_chunk}"
    )


# --------------------------------------------------
# 9. SORT CHUNKS IN DOCUMENT ORDER
# --------------------------------------------------

expanded_chunk_ids = sorted(
    expanded_chunk_ids,
    key=lambda x: int(
        x.split("_")[1]
    )
)


# --------------------------------------------------
# 10. FETCH EXPANDED CHUNKS FROM CHROMA
# --------------------------------------------------

expanded_results = collection.get(
    ids=expanded_chunk_ids,
    include=[
        "documents",
        "metadatas"
    ]
)

context = "\n\n".join(
    expanded_results["documents"]
)
print("\nExpanded context:")

for i in range(
    len(expanded_results["ids"])
):

    print(
        "\n=============================="
    )

    print(
        "ID:",
        expanded_results["ids"][i]
    )

    print(
        "Pages:",
        expanded_results["metadatas"][i]
    )

    print(
        "Text:",
        expanded_results["documents"][i]
    )

answer = generate_answer(query, context)

print("\nAnswer:")
print(answer)