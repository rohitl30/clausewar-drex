import asyncio
import os
import streamlit as st
from ndi_parser import parse_all_contracts
from swarm_engine import run_negotiation_swarm

st.set_page_config(page_title="ClauseWar · Drex + NDI Swarm", layout="wide")
st.title("ClauseWar: Sub-Second Multi-Agent Procurement Swarm")
st.caption("Powered by Nace Document Intelligence (NDI) + Drex Calibrated Decision Engine")

with st.sidebar:
    st.header("Authentication")
    api_key = st.text_input(
        "Nace API Key (nace_sk_...)",
        value=os.environ.get("NACE_API_KEY", ""),
        type="password",
        help="Get your key from console.nace.ai -> API Keys",
    ).strip()
    if api_key:
        st.caption(f"Key loaded: `{api_key[:10]}...` (length: {len(api_key)})")

if "parsed_docs" not in st.session_state:
    st.session_state.parsed_docs = None

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. NDI Document Ingestion")
    uploaded = st.file_uploader("Upload RFP & Vendor PDFs (or use preloaded sample contracts)", accept_multiple_files=True, type=["pdf"])
    if st.button("Parse Contracts with NDI", use_container_width=True):
        if not api_key or not api_key.startswith("nace_sk_"):
            st.error("Please enter a valid API key starting with `nace_sk_` in the left sidebar.")
        else:
            with st.spinner("Running Nace Document Intelligence (Perception Layer)..."):
                if uploaded:
                    os.makedirs("uploaded_docs", exist_ok=True)
                    paths = []
                    for f in uploaded:
                        p = os.path.join("uploaded_docs", f.name)
                        with open(p, "wb") as out:
                            out.write(f.read())
                        paths.append(p)
                else:
                    paths = [os.path.join("sample_docs", f) for f in sorted(os.listdir("sample_docs"))]
                st.session_state.parsed_docs = asyncio.run(parse_all_contracts(paths, api_key=api_key))

    if st.session_state.parsed_docs:
        for d in st.session_state.parsed_docs:
            with st.expander(f"{d['file']} ({d['ndi_latency_ms']} ms)"):
                st.markdown(d["markdown"])

with col2:
    st.subheader("2. Drex Multi-Agent Negotiation Arena")
    rounds = st.slider("Max Negotiation Rounds", 3, 12, 6)
    if st.button("Launch Drex Swarm Negotiation", type="primary", use_container_width=True):
        if not st.session_state.parsed_docs:
            st.warning("Click 'Parse Contracts with NDI' first!")
        else:
            rfp_md = next((d["markdown"] for d in st.session_state.parsed_docs if "RFP" in d["file"]), st.session_state.parsed_docs[0]["markdown"])
            vendor_map = {
                "Apex Compute": next((d["markdown"] for d in st.session_state.parsed_docs if "VendorA" in d["file"]), ""),
                "Nebula Scale": next((d["markdown"] for d in st.session_state.parsed_docs if "VendorB" in d["file"]), ""),
                "BudgetNode": next((d["markdown"] for d in st.session_state.parsed_docs if "VendorC" in d["file"]), ""),
            }
            with st.spinner("Executing multi-agent calibrated decisions..."):
                offers, logs, total_ms, calls = asyncio.run(run_negotiation_swarm(rfp_md, vendor_map, max_rounds=rounds, api_key=api_key))

            avg_ms = round(total_ms / max(calls, 1), 1)
            est_llm_sec = round((calls * 950) / 1000, 1)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Drex Decisions Made", calls)
            m2.metric("Avg Drex Latency", f"{avg_ms} ms")
            m3.metric("Total Swarm Time", f"{round(total_ms/1000, 2)} s")
            m4.metric("Est. Frontier LLM Time", f"~{est_llm_sec} s", delta=f"{round((calls*950)/max(total_ms,1), 1)}x faster")

            winner = next((o for o in offers if o.status == "WON"), None)
            if winner:
                st.success(f"AWARDED TO {winner.vendor.upper()} — ${winner.price:,.0f} | {winner.sla}% SLA | {winner.payment_terms} | {winner.delivery_days}d delivery")
            else:
                st.info("Negotiation completed — review final Pareto-optimal offers below.")

            st.dataframe(logs, use_container_width=True)
