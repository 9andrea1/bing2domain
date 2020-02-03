#!/usr/bin/env python
import urllib, httplib, re, commands, sys
from termcolor import colored #except ImportError
from netaddr import *

latest_ip="" ########## manca nella versione di erik

# main ext function
def do(IP, NET):
        try:
                resp = search(str(IP))
                find_and_print(resp, NET, str(IP))
        except IndexError:
                # getcountpage exception: no results for current ip
                None
        except:
                None


# bing search based on ip, starting from 'i'
def search(IP):
        conn.request("GET","/search?q=IP:"+IP)
        response=conn.getresponse()
        resp = response.read()
        conn.close()
        return resp


# find link in html response and print
def find_and_print(resp, net, ip):
        global latest_ip
        res = []
        # get results list
        res = re.findall('<li class="b_algo".*?href="(.*?)".*?</a>',resp)
        if net==1 and len(res)>0 and latest_ip!=ip:
                print "\nIP: " + colored(ip,"green")
                latest_ip = ip
        # print the list
        for i in range(0,len(res)):
                tmp = commands.getoutput("echo '%s' | sed 's/\&amp;/\&/g'" %res[i])
                pos = tmp.find("?")
                if pos > 0 :
                        print tmp[:pos]+colored(tmp[pos:],"cyan")
                else:
                        print tmp

#-----------------------------------------
#               MAIN                     -
#-----------------------------------------

url="www.bing.com"
conn=httplib.HTTPConnection(url,80)

# check input type
HOST=sys.argv[1]# ip, url or network
if re.search("[0-9]+.[0-9]+.[0-9]+.[0-9]+",HOST):
        # IP
        if re.search("[0-9]+.[0-9]+.[0-9]+.[0-9]+/[1-3][0-9]",HOST):
                # NET
                print "Net " + HOST
                ip_list = IPNetwork(HOST)
                try: 
                        for ip in ip_list:
                                do(str(ip), 1)
                except KeyboardInterrupt: # if ctrl-c
                        print "\nAborting..."
                        sys.exit()
        else:
                # NO NET
                IP = HOST
                print "IP: " + IP
                do(IP,0)
else:
        # NO IP
        IPs = commands.getoutput("host %s | grep 'has address' | cut -d ' ' -f 4" %HOST)
        IP = IPs.split()
        if len(IP)>1: # if multi IP
                for i in range(0,len(IP)):
                        print "HOST " + HOST + " has IP " + colored(IP[i],"green")
                        do(IP[i],0)
                        print ""
        elif len(IP)==1: # 1 IP only
                print "HOST " + HOST + " has IP " + IP[0]
                do(IP[0],0)
        else: # not found
                print "Host not found"
