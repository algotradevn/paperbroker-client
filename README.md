
---

# paperbroker-client

A Python client that **abstracts away FIX protocol complexity** when interacting with the Paper Broker server.

---

## 🔧 Installation

1. Download the latest `.whl` file from [Releases](https://github.com/algotradevn/paperbroker-client/releases):

   ```
   https://github.com/algotradevn/paperbroker-client/releases/download/v0.1.2/paperbroker_client-0.1.3-py3-none-any.whl
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install the `.whl` file:

   ```bash
   pip install paperbroker_client-0.1.3-py3-none-any.whl
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
    console=False,  # Set to True for debug logging to console
)

client.connect()
time.sleep(5)
client.disconnect()
```

---

### Place and Cancel Orders

```python
cl_ord_id = client.place_order("HNXDS:VN30F2508", "BUY", qty=1, price=1650)
client.cancel_order(cl_ord_id)
```

---

## 📑 Data Structures

### 1. Portfolio

```python
client.get_portfolio()
```

```json
{
  "accountID": "e853",
  "holdings": [
    {
      "instrument": "HNXDS:VN30F2508",
      "quantity": 2,
      "openPrice": 40250000.0,
      "currentPrice": 1610,
      "t1": 0,
      "t2": 0,
      "buyVolume": 0,
      "sellVolume": 0,
      "totalCost": 80500000.0
    }
  ]
}
```

---

### 2. Remain Balance

```python
client.get_remain_balance()
```

```json
{
  "accountID": "e853",
  "remainBalance": 999919493000
}
```

---

### 3. Total Balance

```python
client.get_total_balance()
```

```json
{
  "accountID": "e853",
  "totalBalance": 999999993000.0
}
```

---

### 4. Orders List

```python
client.get_stock_orders()
client.get_derivative_orders()
```

```json
[
  {
    "orderID": "d4fb34fe-9fe0-4ba3-baee-f15c628addbd",
    "clOrdID": "d306a7bd",
    "accountID": "e853",
    "instrument": "VN30F2508",
    "side": "1",                // 1 = BUY, 2 = SELL
    "orderQty": 1,
    "price": 1610,
    "ordStatus": "2",           // '2' = Filled
    "orderTime": "2025-07-31T15:59:46.01",
    "statusCode": "FILLED",
    "statusText": "Order was fully filled",
    "leavesQty": 0,
    "cumQty": 1,
    "avgPx": 1610,
    "position": "LONG"
  }
]
```

---

### 5. Transactions

```python
client.get_transactions()
```

```json
[
  {
    "transactionID": "72d7b44b-8f8f-4de6-ba71-fc677699ab73",
    "side": "BUY",              // or SELL
    "accountID": "e853",
    "instrument": "HNXDS:VN30F2508",
    "price": 1610,
    "quantity": 1,
    "type": "BUY",
    "envTimestamp": "2025-07-31T15:59:46.090870717",
    "sysTimestamp": "2025-07-31T15:59:46.129827767"
  }
]
```

---

### 6. Executions

#### Executions by Order

```python
client.get_executions_by_order(cl_ord_id)
```

```json
[
  {
    "execID": "1f5300bb-9fca-40f2-bb94-796c4b778c48",
    "orderID": "0e49f0b0-fe6b-4ed8-bb83-b65a238e77b5",
    "execQty": 1,
    "execPrice": 1610,
    "transactTime": "2025-07-31T16:04:49.433"
  }
]
```

#### Executions by Account

```python
client.get_executions_by_account(account_id)
```

```json
[
  {
    "execID": "1f5300bb-9fca-40f2-bb94-796c4b778c48",
    "orderID": "0e49f0b0-fe6b-4ed8-bb83-b65a238e77b5",
    "execQty": 1,
    "execPrice": 1610,
    "transactTime": "2025-07-31T16:04:49.433"
  },
  {
    "execID": "bbee1f52-1858-4b18-9370-2c1b40a3c4ae",
    "orderID": "d4fb34fe-9fe0-4ba3-baee-f15c628addbd",
    "execQty": 1,
    "execPrice": 1610,
    "transactTime": "2025-07-31T15:59:46.09"
  },
  {
    "execID": "24060938-e280-46eb-b1b8-493f15dbc778",
    "orderID": "53f69123-5670-4244-bc35-469570841ba5",
    "execQty": 1,
    "execPrice": 1610,
    "transactTime": "2025-07-31T15:59:38.612"
  }
]
```

---

### 7. Quotes via Kafka

Paper Broker also streams **real-time market data** through Kafka topics.
Example: retrieving the **latest matched price** for an instrument:

```python
import os
import json
import time
from kafka import KafkaConsumer

TOPIC_NAME = "kafka.HNXDS.VN30F2508"
GROUP_ID = f"plutus-{int(time.time())}"

kafka = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(","),
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="PLAIN",
    sasl_plain_username=os.getenv("KAFKA_USERNAME", "your-username"),
    sasl_plain_password=os.getenv("KAFKA_PASSWORD", "your-password"),
    group_id=GROUP_ID,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
)

def get_latest_matched_price(timeout=1):
    msg_pack = kafka.poll(timeout_ms=timeout * 1000, max_records=10)
    for messages in msg_pack.values():
        for msg in reversed(messages):
            return (
                msg.value.get("quote_entries", {})
                .get("latest_matched_price", {})
                .get("value")
            )
    return None

print("Latest matched price:", get_latest_matched_price())
```

---

### Quote Structure

A full quote message looks like this:

```json
{
  "instrument": "HSX:MWG",
  "quote_entries": {
    "latest_matched_price": {
      "instrument": "HSX:MWG",
      "quote_type": "latest_matched_price",
      "value": 56500,
      "source": "X2",
      "last_updated_str": "15/04/2025 10:21:14",
      "last_updated": 1744687274
    },
    "latest_matched_quantity": {
      "instrument": "HSX:MWG",
      "quote_type": "latest_matched_quantity",
      "value": 800,
      "source": "X2",
      "last_updated_str": "15/04/2025 10:21:35",
      "last_updated": 1744687295
    },
    "ref_price": { "...": "..." },
    "open_price": { "...": "..." },
    "ceiling_price": { "...": "..." },
    "floor_price": { "...": "..." },
    "bid_price_1": { "...": "..." },
    "ask_price_1": { "...": "..." },
    "...": "more entries"
  },
  "hidden_system_status": "{\"Open\":56000,\"Close\":56500,...}",
  "datetime_str": "15/04/2025 10:21:53",
  "timestamp": 1744687313
}
```

👉 The `quote_entries` map contains many different fields, such as reference price (`ref_price`), open/close prices (`open_price`, `close_price`), ceiling/floor limits (`ceiling_price`, `floor_price`), bid/ask ladders (`bid_price_1…10`, `ask_price_1…10`), matched quantities (`latest_matched_quantity`, `total_matched_quantity`), average price (`average_price`), foreign room (`foreign_room`), and more.

---

