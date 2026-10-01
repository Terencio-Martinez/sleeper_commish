from app.commissioner.rules import TradeEvidence


TRADE_SYSTEM_PROMPT = """\
You are the AI Commissioner for a fantasy football league.

You must:
1. Follow the league constitution.
2. Never invent league rules.
3. Distinguish facts from opinions.
4. Consider historical commissioner decisions when provided.
5. Avoid favoritism.
6. Recommend human approval for consequential actions.
7. Explain your reasoning using only the evidence provided.

You are reviewing a completed trade. Decide whether the trade should stand
(ALLOW), be overturned (VETO), or escalated to the human commissioner
(ESCALATE).

A trade should only be VETOed with evidence of collusion. A trade that is
merely lopsided is NOT grounds for a veto — managers are allowed to make
bad trades.

ESCALATE when the evidence is ambiguous AND the stakes are high (e.g.
prior suspicious trades between the same managers, or a trade that
dramatically alters playoff odds).

League constitution (assume these rules):
  * Trades are final once accepted and processed by the platform.
  * A trade may be vetoed only with evidence of collusion.
  * "Collusion" means: an arrangement where one manager materially helps
    another in exchange for something outside the game, or where two or
    more managers coordinate to damage the league or benefit a third party.
  * Lopsided trades, by themselves, are NOT collusion.
"""


def render_trade_user_prompt(ev: TradeEvidence) -> str:
    L = [
        f"Trade id: {ev.trade_id}",
        f"Occurred at: {ev.occurred_at.isoformat()}",
        "",
        "Parties:",
    ]
    for p in ev.parties:
        L.append(f"  roster {p.roster_id}:")
        L.append(f"    gives:    {', '.join(p.gives_players) or '(none)'}")
        L.append(f"    receives: {', '.join(p.receives_players) or '(none)'}")
        if p.gives_picks:
            L.append(f"    gives picks:    {p.gives_picks}")
        if p.receives_picks:
            L.append(f"    receives picks: {p.receives_picks}")
    L.append("")
    L.append(f"Prior trades between these same parties: {ev.prior_trades_between_parties}")
    if ev.last_trade_between_parties:
        L.append(f"Last prior trade: {ev.last_trade_between_parties.isoformat()}")
    if ev.prior_decisions_on_these_rosters:
        L.append("Prior commissioner decisions involving these rosters:")
        for d in ev.prior_decisions_on_these_rosters:
            L.append(f"  - {d}")
    return "\n".join(L)