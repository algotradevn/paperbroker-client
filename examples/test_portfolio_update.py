import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from paperbroker import PaperBrokerClient
from kafka import KafkaConsumer

# Load environment variables
load_dotenv()

client = PaperBrokerClient(
    account=os.getenv("PAPER_ACCOUNT"),
    username=os.getenv("PAPER_USERNAME"),
    password=os.getenv("PAPER_PASSWORD"),
    cfg_path=os.getenv("PAPER_CFG"),
    console=False,
    rest_base_url=os.getenv("PAPER_REST_BASE_URL"),
)

# Kafka configs (set in .env)
KAFKA_BOOTSTRAP_SERVERS = [os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")]
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "example.topic")
GROUP_ID = f"example-test-{int(time.time())}"
INSTRUMENT = os.getenv("INSTRUMENT", "EXCHANGE:SYMBOL")

kafka = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_PLAINTEXT"),
    sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM", "PLAIN"),
    sasl_plain_username=os.getenv("KAFKA_USERNAME", "your-username"),
    sasl_plain_password=os.getenv("KAFKA_PASSWORD", "your-password"),
    group_id=GROUP_ID,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
)


def get_latest_matched_price(timeout: int = 1):
    """Fetch the most recent matched price from Kafka (within `timeout` seconds)."""
    msg_pack = kafka.poll(timeout_ms=timeout * 1000, max_records=10)
    for messages in msg_pack.values():
        for msg in reversed(messages):
            return (
                msg.value.get("quote_entries", {})
                .get("latest_matched_price", {})
                .get("value")
            )
    return None


try:
    client.connect()
    time.sleep(3)  # Allow time for connection

    # --- place a test order ---
    init_price = os.getenv("INIT_PRICE")
    init_price = float(init_price) if init_price else None
    while init_price is None:
        init_price = get_latest_matched_price()
        if init_price is None:
            print("[WAITING] No matched price yet, retrying...")
            time.sleep(1)

    cl_ord_id = client.place_order(INSTRUMENT, "BUY", 1, init_price)
    print(
        f"[{datetime.now():%H:%M:%S}] Placed test order @ {init_price}, clOrdID={cl_ord_id}"
    )

    # --- loop: print balance/portfolio every second ---
    while True:
        now = datetime.now()
        if now.hour >= 15:
            print(f"[{now:%H:%M:%S}] Market closed. Exiting...")
            break

        latest_price = get_latest_matched_price() or init_price
        total_balance = client.get_total_balance()
        portfolio = client.get_portfolio()

        print(f"[{now:%H:%M:%S}] Price = {latest_price}")
        print(f"[{now:%H:%M:%S}] Total balance: {total_balance}")
        print(f"[{now:%H:%M:%S}] Portfolio: {portfolio}")
        print("-" * 80)

        time.sleep(1)

finally:
    client.disconnect()
