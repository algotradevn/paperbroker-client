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

# Default alternating steps (SELL/BUY with qty and price)
# You can override using ALTERNATING_STEPS in .env, format: SELL:1:1610,BUY:2:1600,...
DEFAULT_STEPS = [
    ("SELL", 1, 1610),
    ("BUY", 2, 1600),
    ("SELL", 3, 1610),
    ("BUY", 4, 1600),
    ("SELL", 5, 1610),
    ("BUY", 6, 1600),
]


def wait_for_logon(*clients):
    """Wait until all clients have established FIX logon."""
    while any(c.get_session_id() is None for c in clients):
        print("[WAITING] Waiting for FIX logons...")
        time.sleep(0.2)


def match_orders(buyer, seller, side_buyer, qty, price):
    """Send opposite orders to guarantee a match (with cancel/replace demo)."""
    cl_b = buyer.place_order(SYMBOL, side_buyer, qty=qty, price=price)
    print(f"[{side_buyer}] Placed order: {cl_b}")
    buyer.cancel_order(cl_b)  # Cancel first order
    cl_b = buyer.place_order(SYMBOL, side_buyer, qty=qty, price=price)
    print(f"[{side_buyer}] Replaced order: {cl_b}")
    side_seller = "SELL" if side_buyer == "BUY" else "BUY"
    cl_s = seller.place_order(SYMBOL, side_seller, qty=qty, price=price)
    time.sleep(1.5)  # allow matching
    return cl_b, cl_s


def print_balance_step(step, qty, side, price):
    """Print account balance and portfolio after each trade step."""
    print(f"\n=== AFTER {side} {qty} @ {price} (Step {step}) ===")
    print("[COMBAT] Remain Balance:", combat.get_remain_balance())
    print("[COMBAT] Total Balance :", combat.get_total_balance())
    print("[COMBAT] Portfolio     :", combat.get_portfolio())


def load_steps():
    steps_env = os.getenv("ALTERNATING_STEPS")
    if steps_env:
        steps = []
        for token in steps_env.split(","):
            side, qty, price = token.split(":")
            steps.append((side.strip().upper(), int(qty), float(price)))
        return steps
    return DEFAULT_STEPS


try:
    combat.connect()
    ask_bot.connect()
    wait_for_logon(combat, ask_bot)

    print("\n=== INITIAL BALANCE ===")
    init_balance = combat.get_remain_balance()
    print(f"[COMBAT] Init remain balance = {init_balance}")

    steps = load_steps()

    for i, (side, qty, price) in enumerate(steps, start=1):
        cl1, _ = match_orders(combat, ask_bot, side, qty, price)
        print(f"[{side} {i}] Placed {side} {qty} @ {price}, orderID={cl1}")
        print_balance_step(i, qty, side, price)

    # --- Final check ---
    print("\n=== FINAL BALANCES ===")
    remain_balance = combat.get_remain_balance()
    total_balance = combat.get_total_balance()
    portfolio = combat.get_portfolio()

    print(f"[COMBAT] Remain Balance: {remain_balance}")
    print(f"[COMBAT] Total Balance : {total_balance}")
    print(f"[COMBAT] Portfolio     : {portfolio}")

    total_trades = sum(qty for _, qty, _ in steps)
    expected_fee_loss = total_trades * FEE_PER_TRADE
    print(f"[CHECK] Expected fee loss ≈ {expected_fee_loss}")

    # --- NAV & Drawdown metrics ---
    print("\n=== NAV HISTORY ===")
    nav_history = combat.get_nav_history()
    for point in nav_history[-5:]:
        print(f"{point['timestamp']} : {point['value']:.2f}")

    print("\n=== MAX DRAWDOWN ===")
    mdd = combat.get_max_drawdown()
    print(f"[COMBAT] Max Drawdown: {mdd.get('maxDrawdownPct', 0):.9f}")

    print("\n=== DRAWDOWN PERIODS ===")
    drawdowns = combat.get_drawdown_periods()
    for d in drawdowns:
        print(
            f"- {d['drawdownPct']:.9f} from {d['peakTime']} ({d['peakValue']}) "
            f"→ {d['troughTime']} ({d['troughValue']})"
        )

finally:
    combat.disconnect()
    ask_bot.disconnect()
