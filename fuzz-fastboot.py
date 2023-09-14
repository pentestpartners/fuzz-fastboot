#!/usr/bin/env python3
import usb.core
import usb.util
import sys
import argparse
import string
from itertools import product
from tqdm.auto import tqdm,trange
#from tqdm.contrib.itertools import product


#dev=usb.core.find(idVendor=0x18d1, idProduct=0x4ee0)
dev=usb.core.find(idVendor=0x22b8, idProduct=0x2e80)

if dev is None:
	raise ValueError("Fastboot Device not found")

#epout=6
#epin=0x85
epout=1
epin=0x81
outfile="data.out"
blocksize=4096 * 1024

def send(dev, command):
	dev.write(epout, command)
	output=""
	ret=0
	while True:
		resp=dev.read(epin, 512, 200).tobytes().decode('utf-8')
		header = resp[:4]
		data   = resp[4:]
		if header == "INFO":
			output+=f"{data}\n"
		elif header == "OKAY":
			output+=f"Success: {data}\n"
			break
		elif header == "DATA":
			octets=int(data, 16)
			output+=f"Data response, {octets} octets"
			fileout=open(outfile, "wb")
			while octets > 0:
				r=blocksize
				if octets < blocksize: r=octets
				readdata=dev.read(epin, r, 1000)
				fileout.write(readdata)
				octets-=r
			fileout.close()
		else:
			output+=f"Error: {data}\n"
			ret=1
			break
	return ret,output

parse = argparse.ArgumentParser()
parse.add_argument("-l", "--log", nargs="?", help="Log to file")
parse.add_argument("-a", "--avoid", nargs="?", help="File of words to avoid")
parse.add_argument("-b", "--base", nargs="?", help="Base command, e.g. \"oem\"")
parse.add_argument("-f", "--match_fail", nargs="?", help="Match string for failure")
parse.add_argument("-r", "--bruteforce", type=int, help="Bruteforce characters up to parameter size")
parse.add_argument("dictionary", nargs="?", help="Dictionary of commands")

args = parse.parse_args()
logging = (args.log is not None)
base=" "
match_fail="not a supported oem command"

if logging: l=open(args.log,"w")
deny=[]
if args.avoid is not None:
	avoid=[line.strip() for line in open(args.avoid,"r")]
found=[]
restricted=[]
if args.dictionary is None and args.bruteforce is None:
	print("No dictionary files given")
	exit(1)
if args.base is not None: base=f"{args.base} "
if args.match_fail is not None: match_fail=args.match_fail
if args.bruteforce is None:
	words=[line.strip() for line in open(args.dictionary,"r")]
	longest=len(max(words, key=len))
	for word in (pbar := tqdm(words)):
		if word in avoid: continue
		if logging: l.write(f"TRYING: {base}{word}\n")
		pbar.set_postfix_str(word.ljust(longest,' '))
		(success, msg)=send(dev, f"{base}{word}")
		if logging: l.write(f"OUTPUT: {msg}")
		if match_fail not in msg:
			line=word
			found.append(word)
			if "command restricted" in msg:
				restricted.append(word)
				line+=" (restricted)"
				tqdm.write(f"Found {base}{line}") 
else:
	longest=args.bruteforce
	chars=string.ascii_lowercase+"-_"
	for ln in (pbar := trange(1, args.bruteforce+1)):
		for w in product(chars,repeat=ln):
			word=''.join(w)	
			if word in avoid: continue
			if logging: l.write(f"TRYING: {base}{word}\n")
			pbar.set_postfix_str(word.ljust(longest,' '))
			(success, msg)=send(dev, f"{base}{word}")
			if logging: l.write(f"OUTPUT: {msg}")
			if match_fail not in msg:
				line=word
				found.append(word)
				if "command restricted" in msg:
					restricted.append(word)
					line+=" (restricted)"
				tqdm.write(f"Found {base}{line}") 


