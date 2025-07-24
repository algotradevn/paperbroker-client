import time
from paperbroker import PaperBrokerClient

client = PaperBrokerClient(
    account="reppg",
    username="reppg",
    password="123",
    cfg_path="test.cfg",
    console=True,
)
client.connect()

time.sleep(5)

client.disconnect()
