"""Refresh the public BAGSY status snapshot from pump.fun and Solana RPC."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.request import Request, urlopen

MINT = "GUAFAP1wtFK2R79y5mCpumZA4yR2R9bNrZs7yB2epump"
TOKEN_2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
PUMP_URL = f"https://frontend-api-v3.pump.fun/coins/{MINT}"
RPC_URL = "https://api.mainnet-beta.solana.com"
OUTPUT = Path(__file__).resolve().parents[1] / "status.json"


def fetch_json(url: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload else None
    request = Request(
        url,
        data=body,
        headers={"Accept": "application/json", "Content-Type": "application/json", "User-Agent": "BAGSY-status/1.0"},
        method="POST" if payload else "GET",
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def build_snapshot(coin: dict, program_accounts: list[dict], checked_at: datetime) -> dict:
    balances: dict[str, Decimal] = {}
    for account in program_accounts:
        info = account["account"]["data"]["parsed"]["info"]
        amount = Decimal(info["tokenAmount"]["uiAmountString"])
        if amount > 0:
            owner = info["owner"]
            balances[owner] = balances.get(owner, Decimal(0)) + amount

    curve_owner = coin["bonding_curve"]
    creator = coin["creator"]
    non_curve = {owner: amount for owner, amount in balances.items() if owner != curve_owner}
    external = {owner: amount for owner, amount in non_curve.items() if owner != creator}
    total = sum(balances.values(), Decimal(0))
    creator_amount = balances.get(creator, Decimal(0))
    creator_percent = (creator_amount / total * 100) if total else Decimal(0)
    last_trade = datetime.fromtimestamp(int(coin["last_trade_timestamp"]) / 1000, tz=timezone.utc)

    return {
        "schemaVersion": "1.0",
        "checkedAt": checked_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "officialMint": MINT,
        "market": {
            "complete": bool(coin["complete"]),
            "usdMarketCap": round(float(coin["usd_market_cap"]), 2),
            "realSolReserves": round(int(coin["real_sol_reserves"]) / 1_000_000_000, 4),
            "lastTradeAt": last_trade.isoformat().replace("+00:00", "Z"),
        },
        "holders": {
            "nonCurveWallets": len(non_curve),
            "walletsBeyondCreator": len(external),
            "definition": "Distinct on-chain wallet owners with a nonzero token balance, excluding the pump.fun bonding-curve owner. Wallets do not necessarily equal individual people.",
        },
        "distribution": {
            "creatorWallet": creator,
            "creatorSupplyPercent": round(float(creator_percent), 4),
        },
        "sources": {
            "market": PUMP_URL,
            "rpc": RPC_URL,
        },
        "warning": "This is a timestamped public-data snapshot, not financial advice. Values can change after checkedAt and should be verified independently.",
    }


def main() -> None:
    coin = fetch_json(PUMP_URL)
    rpc_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getProgramAccounts",
        "params": [
            TOKEN_2022_PROGRAM,
            {"encoding": "jsonParsed", "filters": [{"memcmp": {"offset": 0, "bytes": MINT}}]},
        ],
    }
    rpc_response = fetch_json(RPC_URL, rpc_payload)
    if "error" in rpc_response:
        raise RuntimeError(f"Solana RPC error: {rpc_response['error']}")
    snapshot = build_snapshot(coin, rpc_response["result"], datetime.now(timezone.utc))
    OUTPUT.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
