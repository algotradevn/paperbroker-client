from paperbroker import PaperBrokerClient
import time

client = PaperBrokerClient(
    account="reppg",
    username="reppg",
    password="123",
    cfg_path="test.cfg",
    console=True,
)

try:
    client.connect()

    # Wait for logon
    while client.get_session_id() is None:
        print("[WAITING] Waiting for FIX logon...")
        time.sleep(0.2)

    cl_ord_id = client.place_order("MWG", "BUY", qty=100, price=74500)
    print(f"[STEP 1] Placed order: {cl_ord_id}")

    time.sleep(2)
    status = client.get_order_status(cl_ord_id)
    print(f"[STEP 2] Order status: {status}")

    time.sleep(2)
    client.cancel_order(cl_ord_id)
    print(f"[STEP 3] Cancel sent for order {cl_ord_id}")

    time.sleep(2)
    status = client.get_order_status(cl_ord_id)
    print(f"[STEP 4] Final status: {status}")

finally:
    client.disconnect()  # ✅ Always clean up session
