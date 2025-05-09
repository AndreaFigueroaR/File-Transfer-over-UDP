import socket
from lib.protocols.config import MAX_TIME_OUT
    
def reconsider_timeout(skt: socket):
    actual_time_out = skt.gettimeout() 
    if actual_time_out < MAX_TIME_OUT:
        skt.settimeout(actual_time_out + actual_time_out)
