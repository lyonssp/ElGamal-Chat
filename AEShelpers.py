import sys,os,socket
from Crypto.Cipher import AES
from Crypto import Random
import pdb

#Display exception info from function name func
def displayException(funcName,e):
	print("%s in function %s: %s" %(type(e).__name__,funcName,str(e)))

#Pad and Unpad to create messages that are multiples of keylength#
def pad_msg(msg,keyLen):
	msg = msg + (keyLen - len(msg) % keyLen) * chr(keyLen - len(msg) % keyLen)
	return msg

def remove_pad_bytes(msg):
	msg = msg[:-ord(msg[len(msg)-1:])]
	return msg
#################################################################
