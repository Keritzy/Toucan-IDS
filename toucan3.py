# -*- coding: utf-8 -*-

#----------------------------------------
# Toucan WIDS 
# Author: Splithor1zon (Collin Sullivan)
# Created: 2017
#----------------------------------------

#--------------------------------------------------------------------------------------------------------------------------------
# Monitors a LAN and will protect against spoofing attacks for MITM purposes
# 1. Scans Network for Active Hosts
# 2. Scans hosts for Layer 2 Addresses and can "attack back" when a MITM is discovered by correcting poisoned hosts
# 3. Will send ALERT 
# Needs to be run as ROOT
#--------------------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------------------------
#                    GNU GENERAL PUBLIC LICENSE
#                      Version 3, 29 June 2007

# Copyright (C) William Collin Sullivan <wcsullivan@oru.edu>
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#--------------------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------------------------

# TO DO:
# 1. Option parser for fast use - but then you don't get to seee my toucan =( 

#--------------------------------------------------------------------------------------------------------------------------------


import logging
import socket, sys
from scapy.error import Scapy_Exception
from scapy.all import sr1,IP,ICMP
from scapy.all import srp
from scapy.all import Ether, ARP, conf
from scapy.all import IPv6
from scapy.all import *
import os
import sys
import threading
from threading import Thread
from optparse import OptionParser
import signal
from struct import *
import time



logging.basicConfig(filename='toucan.log',level=logging.DEBUG)


print("\033[31m'                                                                                                        ............ ")
print("\033[33m'                                                                                                ..............-.-----. ")
print("\033[32m'                                         .-.                                               ..--.........:---:-------:- ")
print("\033[31m'                                           .--                                          .-:-........:-:-:---....``````. ")
print("\033[32m'                                            `.-.`````````.-:-.                     .-//:-.....--:::----.. ")
print("\033[31m'                                            `..--..`````.-:+:-..-//:.           -+sdmmo-..-.--/::----. ")
print("\033[32m'                                            .-///.--:/-.`..-:+///-.:/:.        +hm   h/.--+::-----. ")
print("\033[31m'                                            .--/:::-.``-:+-.--/-/+/-----      hmdhssysy/://:::::.")
print("\033[31m'                                                    ````....-:---.``.``````+mddhddddmd//+oyds.")
print("\033[32m'                                            ..::--...-````....---...```````ommmmddmmmmmsdmmNs")
print("\033[31m'                                            ..-.-:-...``````..-::-:-`.````ommdddmmmmmdddmmmh.")
print("\033[31m'                                            ...-::...```````:--:/::```-+hmmddhdmmdyhhhhmmm+`")
print("\033[31m'                                           .---.-:...```````-.-::+--/sdmmdhhhyyddddhhddmmm-")
print("\033[31m'                                            -.`.--...``````.:/oshdddmddddhhyyyssdmdddddmmm.")
print("\033[37m'                                                .....````-+ydmmNmmmmddddmmhyyyssosydmdmmmmd.")
print("\033[32m'                                                `...```.+hmmmmmmmddddddmNNmhyyyssooosyhdmNNh`")
print("\033[33m'                                                .````.odddddddhdddddmmmNNNmdyyysosoosyyhddh/")
print("\033[33m'                                                   +dmdddddhddddhdddmmNNNmdyyysoossyyhddh+")
print("\033[31m'                                                 -ydddddddddddddmddhdmmdddddhyyyyyyhhddh+")
print("\033[31m'                              ``.`.`            dddddddddddddddhdhydmhhyhmmdhyyyhhddhy:")
print("\033[32m'                                .-:-..`.       dddddhdddddyssyhhyyyyddyhhhmmmmdddddds.```.----...````.-..")
print("\033[33m'                                 .-:+/:..    /dddddhdddho///osyyssssydddddmNNNNNNNms....:::--------.--:-.")
print("\033[35m'                                         /:-. :oyhhhhhhs+//:://ossssssyhdmmNNNNNNNd+---://:::----//-----:.")
print("\033[33m'                                            +::::++oss/ss+:::-:osysssssydmmNNNmds:-:/++o:-:::.-:--.-....")
print("\033[31m'                                            -yyyo++//+/+/ssy++/--:oossyyyhhdmmhss:...+o+/:::-.---........")
print("\033[34m'                                            ddhyyysysso+ysh:-:::::/+syhhhdhy+-`-:.`.s+/:----..........")
print("\033[37m'                                           +mdhhhyymyhshy+o+/:-.-:///+oss+:.`````::-s/::::+:::-")
print("\033[33m'                                           ymddhyhhdssy+:-:+ys/:..-/+/:---````````.:+/:---/---.")
print("\033[32m'                                           ddh+hdmhs+s+----/hhssoo+-://oyyo.````````-//:-:--..")
print("\033[31m'                                           dy+.hmdy+//::-:-ohhyyyoso+::yssy:..````````-/++:-..")
print("\033[32m'                                          :y+.-ydhs+---::.`:ooo++/:/sooh+yy/+::::-----:-+so+::-:-....``.........`")
print("\033[32m'                                          :/:`--/ys+-.-:.````....``.--:/sh+/::::-....-----...........`.-.-.-:```...```.-````--")
print("\033[32m'                                          ./.````ss/---/+-             :o/+o+o++/::::--::--.--..:--//-:-:::--...-.````..````.`")
print("\033[32m'                                                 oy+---::+-            ...-:/-://oooooos+ooo+/+//+//::/:--.")
print("\033[32m'                                                 .hs:-:+::+-            ....-.-````````....-..-..---...")
print("\033[32m'                                                  sy://so/:+-")
print("\033[32m'                                                  -h/ososo///.  ")
print("\033[32m'                                                   oo+yyo/so/.``````.--...........-----.-.......`")
print("\033[32m'                                                   -s+yyso:+o-```````````````")
print("\033[32m'                                                    osssyoo:/o.               ")
print("\033[32m'                                                    :o+osys+:o/                        .....-://oo/---////:.////:.////:.")
print("\033[31m'                                                    .s/oyyyo+/o-                        ``..-.          TOUCAN ")
print("\033[32m'                                                     -+/+yho+o++.                            `+o///---////:.////:.////:.")
print("\033[32m'                                                     .+/+hhs//s:`                             ")
print("\033[32m'                                                      //ohyys:oo`")
print("\033[32m'                                                      .s:ssyys:s:")
print("\033[32m'                                                        //+oyyy+/+")
print("\033[32m'                                                       `-o/oyyo+s+")
print("\033[32m'                                                        /ooshs:/s-  ")                             
print("\033[32m'                                                        .o:oyho/oo   ")                            
print("\033[32m'                                                        `//oshss+o    ")                          
print("\033[32m'                                                         ./+ys++os")
print("\033[32m'                                                          `.+/os++                              The world is a jungle in general, and the")
print("\033[32m'                                                           `-//:-.                              networking game contributes many animals.")
print("\033[32m'                                                                                                - RFC 826")
print("\033[32m'Written by: Collin Sullivan, a.k.a Splithor1zon\033[0m")

os.system("espeak 'Welcome to Toucan'")

class colors:

    Red ='\033[31m'

    Green ='\033[32m'

    Yellow ='\033[33m'

    Blue ='\033[34m'

    Pink ='\033[35m'

    Cyan ='\033[36m'

    White ='\033[37m'

    ENDC = '\033[0m'


time_current = time.strftime("%I:%M:%S\n")
logging.info('%s' % time_current)


date_current = time.strftime("%d/%m/%Y\n")
logging.info('%s' % date_current)


print(colors.Yellow + """
Toucan is an Intrusion Detection System. Capabilities include scanning and defending hosts on a network by actively 
monitoring traffic for different types of known attacks by maleficent users. This program is not to be used on an
unauthorized network and the creator is not responsible for any damage done. Using this programmeans you understand and agree to these conditions.
\n""" + colors.ENDC)

print(time_current)
print(date_current)


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):

    str_format = "{0:." + str(decimals) + "f}"

    percents = str_format.format(100 * (iteration / float(total)))

    filled_length = int(round(bar_length * iteration / float(total)))

    bar = '\033[32m■\033[0m' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def get_mac_address(ip_address):

    response, unanswered = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip_address), \
        timeout=2, retry=2)

    for s, r in response:
        return r[Ether].src
    return None

    logging.info('Gateway Layer 2 address is: %s' % r[Ether].src)

    GATEWAY_MAC = "%s" % r[Ether].src

    
def get_mac_address_v6(ip_address):

    response, unanswered = srp(Ether(dst='33:33:00:00:00:02')/IPv6(dst="FF02::2")/ICMPv6ND_RS(code = 133), \
        timeout = 2, retry = 2)

    for s, r in response:
        return r[Ether].src
    return None

    logging.info('Gateway Layer 2 address is: %s' % r[Ether].src)

    GATEWAY_MAC = "%s" % r[Ether].src


def arp_network_range(iprange):

    logging.info('Sending ARPs to network range')

    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=iprange), timeout=5)

    ip_collection = []

    eth_collection = []

    for snd, rcv in ans:

        host_ip_address = rcv.sprintf(r"%ARP.psrc%")

        host_eth_address = rcv.sprintf(r"%Ether.src%")

        logging.info("{}".format(host_ip_address))

        logging.info("{}".format(host_eth_address))
        
        ip_collection.append(host_ip_address)

        eth_collection.append(host_eth_address)

    print("Host List IP Addresses:")
    for host_ip in ip_collection:
        print(host_ip)

    print("Host List Ethernet Addresses:")
    for host_eth in eth_collection:
        print(host_eth)

    with open("toucan_hosts.txt", "w") as output:

        output.write(str(ip_collection))
        output.write(str(eth_collection))

        
def arp_display(packet):

    global attacker_L2
    global attacker_L3
    global victim_L3
    global victim_MAC

    if packet[ARP].op == 1: 

        print("\033[31m[1] ARP Request Ethernet Info: [Source] = {} + [Destination] = {} \033[0m".format(packet[Ether].src, packet[Ether].dst))

        print("\033[31m[1] ARP Request- {} is asking for L2 of {} \033[0m".format(packet[ARP].psrc, packet[ARP].pdst))

    if packet[ARP].op == 1 and packet[ARP].psrc == GATEWAY_IP and packet[Ether].src != GATEWAY_MAC:

        return "\033[31m[!]WARNING: GATEWAY IMPERSONTATION DETECTED. POSSIBLE MITM ATTACK FROM %s\033[31m".format(packet[ARP].hwsrc)

        attacker_L2 = packet[ARP].hwsrc

        victim_L3 = packet[ARP].dst

        victim_MAC = packet[Ether].dst

    if packet[ARP].op == 1 and packet[ARP].psrc == GATEWAY_IP and packet[ARP].hwsrc != GATEWAY_MAC:

        print("\033[31m[!]WARNING: GATEWAY IMPERSONTATION DETECTED. POSSIBLE MITM ATTACK FROM %s\033[31m".format(packet[ARP].hwsrc))

        attacker_L2 = packet[ARP].hwsrc

        victim_L3 = packet[ARP].dst

        victim_MAC = packet[Ether].dst

    if packet[ARP].op == 2: 

        logging.info("[2] ARP Response- {} has layer 2 address: {}".format(packet[ARP].psrc, packet[ARP].hwsrc))

        print("\033[33m[2] Reponse Ethernet Info: [Source] = {} + [Destination] = {} \033[0m".format(packet[Ether].src, packet[Ether].dst))

        print("\033[33m[2] ARP Response- {} has layer 2 address: {}\033[0m".format(packet[ARP].psrc, packet[ARP].hwsrc))


    if packet[ARP].op == 2 and packet[ARP].psrc == GATEWAY_IP and packet[Ether].src != GATEWAY_MAC:

        print("\033[31m[!]WARNING: GATEWAY IMPERSONTATION DETECTED. POSSIBLE MITM ATTACK FROM {} \033[31m".format(packet[ARP].hwsrc))

        attacker_L2 = packet[ARP].hwsrc

        victim_L3 = packet[ARP].dst

        victim_MAC = packet[Ether].dst

    if packet[ARP].op == 2 and packet[ARP].psrc == GATEWAY_IP and packet[ARP].hwsrc != GATEWAY_MAC:

        print("\033[31m[!]WARNING: GATEWAY IMPERSONTATION DETECTED. POSSIBLE MITM ATTACK FROM {}\033[31m".format(packet[ARP].hwsrc))

        attacker_L2 = packet[ARP].hwsrc

        victim_L3 = packet[ARP].dst

        victim_MAC = packet[Ether].dst
      

def na_packet_discovery(neighbor_adv_packet):

  if neighbor_adv_packet.haslayer(IPv6) and neighbor_adv_packet.haslayer(ICMPv6ND_NA):

    print("[NA-Ether] Neighbor advertisement layer 2 information: Source- {}, Destination- {}".format(neighbor_adv_packet[Ether].src, neighbor_adv_packet[Ether].dst))

    print("[NA] Neighbor advertisement layer 3 information: Source- {}, Destination- {} ".format(neighbor_adv_packet[IPv6].src, neighbor_adv_packet[IPv6].dst))  

    logging.info("Neighbor advertisement source: {}, destination: {}".format(neighbor_adv_packet[IPv6].src, neighbor_adv_packet[IPv6].dst))


def na_packet_discovery_v6(neighbor_adv_packet):

  if neighbor_adv_packet.haslayer(IPv6) and neighbor_adv_packet.haslayer(ICMPv6ND_NA):

    print("[NA-Ether] Neighbor advertisement layer 2 information: Source- {}, Destination- {}".format(neighbor_adv_packet[Ether].src, neighbor_adv_packet[Ether].dst))

    print("[NA] Neighbor advertisement layer 3 information: Source- {}, Destination- {} ".format(neighbor_adv_packet[IPv6].src, neighbor_adv_packet[IPv6].dst))  

    logging.info("Neighbor advertisement source: {}, destination: {}").format(neighbor_adv_packet[IPv6].src, neighbor_adv_packet[IPv6].dst)

  if neighbor_adv_packet["IPv6"].src == GATEWAY_IP and neighbor_adv_packet["ICMPv6NDOptDstLLAddr"].lladdr != GATEWAY_MAC:

    print("\033[31m[!]WARNING: IPv6 GATEWAY IMPERSONATION DETECTED. POSSIBLE MITM ATTACK FROM: {} (L2): {}\033[0m".format(neighbor_adv_packet[IPv6].src, neighbor_adv_packet[Ether].src))

  if neighbor_adv_packet["IPv6"].src == host_ip_address in ip_collection and neighbor_adv_packet["ICMPv6NDOptDstLLAddr"].lladdr != host_eth_address in eth_collection:

    print("\033[31m[!]WARNING: IPv6 GATEWAY IMPERSONATION DETECTED. POSSIBLE MITM ATTACK FROM: {} (L2): {}\033[0m".format(neighbor_adv_packet[IPv6].src, neighbor_adv_packet[Ether].src))


def ns_packet_discovery(neighbor_sol_packet):

  if neighbor_sol_packet.haslayer(IPv6) and neighbor_sol_packet.haslayer(ICMPv6ND_NS):

    print("[NS-Ether] Neighbor solicitation layer 2 information: Source- {}, Destination- {}".format(neighbor_sol_packet[Ether].src, neighbor_sol_packet[Ether].dst))    

    print("\033[32m[NS] Neighbor solicitation source: {}, destination: {}\033[0m".format(neighbor_sol_packet[IPv6].src, neighbor_sol_packet[IPv6].dst))

    logging.info("Neighbor solicitation source: {}, destination: {}".format(neighbor_sol_packet[IPv6].src, neighbor_sol_packet[IPv6].dst))


def detect_deauth(deauth_packet):

    if deauth_packet.haslayer(Dot11) and deauth_packet.haslayer(Dot11Deauth):

        print("\033[31m[!] Deauthentication Detected from: {} on Access Point {}\033[0m".format(deauth_packet[Dot11].addr1, deauth_packet[Dot11].addr2))

        logging.warning("Deauth detected from {}".format(deauth_packet[Dot11].addr1))
        logging.warning("Sending option to repond to deauthentication...")

    #need to write deauth response


def detect_router_advertisement_flood(ra_packet):

    if ra_packet.haslayer(IPv6) and ra_packet.haslayer(ICMPv6ND_RA): 

        print("[RA] Router advertisement discovered from {} with Layer 2 address: {}".format(ra_packet[IPv6].src, ra_packet[Ether].src)) 

        logging.info("Router advertisement from %s with Layer 2 address: {}".format(ra_packet[IPv6].src, ra_packet[Ether].src))

    if ra_packet[Ether].src != GATEWAY_MAC:

        print("""\033[31m

        [RA] POSSIBLE MALICIOUS ROUTER ADVERTISEMENT DISCOVERED: 

        Layer 2 Source: {}
        Layer 3 Source: {} 
        Prefix: {}
        lladdr: {}
        \033[0m""".format(ra_packet[Ether].src, ra_packet[IPv6].src, ra_packet[ICMPv6NDOptPrefixInfo].prefix, ra_packet[ICMPv6NDOptSrcLLAddr].lladdr))


def detect_router_advertisement_packet(ra_packet):

    if ra_packet.haslayer(IPv6) and ra_packet.haslayer(ICMPv6ND_RA):  

        print("\033[32m[RA] Router advertisement discovered from {} with Layer 2 address: {}\033[0m".format(ra_packet[IPv6].src, ra_packet[Ether].src))

        logging.info('Router advertisement from {} with Layer 2 address: {}'.format(ra_packet[IPv6].src, ra_packet[Ether].src)) 


def defensive_arps(GATEWAY_IP, GATEWAY_MAC, victim_L3, victim_MAC):

    un_poison_victim = ARP()

    un_poison_victim.op = 2

    un_poison_victim.psrc = gateway_ip

    un_poison_victim.pdst = victim_L3

    un_poison_victim.hwsrc = GATEWAY_MAC

    un_poison_gateway = ARP()

    un_poison_gateway.op = 2

    un_poison_gateway.psrc = victim_L3

    un_poison_gateway.pdst = gateway_ip

    un_poison_gateway.hwsrc = victim_MAC

    send(un_poison_victim)
    
    send(un_poison_gateway)

    time.sleep(2)

    print("Sent defensive ARP to restore {}".format(victim_L3))

    print("Sent defensive ARP to restore {}".format(GATEWAY_IP))


def defensive_deauth(GATEWAY_MAC, Attacker_Deauth_Layer2):

  conf.iface = interface
  
  bssid = GATEWAY_MAC 

  count = 77

  conf.verb = 0 

  packet = RadioTap()/Dot11(type=0, subtype=12, addr1=Attacker_Deauth_Layer2, addr2=bssid, addr3=bssid)/Dot11Deauth(reason=7) 

  logging.info("Intruder at {} is being kicked off network {}".format(Attacker_Deauth_Layer2))

  for n in range(int(count)):

    sendp(packet)

    print("\033[32mRemoving malicious host at with Layer 2 address: {}".format(attacker_L2))


def sniff_arps():

  sniff(filter = "arp", prn = arp_display)


def sniff_deauth():

  sniff(iface="{}".format(wifi_interface), prn = detect_deauth)


def sniff_ns():

  sniff(iface="{}".format(interface), prn = ns_packet_discovery) 


def sniff_na():

  sniff(iface="{}".format(interface), prn = na_packet_discovery)


def sniff_na_ipv6():

  sniff(iface="{}".format(interface), prn = na_packet_discovery_v6)


def sniff_ra():

  sniff(iface="{}".format(interface), prn = detect_router_advertisement_packet)


def sniff_ra_v6_detect_flood():

  sniff(iface="{}".format(interface), prn = detect_router_advertisement_flood)  


if __name__ == '__main__':

    counter = 0

    attacker_L2 = ''    

    attacker_L3 = ''    

    victim_MAC = '' 

    victim_L3 = ''  

    RA_attacker_L3 = '' 

    RA_attacker_L2 = '' 

    GATEWAY_IP = input("\033[33mEnter your Gateway Layer 3 Address: \033[0m")   

    logging.info("Gateway IP: {}".format(GATEWAY_IP)) 

    interface = input("\033[32m\nEnter your Network Interface: \033[0m")    

    logging.info('Interface: %s' % interface)   

    n_range = input("\033[31m\nEnter your network range to defend (in format 10.0.0.1/24): \033[0m")    

    logging.info('Network range to defend: %s' % n_range)

    print("\n")
    
    input_one = input("""\033[35m
____________________________________________________________
____________________________________________________________
-                                                          -
- Mr. Toucan, are you defending an IPv4 or IPv6 network?   -
-                                                          -
-                                                          -
- 1. IPv4                                                  -
- 2. IPv6                                                  -
____________________________________________________________
____________________________________________________________

\033[0m\n""")

    input_two = input("""\033[35m
____________________________________________________________
____________________________________________________________
-                                                          -
- Mr. Toucan, are you sniffing for deauthentication frames?-
-                                                          - 
-                                                          -
- 1. Yes                                                   -
- 2. No                                                    -
____________________________________________________________
____________________________________________________________
\033[0m\n""")

    if input_one == "1" or "yes" or "Yes" or "Y" or "y":
        GATEWAY_MAC = get_mac_address(GATEWAY_IP)

    elif input_one == "2" or "no" or "No" or "N" or "n":
        GATEWAY_MAC = get_mac_address_v6(GATEWAY_IP)

    if input_two == "1":

        wifi_interface = input("Please enter your wireless interface to sniff on: ")

        os.system('sudo ifconfig {} down').format(wifi_interface)

        os.system('sudo iwconfig {} mode monitor').format(wifi_interface)

        os.system('sudo ifconfig {} up').format(wifi_interface)

    elif input_two == "2":
        print("Ok")
    
    print(colors.Red + "[*] Gateway Locked in...") 
    print_progress(iteration = 100, total = 100)
    time.sleep(.4)
    print("\n")
    print(colors.Yellow + "[*] Interface configured...")
    print_progress(iteration = 100, total = 100)
    time.sleep(.4)
    print("\n")   
    print(colors.Green +"[*] Network Range set...")
    print_progress(iteration = 100, total = 100)
    time.sleep(.4)
    print("\n")
    print(colors.Pink +"[*] Commensing..." + colors.ENDC)
    print_progress(iteration = 100, total = 100)
    print("\n")

    GATEWAY_MAC = get_mac_address(GATEWAY_IP)

    print(colors.Red + "\n [*] Gateway {} is locked in at {}".format(GATEWAY_IP, GATEWAY_MAC)) 


    answer = True
    
    while answer:
        
    #need to work on this menu a bit 
    
        answer =input("""\033[33m
        __________________________________
        __________________________________

        -          TOUCAN MENU           -
        Its' a menu... but not for toucans
        __________________________________
        __________________________________

        - [1] Scan for hosts to protect -
        - [2] Start Monitoring (IPv4)   -
        - [3] Start Monitoring (IPv6)   -
        - [4] Deauthenticate Attacker   -
        - [5] Send Defensive ARPs       -
        - [6] Exit                      -
        __________________________________
        __________________________________
        
        Please select an option: \033[0m""") 
    
        if answer =="1": 
          
          print("\033[35m[*]Sending ARPs to scan network range...\033[0m")

          network_range = arp_network_range(n_range)

        elif answer =="2":

            try:

                Thread(target = sniff_arps).start()                          

                Thread(target = sniff_ns).start()           

                Thread(target = sniff_na).start()           

                Thread(target = sniff_ra).start() 

            except KeyboardInterrupt:

                sys.exit()

        elif answer =="3":

            try:

                Thread(target = sniff_arps).start()                         

                Thread(target = sniff_ns).start()           

                Thread(target = sniff_na_ipv6).start()           

                Thread(target = sniff_ra_v6_detect_flood).start() 

            except KeyboardInterrupt:

                sys.exit()
    
        elif answer =="4":

            DeauthAttacker = input("Please enter attacker's layer 3 address: ")

            Attacker_Deauth_Layer2 = get_mac_address(DeauthAttacker)
    
            defensive_deauth()

        elif answer == "5":

            defensive_arps()

        elif answer =="6":

          print("\n\033[35m Exiting...\033[0m") 

          answer = None

          sys.exit()
    
        elif answer !="":
    
          print("\033[35m[!]Not Valid Option...\033[0m") 

   
