# examples/two_clients_executions.py

import os
import time
from dotenv import load_dotenv
from paperbroker import PaperBrokerClient

# Load environment variables
load_dotenv()
REST_BASE_URL = os.getenv("rest_base_url", "http://localhost:9090")

# Initialize buyer
buyer = PaperBrokerClient(
    account=os.getenv("account", "combat"),
    username=os.getenv("username", "combat"),
    password=os.getenv("password", "123"),
    cfg_path=os.getenv("cfg_path", "test.cfg"),
    console=False,
    rest_base_url=REST_BASE_URL,
)

# Initialize seller
seller = PaperBrokerClient(
    account=os.getenv("account_ask", "ask_bot"),
    username=os.getenv("username_ask", "ask_bot"),
    password=os.getenv("password_ask", "123"),
    cfg_path=os.getenv("cfg_path_ask", "test_ask.cfg"),
    console=False,
    rest_base_url=REST_BASE_URL,
)

try:
    # Connect both
    buyer.connect()
    seller.connect()

    # Wait until both FIX sessions are fully established
    while buyer.get_session_id() is None or seller.get_session_id() is None:
        print("[WAITING] Waiting for both FIX logons...")
        time.sleep(0.2)

    # Step 1: Buyer places a BUY order
    cl_buy = buyer.place_order("HNXDS:VN30F2508", "BUY", qty=1, price=1610)
    print(f"[STEP 1] Buyer placed order: {cl_buy}")

    # Step 2: Seller places a SELL order (should match)
    cl_sell = seller.place_order("HNXDS:VN30F2508", "SELL", qty=1, price=1610)
    print(f"[STEP 2] Seller placed order: {cl_sell}")

    # Allow time for matching & execution
    time.sleep(3)

    # Step 3: Fetch executions by order
    print("\n=== EXECUTIONS BY ORDER ===")
    print("[BUYER Executions]:", buyer.get_executions_by_order(cl_buy))
    print("[SELLER Executions]:", seller.get_executions_by_order(cl_sell))

    # Step 4: Fetch executions by account
    print("\n=== EXECUTIONS BY ACCOUNT ===")
    print("[BUYER Executions]:", buyer.get_executions_by_account())
    print("[SELLER Executions]:", seller.get_executions_by_account())

finally:
    buyer.disconnect()
    seller.disconnect()
