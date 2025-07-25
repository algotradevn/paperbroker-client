import os
from dotenv import load_dotenv
import time
from paperbroker import PaperBrokerClient

load_dotenv()

client = PaperBrokerClient(
    account=os.getenv("account", "default_account"),
    username=os.getenv("username", "default_username"),
    password=os.getenv("password", "default_password"),
    cfg_path=os.getenv("cfg_path", "default.cfg"),
    console=True,
)
client.connect()

time.sleep(5)

client.disconnect()
