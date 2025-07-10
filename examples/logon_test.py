from paperbroker import PaperBrokerClient

client = PaperBrokerClient(
    account="PINETREE", username="PINETREE", password="123", cfg_path="PINETREE.cfg"
)
client.connect()
