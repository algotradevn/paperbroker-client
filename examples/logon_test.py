import time
from paperbroker import PaperBrokerClient

client = PaperBrokerClient(
    account="reppg", username="reppg", password="123", cfg_path="test.cfg"
)
client.connect()

while True:
    time.sleep(2)
