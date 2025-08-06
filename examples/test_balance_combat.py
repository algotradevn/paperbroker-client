import os
import time
from dotenv import load_dotenv
from paperbroker import PaperBrokerClient

# Load environment variables
load_dotenv()

REST_BASE_URL = os.getenv("PAPER_REST_BASE_URL", "http://localhost:9090")

combat = PaperBrokerClient(
    account=os.getenv("COMBAT_ACCOUNT", "combat"),
    username=os.getenv("COMBAT_USERNAME", "combat"),
    password=os.getenv("COMBAT_PASSWORD", "123"),
    cfg_path=os.getenv("COMBAT_CFG_PATH", "combat.cfg"),
    console=False,
    rest_base_url=REST_BASE_URL,
)

ask_bot = PaperBrokerClient(
    account=os.getenv("ASKBOT_ACCOUNT", "ask_bot"),
    username=os.getenv("ASKBOT_USERNAME", "ask_bot"),
    password=os.getenv("ASKBOT_PASSWORD", "123"),
    cfg_path=os.getenv("ASKBOT_CFG_PATH", "ask_bot.cfg"),
    console=False,
    rest_base_url=REST_BASE_URL,
)

FEE_PER_TRADE = int(os.getenv("FEE_PER_TRADE", "3500"))
SYMBOL = os.getenv("INSTRUMENT", "EXCHANGE:SYMBOL")
PRICE = float(os.getenv("INIT_PRICE", "1610"))


def wait_for_logon(*clients):
    while any(c.get_session_id() is None for c in clients):
        print("[WAITING] Waiting for FIX logons...")
        time.sleep(0.2)


def match_orders(buyer, seller, side_buyer, qty, price):
    """Place opposite orders to ensure match"""
    cl_b = buyer.place_order(SYMBOL, side_buyer, qty=qty, price=price)
    side_seller = "SELL" if side_buyer == "BUY" else "BUY"
    cl_s = seller.place_order(SYMBOL, side_seller, qty=qty, price=price)
    time.sleep(1.5)  # allow matching
    return cl_b, cl_s


def print_balance_step(step, qty, side):
    print(f"\n=== AFTER {side} {qty} (Step {step}) ===")
    print("[COMBAT] Remain Balance:", combat.get_remain_balance())
    print("[COMBAT] Total Balance :", combat.get_total_balance())
    print("[COMBAT] Portfolio     :", combat.get_portfolio())


try:
    combat.connect()
    ask_bot.connect()
    wait_for_logon(combat, ask_bot)

    print("\n=== INITIAL BALANCE ===")
    init_balance = combat.get_remain_balance()
    print(f"[COMBAT] Init remain balance = {init_balance}")

    # --- SELL 1 -> 2 -> 3 ---
    for i, qty in enumerate([1, 2, 3], start=1):
        cl1, _ = match_orders(combat, ask_bot, "SELL", qty, PRICE)
        print(f"[SELL {i}] Placed SELL {qty} @ {PRICE}, orderID={cl1}")
        print_balance_step(i, qty, "SELL")

    # --- BUY 4 -> 5 -> 6 ---
    for j, qty in enumerate([4, 5, 6], start=4):
        cl1, _ = match_orders(combat, ask_bot, "BUY", qty, PRICE)
        print(f"[BUY {j}] Placed BUY {qty} @ {PRICE}, orderID={cl1}")
        print_balance_step(j, qty, "BUY")

    # --- FINAL CHECK ---
    print("\n=== FINAL BALANCES ===")
    remain_balance = combat.get_remain_balance()
    total_balance = combat.get_total_balance()
    portfolio = combat.get_portfolio()

    print(f"[COMBAT] Remain Balance: {remain_balance}")
    print(f"[COMBAT] Total Balance : {total_balance}")
    print(f"[COMBAT] Portfolio     : {portfolio}")

    # Optional: compute expected fee impact
    total_trades = (1 + 2 + 3) + (4 + 5 + 6)
    expected_fee_loss = total_trades * FEE_PER_TRADE
    print(f"[CHECK] Expected fee loss ≈ {expected_fee_loss}")

finally:
    combat.disconnect()
    ask_bot.disconnect()
