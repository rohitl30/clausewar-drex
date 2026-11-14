# ⚔️ ClauseWar: Sub-Second Multi-Agent Procurement Swarm

**Built for Drexathon: Nace AI's Decision Model Hackathon × Adobe EDU**  
**Track:** Swarm Intelligence

ClauseWar is an automated, sub-second multi-agent procurement negotiation arena powered by **Drex calibrated decision models (`system_one`)** and grounded in real-world unstructured contracts via **Nace Document Intelligence (NDI)**.

---

## 🎯 The Problem
Enterprise procurement relies on comparing complex Request for Proposal (RFP) constraints against competing vendor quotes buried in unstructured PDFs. Running multi-agent negotiations on traditional frontier generative LLMs fails in production due to:
1. **Latency Bottlenecks:** Autoregressive LLM turns take ~950–1,500 ms each, causing multi-round, multi-vendor negotiations to stall.
2. **Clause Hallucination:** Chat-based agents frequently drift or overlook hard fine-print constraints (minimum uptime SLAs, Net-60 payment terms, delivery deadlines).
3. **Lack of Auditability:** Free-form text exchanges lack calibrated confidence or compliance probabilities for enterprise governance.

---

## 🏗️ System Architecture

ClauseWar decouples **document perception** from **calibrated tactical decision-making**:

1. **Perception Layer — Nace Document Intelligence (NDI):**
   - Ingests raw, unstructured PDFs (`RFP_Requirements.pdf` and competing vendor proposals) via `client.documents.upload` and `client.documents.parse`.
   - Extracts verified, grounded Markdown rules (budget ceilings, uptime SLAs, penalty credits, payment schedules, and delivery windows).
2. **Swarm Decision Layer — Drex `system_one` Engine:**
   - Spawns 4 autonomous agents (**1 Enterprise Buyer** + **3 Vendors**: *Apex Compute*, *Nebula Scale*, and *BudgetNode*).
   - Executes parallel forward-pass decisions per round using Drex primitives:
     - **`Choice`**: Selects the optimal tactical move (`ACCEPT`, `COUNTER_PRICE`, `COUNTER_TERMS`, or `WALK_AWAY`).
     - **`Noul`**: Evaluates calibrated probability (`compliant_prob`) that an offer satisfies all hard RFP constraints.
     - **`Score`**: Rates overall commercial attractiveness across price, SLA, payment terms, and delivery speed.
3. **Interactive War-Room Dashboard (`app.py`):**
   - Built in Streamlit with real-time NDI parsing expanders, per-decision latency telemetry, frontier LLM speedup comparisons, and a full round-by-round audit ledger.

---

## 📊 Measured Benchmark Evidence

In our end-to-end benchmark run across 4 PDFs and 4 negotiating agents:

| Metric | Measured Result |
| :--- | :--- |
| **Total Drex Decisions Executed** | **11 calibrated forward passes** |
| **Average Drex Decision Latency** | **308.8 ms** per decision |
| **Total Multi-Agent Swarm Time** | **3.4 seconds** (vs. ~10.4 s estimated frontier LLM chain) |
| **End-to-End Speedup** | **3.1× faster** |
| **Winning Outcome** | **BudgetNode — $445,000 \| 99.9% SLA \| Net-60 \| 14d delivery** |

### Why This Proves Calibrated Intelligence
* **Round 1 Trap Avoided:** *BudgetNode* submitted the lowest initial bid (`$445,000`), but violated the RFP's hard constraints (`99.5%` SLA, `50% Upfront` payment, `21-day` delivery). Drex flagged this immediately with `compliant_prob = 0.000`.
* **Targeted Term Counter:** Instead of blindly accepting the cheapest bid or walking away, the Buyer agent issued `COUNTER_TERMS` (`confidence: 0.886`), compelling BudgetNode to concede to `99.9% SLA`, `Net-60`, and `14-day` delivery while preserving the `$445,000` price.
* **Round 2 Auditable Award:** Once compliance was verified, the swarm closed and awarded the contract with a complete decision trace.

---

## 🎨 Visual Identity & Pitch Deck (Adobe EDU)
* **Custom Agent Badges (`assets/`):** Distinct minimalist vector badges created for the Enterprise Buyer and all three competing vendors (*Apex Compute*, *Nebula Scale*, *BudgetNode*).
* **Executive Presentation (`ClauseWar_Presentation.pdf`):** Designed with **Adobe Express** (SJSU EDU) featuring dark-slate visual hierarchy and live telemetry captures.

---

## 📂 Repository Structure

```text
clausewar-drex/
├── app.py               # Streamlit war-room UI & live benchmark telemetry
├── ndi_parser.py        # Async Nace Document Intelligence (NDI) PDF ingestion & parsing
├── swarm_engine.py      # Multi-agent Drex system_one negotiation loop (Choice, Noul, Score)
├── generate_docs.py     # Generates sample RFP & competing vendor proposal PDFs
├── sample_docs/         # Preloaded sample RFP & 3 vendor quote PDFs
├── assets/              # Custom agent badge icons for Buyer & Vendors
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## 🚀 Quickstart

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/<your-username>/clausewar-drex.git
cd clausewar-drex
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Your Nace API Key
Generate an API key (`nace_sk_...`) from [console.nace.ai](https://console.nace.ai) and set it in your environment (or paste it directly into the Streamlit sidebar):
```powershell
$env:NACE_API_KEY="nace_sk_your_secret_key_here"
```

### 3. Generate Sample Contracts & Launch the Swarm Arena
```bash
python generate_docs.py
streamlit run app.py
```
Open `http://localhost:8501`, click **Parse Contracts with NDI**, and then click **Launch Drex Swarm Negotiation**.
