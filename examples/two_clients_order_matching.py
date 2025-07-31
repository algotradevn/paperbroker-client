# two_clients_order_matching.py

import os
import time
from dotenv import load_dotenv
from paperbroker import PaperBrokerClient

# Load environment variables
load_dotenv()
REST_BASE_URL = os.getenv("rest_base_url", "http://localhost:9090")

# Initialize two clients (buyer and seller)
buyer = PaperBrokerClient(
    account=os.getenv("account", "combat"),
    username=os.getenv("username", "combat"),
    password=os.getenv("password", "123"),
    cfg_path=os.getenv("cfg_path", "test.cfg"),
    console=False,
    rest_base_url=REST_BASE_URL,
)

seller = PaperBrokerClient(
    account=os.getenv("account_ask", "ask_bot"),
    username=os.getenv("username_ask", "ask_bot"),
    password=os.getenv("password_ask", "123"),
    cfg_path=os.getenv("cfg_path_ask", "test_ask.cfg"),
    console=False,
    rest_base_url=REST_BASE_URL,
)

try:
    # Connect both clients
    buyer.connect()
    seller.connect()

    # Wait until both FIX sessions are fully established
    while buyer.get_session_id() is None or seller.get_session_id() is None:
        print("[WAITING] Waiting for both FIX logons...")
        time.sleep(0.2)

    print("\n=== INITIAL BALANCES ===")
    print("[BUYER] Remain Balance:", buyer.get_remain_balance())
    print("[BUYER] Total Balance:", buyer.get_total_balance())
    print("[BUYER] Portfolio:", buyer.get_portfolio())
    print("[SELLER] Remain Balance:", seller.get_remain_balance())
    print("[SELLER] Total Balance:", seller.get_total_balance())
    print("[SELLER] Portfolio:", seller.get_portfolio())

    # Step 1: Buyer places a BUY order
    cl_buy = buyer.place_order("HNXDS:VN30F2508", "BUY", qty=1, price=1610)
    print(f"[STEP 1] Buyer placed order: {cl_buy}")

    # Step 2: Seller places a SELL order that should match
    cl_sell = seller.place_order("HNXDS:VN30F2508", "SELL", qty=1, price=1610)
    print(f"[STEP 2] Seller placed order: {cl_sell}")

    # Allow time for matching
    time.sleep(3)

    # Step 3: Check order status for both sides
    print("[STEP 3] Buyer order status:", buyer.get_order_status(cl_buy))
    print("[STEP 3] Seller order status:", seller.get_order_status(cl_sell))

    # Step 4: Fetch remain balances and portfolio after trade
    print("\n=== BALANCES AFTER TRADE ===")
    print("[BUYER] Remain Balance:", buyer.get_remain_balance())
    print("[BUYER] Total Balance:", buyer.get_total_balance())
    print("[BUYER] Portfolio:", buyer.get_portfolio())
    print("[SELLER] Remain Balance:", seller.get_remain_balance())
    print("[SELLER] Total Balance:", seller.get_total_balance())
    print("[SELLER] Portfolio:", seller.get_portfolio())

    # Step 5: Fetch order book (both clients can see)
    print("\n=== ORDER BOOK ===")
    print("[BUYER Orders]:", buyer.get_derivative_orders())
    print("[SELLER Orders]:", seller.get_derivative_orders())

    # Step 6: Fetch transactions (both clients)
    print("\n=== TRANSACTIONS ===")
    print("[BUYER Transactions]:", buyer.get_transactions())
    print("[SELLER Transactions]:", seller.get_transactions())

finally:
    buyer.disconnect()
    seller.disconnect()
