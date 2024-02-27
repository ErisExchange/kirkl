

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:20:57 2020

@author: kirk.lederer
"""

import socket

import argparse
import simplefix
import time

OUTBOUND_SEQ_NUM = 0
fixParser = simplefix.FixParser()
outboundSeq = 1
secondseq = 2
def send_logon(sock, user, pw,throttle):
    global outboundSeq
    message = simplefix.FixMessage()
    message.append_pair(8, "FIX.4.4")
    message.append_pair(35, "A")
    message.append_pair(49, user)
    message.append_pair(56, "ERISX")
    message.append_pair(98, "0")
    message.append_pair(108, "120")
    message.append_pair(141, "Y")
    message.append_pair(34, outboundSeq , header=True)
    message.append_utc_timestamp(52, header=True)
    message.append_pair(554, pw)
    msg_bytes = message.encode()
    sock.send(msg_bytes)
    decodemsg=str(msg_bytes.decode())
    logclean=decodemsg.replace('\x01',' ')
    print(f'Sending: \n{logclean}\n')
    outboundSeq += 1
    do_recv(sock)
    time.sleep(throttle)
    return

def heartbeat_test(sock, user):
    global outboundSeq
    message = simplefix.FixMessage()
    message.append_pair(8, "FIX.4.4")
    message.append_pair(35, "0")
    message.append_pair(49, user)
    message.append_pair(56, "ERISX")
    message.append_pair(112, "1")
    message.append_pair(34, outboundSeq , header=True)
    message.append_utc_timestamp(52, header=True)
    msg_bytes = message.encode()
    sock.send(msg_bytes)
    decodemsg=str(msg_bytes.decode())
    logclean=decodemsg.replace('\x01',' ')
    print(f'Sending: \n{logclean}\n')
    outboundSeq += 1
    do_recv(sock)
    return


def get_socket(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.setblocking(0)
        s.settimeout(0)
        return s
    except Exception as e:
        print("Couldn't connect socket", str(e))
def handle_bytes(bytes):
    fixParser.append_buffer(bytes)
    msg = fixParser.get_message()
    if msg is not None:
        print("received: ", msg)
    ##Add message handling here for different message types
def do_recv(sock):
    try:
        bytes = sock.recv(150)
        if bytes != b'':
            handle_bytes(bytes)
    except BlockingIOError as e:
        pass


def main(host, port, user, pw, iterations):
    sock = get_socket(host, port)
    throttle=int(iterations)
    send_logon(sock, user, pw,throttle)
    do_recv(sock)
    time.sleep(.2)
    loop=1
   
    while(loop<=throttle):
        heartbeat_test(sock,user)
        print(f"We are on loop number:{loop}")
        do_recv(sock)
        time.sleep(.9)
        do_recv(sock)
        loop=loop+1
    time.sleep(1)      
    do_recv(sock)

    time.sleep(2)
    do_recv(sock)
    print(f"Closing Socket {sock}")
    time.sleep(2)
    sock.close()
   
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='FIX Client')
    parser.add_argument('host', type=str, help='Server Host')
    parser.add_argument('port', type=int, help='Server Port')
    parser.add_argument('user', type=str, help='user')
    parser.add_argument('pw', type=str, help='pw')
    parser.add_argument('iterations',type=str, help='Number of Messages')
    args = parser.parse_args()
    print(args)
    main(args.host, args.port, args.user, args.pw, args.iterations)
