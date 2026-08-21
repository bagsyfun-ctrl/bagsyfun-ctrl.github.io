import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_status.py"
SPEC = importlib.util.spec_from_file_location("update_status", SCRIPT)
update_status = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update_status)


def account(owner, amount):
    return {"account": {"data": {"parsed": {"info": {"owner": owner, "tokenAmount": {"uiAmountString": amount}}}}}}


class SnapshotTests(unittest.TestCase):
    def test_counts_distinct_non_curve_wallets(self):
        coin = {
            "bonding_curve": "curve",
            "creator": "creator",
            "complete": False,
            "usd_market_cap": 4000,
            "real_sol_reserves": 7_000_000_000,
            "last_trade_timestamp": 1_700_000_000_000,
        }
        accounts = [account("curve", "800"), account("creator", "150"), account("buyer", "20"), account("buyer", "30")]
        snapshot = update_status.build_snapshot(coin, accounts, datetime(2026, 8, 21, tzinfo=timezone.utc))
        self.assertEqual(snapshot["holders"]["nonCurveWallets"], 2)
        self.assertEqual(snapshot["holders"]["walletsBeyondCreator"], 1)
        self.assertAlmostEqual(snapshot["distribution"]["creatorSupplyPercent"], 15.0)


if __name__ == "__main__":
    unittest.main()
