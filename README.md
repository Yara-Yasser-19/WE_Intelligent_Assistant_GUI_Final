# WE Intelligent Assistant — Desktop GUI RAG PoC

## What this project is
A desktop Proof of Concept for the Telecom Egypt Intelligent Assistant case study.

The interface is a normal desktop GUI built with **CustomTkinter**. It does not use a browser, localhost, Streamlit, or Gradio.

## Main files
- `app.py` — GUI
- `rag_engine.py` — retrieval / grounded answer logic
- `plans.json` — structured plan catalog
- `knowledge/` — local Telecom Egypt knowledge
- `RAG_Notebook.ipynb` — notebook explanation
- `requirements.txt` — required Python packages

## Run
Open the extracted folder in PyCharm.

Install packages once:
```bash
pip install -r requirements.txt
```

Then run:
```bash
python app.py
```

Or simply press the green **Run** button in PyCharm.

## Features
- Modern WE-branded desktop dashboard
- Smart Assistant
- English / Arabic / simple Egyptian-dialect normalization
- Structured plan explorer
- Local RAG-style retrieval
- Source names displayed with answers
- PDF / DOCX / TXT / HTML / Markdown uploads
- Knowledge-base viewer
- Architecture page

## RAG workflow
1. Load knowledge.
2. Clean text.
3. Split into overlapping chunks.
4. Normalize the user query.
5. Retrieve the best matching chunks.
6. Return a grounded answer.
7. Display sources.

## Important implementation note
This is intentionally a lightweight local PoC. It does not pretend to use a generative LLM. For production, the same retrieval flow can be upgraded with multilingual embeddings, a vector database such as FAISS/Chroma, and an on-premises LLM.

## Data
The included plan catalog was prepared from official Telecom Egypt pages and includes source URLs in `plans.json` and each knowledge file. Always verify live commercial prices before production use because telecom offers can change.
