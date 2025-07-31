import os
import time
from dotenv import load_dotenv
from paperbroker import PaperBrokerClient

# Load environment variables
load_dotenv()

REST_BASE_URL = os.getenv("rest_base_url", "http://localhost:9090")

client = PaperBrokerClient(
    account=os.getenv("account", "default_account"),
    username=os.getenv("username", "default_username"),
    password=os.getenv("password", "default_password"),
    cfg_path=os.getenv("cfg_path", "default.cfg"),
    console=False,
    rest_base_url=REST_BASE_URL,
)

try:
    client.connect()

    # Wait until FIX session is established
    while client.get_session_id() is None:
        print("[WAITING] Waiting for FIX logon...")
        time.sleep(0.2)

    # === STOCK ORDER ===
    print("\n=== STOCK ORDER FLOW ===")
    print("[STEP 0] Remain Balance:", client.get_remain_balance())
    print("[STEP 0] Total Balance:", client.get_total_balance())

    cl_ord_id_stock = client.place_order("HSX:MWG", "BUY", qty=10, price=60000)
    print(f"[STEP 1] Placed STOCK order: {cl_ord_id_stock}")

    time.sleep(2)
    print("[STEP 2] Stock order status:", client.get_order_status(cl_ord_id_stock))

    stock_orders = client.get_stock_orders()
    print("[STEP 2b] Stock Orders:", stock_orders)

    client.cancel_order(cl_ord_id_stock)
    print(f"[STEP 3] Cancel sent for STOCK order {cl_ord_id_stock}")

    time.sleep(2)
    print(
        "[STEP 4] Final stock order status:", client.get_order_status(cl_ord_id_stock)
    )

    # === DERIVATIVE ORDER ===
    print("\n=== DERIVATIVE ORDER FLOW ===")
    print("[STEP 0] Remain Balance:", client.get_remain_balance())
    print("[STEP 0] Total Balance:", client.get_total_balance())

    cl_ord_id_der = client.place_order("HNXDS:VN30F2508", "SELL", qty=1, price=1620)
    print(f"[STEP 1] Placed DERIVATIVE order: {cl_ord_id_der}")

    time.sleep(2)
    print("[STEP 2] Derivative order status:", client.get_order_status(cl_ord_id_der))

    derivative_orders = client.get_derivative_orders()
    print("[STEP 2b] Derivative Orders:", derivative_orders)

    client.cancel_order(cl_ord_id_der)
    print(f"[STEP 3] Cancel sent for DERIVATIVE order {cl_ord_id_der}")

    time.sleep(2)
    print(
        "[STEP 4] Final derivative order status:",
        client.get_order_status(cl_ord_id_der),
    )

finally:
    client.disconnect()
