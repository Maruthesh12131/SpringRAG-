Spring Boot Documentation RAG Assistant
A Retrieval-Augmented Generation (RAG) application that answers Spring Boot questions using the official Spring Boot reference documentation as its knowledge source.

The project demonstrates a complete RAG pipeline: PDF extraction, document chunking, E5 embeddings, vector storage/retrieval with ChromaDB, and answer generation with Google Gemini.

Architecture

flowchart LR
    A[Spring Boot Reference PDF]
    B[PyMuPDF4LLM]
    C[Markdown]
    D[Chapter-wise Chunking]
    E[E5-small-v2 Embeddings]
    F[Mean Pooling + L2 Normalization]
    G[ChromaDB]

    Q[User Question]
    QE[E5-small-v2 Query Embedding]
    R[Similarity Search]
    X[Top Retrieved Chunks + Neighbor Context]
    P[Prompt]
    L[Gemini 3.6 Flash]
    ANS[Generated Answer]

    A --> B --> C --> D --> E --> F --> G
    Q --> QE --> R
    G --> R
    R --> X --> P
    Q --> P
    P --> L --> ANS

How It Works

1. Document Processing

The Spring Boot reference PDF is converted into Markdown using PyMuPDF4LLM.

Markdown is used because it preserves useful document structure such as headings, lists, tables, and code blocks.

PDF
 ↓
PyMuPDF4LLM
 ↓
Markdown

2. Chunking

The extracted Markdown is divided into chapters using ## headings.

Each chapter is then split into:

400-token chunks

50-token overlap

No overlap across chapter boundaries

The chapter title is added to each chunk as additional context

This produced approximately 1,300 chunks from the processed documentation.

3. Embeddings

The project uses:

intfloat/e5-small-v2

The document chunks are embedded using the E5 passage: prefix, while user questions use the query: prefix.

The embedding process uses:

Tokenization

Model inference

Attention-mask mean pooling

L2 normalization

The resulting vectors are stored in ChromaDB.

4. Vector Storage and Retrieval

ChromaDB is used to store the document embeddings and perform similarity search.

When a user asks a question:

User Question
     ↓
E5 Query Embedding
     ↓
ChromaDB Similarity Search
     ↓
Top-K Retrieved Chunks

The retriever also expands the most relevant retrieved chunks with their neighboring chunks. This helps preserve surrounding documentation context when a relevant passage spans multiple chunks.

The current generation pipeline uses the top retrieved results and expands context around the top results rather than expanding every retrieved result.

5. Answer Generation

The retrieved context and the original question are combined into a prompt and sent to Google Gemini 3.6 Flash.

The model is instructed to answer using only the supplied Spring Boot documentation context.

If the required information cannot be found in the provided context, the model is instructed to return:

I couldn't find the answer in the provided Spring Boot documentation.

Project Structure

project-03-RAG/
│
├── app/
│   ├── pdf_test.py
│   ├── SpringQARAG.py
│   ├── query.py
│   └── generation.py
│
├── data/
│   ├── raw/
│   │   └── spring-boot-reference.pdf
│   │
│   ├── processed/
│   │   └── spring_boot.md
│   │
│   └── chroma/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt

Technologies Used

Component

Technology

Language

Python

PDF → Markdown

PyMuPDF4LLM

Tokenization

Hugging Face Transformers

Embedding Model

intfloat/e5-small-v2

Vector Database

ChromaDB

LLM

Google Gemini 3.6 Flash

Environment Variables

python-dotenv

Setup

1. Clone the repository

git clone <your-repository-url>
cd project-03-RAG

2. Create and activate a virtual environment

python -m venv .venv
source .venv/bin/activate

On Windows:

.venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure the Gemini API key

Create a .env file in the project root:

GEMINI_API_KEY=your_gemini_api_key_here

Do not commit the .env file to GitHub.

A .env.example file is included as a template.

Running the Pipeline

Step 1 — Extract the PDF

Run:

python app/pdf_test.py

This converts the Spring Boot reference PDF into Markdown.

Output:

data/processed/spring_boot.md

Step 2 — Create embeddings and populate ChromaDB

Run:

python app/SpringQARAG.py

This:

Loads the processed Markdown

Splits it into chapters

Creates token-based chunks

Generates E5 embeddings

Stores the embeddings and documents in ChromaDB

Step 3 — Ask questions

Run:

python app/query.py

Example:

Ask your Spring boot questions here: What is Spring Boot Actuator?

The system retrieves relevant documentation and generates an answer using Gemini.

Retriever Evaluation

The retriever was evaluated using Spring Boot questions covering different topics, including:

Dependency Injection

Spring Bean Creation

Auto-Configuration

Spring Boot Actuator

Spring Security Architecture

The evaluation showed that the retriever can locate the correct semantic region of the documentation, especially for focused questions.

A key observation was that broad questions can produce semantically related but irrelevant chunks. Neighbor expansion improves context when the correct chunk is retrieved, but expanding too many retrieved results can introduce excessive noise for the LLM.

This is an important limitation of the current baseline and an area that could be improved with techniques such as reranking, hybrid retrieval, or better query handling.

Limitations

This project is intentionally a practical RAG baseline rather than a production-ready system.

Current limitations include:

Retrieval quality can decrease for broad or ambiguous questions.

Semantic similarity can return related but irrelevant documentation.

The current system uses dense vector retrieval without BM25/hybrid search.

There is no dedicated reranker.

The source documentation is a static PDF snapshot.

The application currently uses a command-line interface.

Future Improvements

Possible improvements include:

Add a reranking stage

Experiment with hybrid BM25 + dense retrieval

Improve query expansion/decomposition

Add metadata-based filtering

Add a web UI

Add automated evaluation metrics

Add conversational memory

Use a newer or larger embedding model where appropriate

Key Learning

This project demonstrates the core RAG workflow:

Document
   ↓
Extract
   ↓
Chunk
   ↓
Embed
   ↓
Store
   ↓
Retrieve
   ↓
Build Context
   ↓
Generate

The project also highlights an important RAG principle:

A strong language model cannot reliably answer from information that the retriever fails to provide.

Therefore, evaluating the retrieval layer separately from generation is an important part of building a reliable RAG system.

License

This project is intended for learning and demonstration purposes.