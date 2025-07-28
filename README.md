---

# paperbroker-client

A Python client that **abstracts away FIX protocol complexity** when interacting with the Paper Broker server.

---

## 🔧 Installation

1. Download the latest `.whl` file from [Releases](https://github.com/algotradevn/paperbroker-client/releases):

   ```
   https://github.com/algotradevn/paperbroker-client/releases/download/v0.1.1/paperbroker_client-0.1.1-py3-none-any.whl
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install the `.whl` file:

   ```bash
   pip install paperbroker_client-0.1.1-py3-none-any.whl
   ```

4. Create a FIX config file (e.g., `default.cfg`) with this template:

   ```ini
   [DEFAULT]
   ConnectionType=initiator
   SocketConnectHost=127.0.0.1
   SocketConnectPort=5001
   StartTime=00:00:00
   EndTime=23:59:59
   HeartBtInt=30
   FileStorePath=logs/client_fix_messages/
   FileLogPath=logs/

   [SESSION]
   BeginString=FIX.4.4
   SenderCompID=CLIENT_1
   TargetCompID=SERVER
   DataDictionary=fix/FIX44.xml
   ResetOnLogon=Y
   ResetOnLogout=Y
   ResetOnDisconnect=Y
   IgnoreSeqNumTooLow=Y
   ValidateFieldsOutOfOrder=N
   ```

---

## 🚀 Usage Examples

### Logon Only

```python
import os
import time
from dotenv import load_dotenv
from paperbroker import PaperBrokerClient

load_dotenv()

client = PaperBrokerClient(
    account=os.getenv("account", "default_account"),
    username=os.getenv("username", "default_username"),
    password=os.getenv("password", "default_password"),
    cfg_path=os.getenv("cfg_path", "default.cfg"),
    console=True,  # Set to True for debug logging to console
)

client.connect()
time.sleep(5)
client.disconnect()
```

---

### Full Order Flow Example

```python
import os
import time
from dotenv import load_dotenv
from paperbroker import PaperBrokerClient

load_dotenv()

client = PaperBrokerClient(
    account=os.getenv("account", "default_account"),
    username=os.getenv("username", "default_username"),
    password=os.getenv("password", "default_password"),
    cfg_path=os.getenv("cfg_path", "default.cfg"),
    console=False,
    rest_base_url=os.getenv("rest_base_url", "http://localhost:9090"),
)

try:
    client.connect()

    while client.get_session_id() is None:
        print("[WAITING] Waiting for FIX logon...")
        time.sleep(0.2)

    print("[STEP 0] Account Info:", client.get_account_info())

    cl_ord_id = client.place_order("HNXDS:VN30F2508", "BUY", qty=1, price=1620)
    print(f"[STEP 1] Placed order: {cl_ord_id}")

    time.sleep(2)
    print(f"[STEP 2] Order status: {client.get_order_status(cl_ord_id)}")
    print("[STEP 2b] Account Info:", client.get_account_info())

    client.cancel_order(cl_ord_id)
    print(f"[STEP 3] Cancel sent for order {cl_ord_id}")

    time.sleep(2)
    print(f"[STEP 4] Final status: {client.get_order_status(cl_ord_id)}")
    print("[STEP 4b] Account Info:", client.get_account_info())

finally:
    client.disconnect()
```

---

## 🧾 Account Info Structure

Example response from `get_account_info()`:

```json
{
  "account_id": "348f",
  "initial_balance": 1000000000000,
  "current_balance": 1000000000000.0,
  "account_asset": { "keySet": [], "asset": {} },
  "funded_amount": {
    "funded": {
      "uuid": {
        "quantity": 1,
        "price": 40503500.0,
        "total": 40503500.0
      }
    },
    "grand_total": 40503500.0
  },
  "margin_structure": {
    "normal_stock_margin": 1,
    "derivative_margin": 4
  },
  "fee_structure": {
    "normal_stock_fee_pct": 0.005,
    "normal_stock_fee_qty": 0,
    "derivative_fee_pct": 0,
    "derivative_fee_qty": 3500
  },
  "account_history_manager": {
    "yearlyRiskFreeRate": 1.07,
    "sharpeRatio": 0,
    "balance_history": [],
    "mdd": 0,
    "sharpe_ratio": 0.0,
    "risk_free_rate_yearly": 1.07
  },
  "is_unlimited": false,
  "unlimited": false
}
```

---
