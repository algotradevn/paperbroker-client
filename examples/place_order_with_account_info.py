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

    # Step 0: Fetch initial account info before placing order
    account_info = client.get_account_info()
    print("[STEP 0] Account Info (before order):", account_info)

    # Step 1: Place a BUY limit order
    cl_ord_id = client.place_order("MWG", "BUY", qty=100, price=74500)
    print(f"[STEP 1] Placed order: {cl_ord_id}")

    time.sleep(2)

    # Step 2: Check order status after submission
    status = client.get_order_status(cl_ord_id)
    print(f"[STEP 2] Order status: {status}")

    # Step 2b: Fetch account info after placing order
    account_info = client.get_account_info()
    print("[STEP 2b] Account Info (after order placed):", account_info)

    time.sleep(2)

    # Step 3: Send cancel request for the order
    client.cancel_order(cl_ord_id)
    print(f"[STEP 3] Cancel sent for order {cl_ord_id}")

    time.sleep(2)

    # Step 4: Check final status after cancellation
    status = client.get_order_status(cl_ord_id)
    print(f"[STEP 4] Final status: {status}")

    # Step 4b: Fetch account info after cancellation
    account_info = client.get_account_info()
    print("[STEP 4b] Account Info (after cancel):", account_info)

finally:
    # Always disconnect the FIX session properly
    client.disconnect()
