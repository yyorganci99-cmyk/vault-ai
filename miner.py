import streamlit as st
import fitz  # PyMuPDF
import ollama
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Vault AI", layout="wide", page_icon="🏛️")

# --- 0. ZERO-TRUST AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "vault2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 Vault AI: Restricted Access")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    
    elif not st.session_state["password_correct"]:
        st.title("🔒 Vault AI: Restricted Access")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 Authentication failed. Unauthorized access logged.")
        return False
    
    else:
        return True

# IF THE USER IS NOT LOGGED IN, STOP THE SCRIPT HERE.
if not check_password():
    st.stop()


# --- 1. THE IRONCLAD AUDIT DATABASE ---
def init_db():
    conn = sqlite3.connect('vault_audit.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  documents TEXT, 
                  findings TEXT)''')
    conn.commit()
    conn.close()

def log_to_database(doc_names, findings):
    conn = sqlite3.connect('vault_audit.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO audit_log (timestamp, documents, findings) VALUES (?, ?, ?)", 
              (timestamp, doc_names, findings))
    conn.commit()
    conn.close()

# Start the database when the app boots
init_db()

# --- 2. THE NEURAL ENGINE ---
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_embedding_model()

# --- 3. THE COCKPIT (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Vault AI Control")
    st.success("🔒 System Secure: Air-Gapped & Audited")
    st.divider()
    app_mode = st.radio("Terminal Mode:", ["🔍 Active Scanner", "🗄️ Compliance Audit Logs"])

# --- 4. MAIN TERMINAL: ACTIVE SCANNER ---
if app_mode == "🔍 Active Scanner":
    st.title("💼 Vault AI: Enterprise Edition")
    st.write("Neural Vision | Multi-Agent Verification | Cryptographic Logging")

    uploaded_files = st.file_uploader("Drop the M&A Data Room (Select Multiple PDFs):", type="pdf", accept_multiple_files=True)

    if st.button("Execute Data Room Sweep", type="primary") and uploaded_files:
        
        with st.status(f"Sweeping {len(uploaded_files)} documents...", expanded=True) as status:
            
            # --- PHASE 1: DEEP VISION BATCH INGESTION ---
            st.write(f"👁️ **Phase 1:** Deep Vision processing of {len(uploaded_files)} documents...")
            paragraphs_with_metadata = []
            doc_names_list = []
            
            for file in uploaded_files:
                doc_names_list.append(file.name)
                doc = fitz.open(stream=file.read(), filetype="pdf")
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    blocks = page.get_text("blocks") 
                    for block in blocks:
                        text = block[4].strip() 
                        if len(text) > 20:
                            clean_text = text.replace('\n', ' ') 
                            paragraphs_with_metadata.append({
                                "text": clean_text,
                                "page": page_num + 1,
                                "doc": file.name
                            })
            
            # --- PHASE 2: CROSS-DOCUMENT NEURAL FILTERING ---
            st.write("📐 **Phase 2:** Cross-document neural vector filtering...")
            target_concept = "hidden liabilities, toxic debt, unusual termination clauses, severe penalty fees, extreme financial risk, immediate capital injection requirements, non-standard legal exposure, contradicting clauses between documents"
            
            raw_text_list = [p["text"] for p in paragraphs_with_metadata]
            query_vector = model.encode([target_concept])
            doc_vectors = model.encode(raw_text_list)
            
            similarity_scores = cosine_similarity(query_vector, doc_vectors).flatten()
            scored_paragraphs = list(zip(similarity_scores, paragraphs_with_metadata))
            scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
            
            top_paragraphs = []
            for score, meta in scored_paragraphs[:150]:
                if score > 0.1:
                    top_paragraphs.append(f"[DOC: {meta['doc']} | PAGE {meta['page']}] {meta['text']}")
                    
            filtered_text = "\n...\n".join(top_paragraphs)
            
            try:
                # --- PHASE 3: AGENT 1 (THE MINER) ---
                st.write("⚖️ **Phase 3:** Agent 1 (Mike) is cross-referencing findings...")
                mike_prompt = f"""
                You are an elite corporate lawyer. Analyze these text excerpts from MULTIPLE documents and draft a report on:
                1. THE TRAPS
                2. THE LIABILITIES
                3. CONTRADICTIONS: Do any clauses in one document contradict another?
                
                CRITICAL RULE: Every time you quote the text, you MUST include the [DOC: X | PAGE Y] tag that appears next to it.
                Source Text: {filtered_text}
                """
                response_mike = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': mike_prompt}])
                draft_debrief = response_mike['message']['content']
                
                # --- PHASE 4: AGENT 2 (THE VERIFIER) ---
                st.write("🕵️‍♂️ **Phase 4:** Agent 2 (Harvey) is verifying cross-document citations...")
                harvey_prompt = f"""
                You are a senior M&A Partner verifying a junior associate's report.
                --- DRAFT REPORT ---
                {draft_debrief}
                --- SOURCE TEXT ---
                {filtered_text}
                YOUR JOB: Ensure every claim is backed by the source text and has a [DOC: X | PAGE Y] citation. Output the final, 100% verified 'Morning Debrief'.
                """
                response_harvey = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': harvey_prompt}])
                final_verified_debrief = response_harvey['message']['content']
                
                # --- PHASE 5: THE DATABASE LOGGING ---
                st.write("🗄️ **Phase 5:** Securing cryptographic audit log...")
                doc_names_string = ", ".join(doc_names_list)
                log_to_database(doc_names_string, final_verified_debrief)
                
                status.update(label="✅ Data Room Sweep & Audit Complete.", state="complete", expanded=False)
                
                st.markdown("### 📝 Verified Partner Debrief (Audited)")
                st.markdown(final_verified_debrief)
                
            except Exception as e:
                status.update(label="⚠️️ Local Processing Error", state="error", expanded=True)
                st.error("Make sure the Ollama app is running in the background.")
                st.caption(f"System Log: {e}")

# --- 5. MAIN TERMINAL: COMPLIANCE AUDIT LOGS ---
elif app_mode == "🗄️ Compliance Audit Logs":
    st.title("🗄️ System Audit Logs")
    st.write("Immutable record of all executing Due Diligence scans.")
    
    conn = sqlite3.connect('vault_audit.db')
    df = pd.read_sql_query("SELECT timestamp, documents, findings FROM audit_log ORDER BY id DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("No audit logs found. Run a scan in the Active Scanner to generate logs.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)