#!/usr/bin/env python
import urllib, httplib, re, commands, sys
from termcolor import colored #except ImportError
from netaddr import *


# global variables
cookie = ""
latest_ip = ""
flag_cookie = 0


# count result pages (10 link each)
def getcountpage(IP, cookie):
	conn.request("GET","/search?q=IP:"+IP+"&first=1000", headers={'Cookie':cookie})
	risposta=conn.getresponse()
	resp = risposta.read()
	conn.close()
	res = re.findall('<span class="sb_count">.*? .. (.*?) [a-z]+</span>',resp) # x-x di x risultati
	if len(res) == 0: # se meno di 10 risultati -> 1 pagina
		res = re.findall('<span class="sb_count">(.*?) [a-z]+</span>',resp) # x risultati
	return int(res[0])/10


# main ext function
def do(IP, NET):
	global cookie
	global flag_cookie
	if flag_cookie == 0: # if no cookie
		cookie = getcookie(IP)
		flag_cookie = 1
	try:
		num = getcountpage(IP, cookie) # int-> 0 meno di 10, 1 tra 10 e 20 ecc
		for i in range(1, (num+1)*10, 10): # first=1,11,21 ecc
			resp = search(str(IP),str(i))
			find_and_print(resp, NET, str(IP))
	except IndexError:
		# getcountpage exception: no results for current ip
		None	
	except:
		None
	

# get session cookie
def getcookie(IP):
	conn.request("GET","/search?q=IP:"+IP)
	response = conn.getresponse()
	cookies = response.getheader('set-cookie')
	pos = re.search('MUID=(.*?);',cookies).span()
	cookie = cookies[pos[0]:pos[1]]
	conn.close()
	return cookie


# bing search based on ip, starting from 'i'
def search(IP, i):
	conn.request("GET","/search?q=IP:"+IP+"&first="+i)
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
#		MAIN                     -
#-----------------------------------------

url="www.bing.com"
conn=httplib.HTTPConnection(url,80)

# check input type
print "Insert ip, url or network"
HOST=raw_input("$> ")
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
	
