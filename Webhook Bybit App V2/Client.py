import bybit
from BybitWebsocket import BybitWebsocket
import config_bybit

# Client Bybit API 
client = bybit.bybit(test=False,api_key=config_bybit.api_key,api_secret=config_bybit.api_secret)

# Websocket Bybit
ws = BybitWebsocket(wsURL="wss://stream.bytick.com/realtime",api_key=config_bybit.api_key,api_secret=config_bybit.api_secret)
