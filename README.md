# Vault AI: Air-Gapped Agentic RAG for M&A Due Diligence

## 📌 Business Value
Mergers and Acquisitions (M&A) due diligence traditionally requires analysts to spend hundreds of hours manually parsing massive corporate documents (SEC 10-Ks, employment contracts, vendor agreements). Vault AI automates this bottleneck using a 100% local, air-gapped Agentic RAG (Retrieval-Augmented Generation) pipeline. It identifies hidden liabilities, unusual termination clauses, and critical negotiation leverage in seconds. By utilizing local large language models and a dual-agent verification system, Vault AI ensures absolute data privacy and cryptographic auditability without the risk of hallucinations.

## 🏗️ System Architecture
The pipeline is designed for high-stakes financial environments where data privacy is mandatory. It processes documents locally, filtering noise through neural embeddings before passing high-risk semantic chunks to an adversarial dual-agent system.

```mermaid
graph TD
    A[Raw SEC 10-K & Contracts] -->|PyMuPDF| B[Layout-Preserving Text Extraction]
    B -->|all-MiniLM-L6-v2| C[(Local Vector Space)]
    C -->|Cosine Similarity Math| D[Top 150 High-Risk Chunks]
    D --> E[Agent 1: The Miner]
    E -->|Drafts Vulnerability Report| F[Agent 2: The Verifier]
    F -->|Strict Fact-Checking & Citation| G[Final Verified Debrief]
    G --> H[(SQLite Cryptographic Audit Log)]
    G --> I[Streamlit Dashboard]
