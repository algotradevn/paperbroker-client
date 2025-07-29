import os
import time
from dotenv import load_dotenv
from paperbroker import PaperBrokerClient

# Load environment variables from .env file
load_dotenv()

# Initialize FIX + REST client
client = PaperBrokerClient(
    account=os.getenv("account", "default_account"),
    username=os.getenv("username", "default_username"),
    password=os.getenv("password", "default_password"),
    cfg_path=os.getenv("cfg_path", "default.cfg"),
    console=True,
    rest_base_url=os.getenv("rest_base_url", "http://localhost:9090"),
)

try:
    client.connect()

    # Wait until the FIX session is fully established
    while client.get_session_id() is None:
        print("[WAITING] Waiting for FIX logon...")
        time.sleep(0.2)

    # Step 0: Fetch initial remain balance before placing order
    remain_balance = client.get_remain_balance()
    print("[STEP 0] Remain Balance (before order):", remain_balance)

    # Step 1: Place a BUY limit order
    cl_ord_id = client.place_order("HSX:VN30F2508", "BUY", qty=1, price=1620)
    print(f"[STEP 1] Placed order: {cl_ord_id}")

    time.sleep(2)

    # Step 2: Check order status after submission
    status = client.get_order_status(cl_ord_id)
    print(f"[STEP 2] Order status: {status}")

    # Step 2b: Fetch remain balance after placing order
    remain_balance = client.get_remain_balance()
    print("[STEP 2b] Remain Balance (after order placed):", remain_balance)

    time.sleep(2)

    # Step 3: Send cancel request for the order
    client.cancel_order(cl_ord_id)
    print(f"[STEP 3] Cancel sent for order {cl_ord_id}")

    time.sleep(2)

    # Step 4: Check final status after cancellation
    status = client.get_order_status(cl_ord_id)
    print(f"[STEP 4] Final status: {status}")

    # Step 4b: Fetch remain balance after cancellation
    remain_balance = client.get_remain_balance()
    print("[STEP 4b] Remain Balance (after cancel):", remain_balance)

finally:
    # Always disconnect the FIX session properly
    client.disconnect()
