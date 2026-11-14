import asyncio
import os
import time
from dataclasses import dataclass, field
from nace_sdk import AsyncNaceClient, Choice, Noul, Score

@dataclass
class OfferState:
    vendor: str
    price: float
    sla: float
    payment_terms: str
    delivery_days: int
    status: str = "ACTIVE"
    history: list = field(default_factory=list)

async def drex_decide(client: AsyncNaceClient, agent_role: str, state_text: str) -> dict:
    t0 = time.perf_counter()
    res = await client.system_one(
        state=state_text,
        questions={
            "action": Choice(
                instructions=f"As {agent_role}, choose the optimal tactical move in this negotiation round.",
                criteria={
                    "ACCEPT": "Terms satisfy all hard constraints and maximize value; close the deal.",
                    "COUNTER_PRICE": "Demand or offer a 2.5% price reduction while keeping other terms.",
                    "COUNTER_TERMS": "Keep price steady but require better SLA (>=99.9%) or Net-60 terms.",
                    "WALK_AWAY": "Constraints are violated with no realistic path to agreement.",
                },
            ),
            "compliant": Noul(
                instructions="Does the current offer satisfy the RFP hard constraints (Budget <= $480k, SLA >= 99.9%, Delivery <= 14 days)?"
            ),
            "deal_score": Score(
                instructions="Rate overall commercial attractiveness of this offer.",
                criteria=["Unacceptable", "Weak", "Acceptable", "Strong", "Optimal"],
            ),
        },
    )
    ms = round((time.perf_counter() - t0) * 1000, 1)
    return {
        "action": res.choices["action"].choice,
        "action_probs": res.choices["action"].probabilities,
        "compliant_prob": round(res.nouls["compliant"].noul, 3),
        "deal_score": round(res.scores["deal_score"].score, 2),
        "latency_ms": ms,
    }

async def run_negotiation_swarm(rfp_context: str, vendor_contexts: dict, max_rounds: int = 8, api_key: str | None = None):
    key = (api_key or os.environ.get("NACE_API_KEY", "")).strip()
    offers = [
        OfferState("Apex Compute", 510000, 99.95, "Net-30", 7),
        OfferState("Nebula Scale", 492000, 99.90, "Net-60", 12),
        OfferState("BudgetNode", 445000, 99.50, "50% Upfront", 21),
    ]
    logs = []
    total_drex_ms = 0.0
    total_calls = 0

    async with AsyncNaceClient(api_key=key) as client:
        for rnd in range(1, max_rounds + 1):
            active = [o for o in offers if o.status == "ACTIVE"]
            if not active:
                break

            buyer_tasks = []
            for offer in active:
                state = (
                    f"ROUND {rnd}/{max_rounds}\n"
                    f"RFP CONSTRAINTS:\n{rfp_context}\n\n"
                    f"CURRENT OFFER FROM {offer.vendor}:\n"
                    f"Price: ${offer.price:,.0f} | SLA: {offer.sla}% | Terms: {offer.payment_terms} | Delivery: {offer.delivery_days} days\n"
                    f"COMPETING ACTIVE BIDS: " + ", ".join(f"{x.vendor} (${x.price:,.0f}, {x.sla}% SLA)" for x in active)
                )
                buyer_tasks.append(drex_decide(client, "Enterprise Buyer", state))

            buyer_decisions = await asyncio.gather(*buyer_tasks)

            for offer, b_dec in zip(active, buyer_decisions):
                total_drex_ms += b_dec["latency_ms"]
                total_calls += 1
                act = b_dec["action"]

                logs.append({
                    "round": rnd,
                    "agent": f"Buyer -> {offer.vendor}",
                    "decision": act,
                    "confidence": round(max(b_dec["action_probs"].values()), 3),
                    "compliant_prob": b_dec["compliant_prob"],
                    "deal_score": b_dec["deal_score"],
                    "latency_ms": b_dec["latency_ms"],
                    "snapshot": f"${offer.price:,.0f} | {offer.sla}% SLA | {offer.payment_terms} | {offer.delivery_days}d",
                })

                if act == "ACCEPT" and b_dec["compliant_prob"] >= 0.55:
                    offer.status = "WON"
                    return offers, logs, total_drex_ms, total_calls

                if act == "WALK_AWAY":
                    offer.status = "ELIMINATED"
                    continue

                v_state = (
                    f"ROUND {rnd}/{max_rounds}\n"
                    f"YOUR VENDOR PROFILE ({offer.vendor}):\n{vendor_contexts.get(offer.vendor, '')}\n\n"
                    f"BUYER ACTION: {act}\n"
                    f"YOUR CURRENT OFFER: ${offer.price:,.0f} | SLA: {offer.sla}% | Terms: {offer.payment_terms} | Delivery: {offer.delivery_days} days"
                )
                v_dec = await drex_decide(client, f"Vendor ({offer.vendor})", v_state)
                total_drex_ms += v_dec["latency_ms"]
                total_calls += 1

                if v_dec["action"] == "COUNTER_PRICE":
                    offer.price = round(offer.price * 0.975, -2)
                elif v_dec["action"] == "COUNTER_TERMS":
                    offer.sla = max(offer.sla, 99.90)
                    offer.payment_terms = "Net-60"
                    offer.delivery_days = min(offer.delivery_days, 14)
                elif v_dec["action"] == "WALK_AWAY":
                    offer.status = "ELIMINATED"

                logs.append({
                    "round": rnd,
                    "agent": f"Vendor ({offer.vendor})",
                    "decision": v_dec["action"],
                    "confidence": round(max(v_dec["action_probs"].values()), 3),
                    "compliant_prob": v_dec["compliant_prob"],
                    "deal_score": v_dec["deal_score"],
                    "latency_ms": v_dec["latency_ms"],
                    "snapshot": f"${offer.price:,.0f} | {offer.sla}% SLA | {offer.payment_terms} | {offer.delivery_days}d",
                })

    return offers, logs, total_drex_ms, total_calls
