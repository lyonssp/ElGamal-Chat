import random
import pdb

#Compute a^b(mod m) with Rabin test embedded
def riggedExpMod(a,b,m):
	if b == 0:
			return 1
	elif b%2 == 0:
			y = riggedExpMod(a, b/2, m)
			z = pow(y,2,m)
			#Rabin test for nontrivial roots of unity
			if(z==1 and y!=1 and y!=m-1):
					#m cannot be prime if y^2 = 1(mod m) and y != +1 or -1
					return 0
			else:
					return z
	else:
			y = riggedExpMod(a,b-1,m)
			z = (a*y)%m
			return z	

#Miller-Rabin primality testing
def is_prime(n, confidence):
	while(confidence > 0):
			a = random.randint(1,n-1)
			if(riggedExpMod(a,n,n) != a):
					return False
			confidence -= 1
	
	return True

#generate a k-bit prime with the primality of the result guaranteed with a certain confidence
def gen_prime(k,confidence):
	lowPrimeRange = pow(2,k-1)
	highPrimeRange = pow(2,k)-1

	while 1:
		p = random.randrange(lowPrimeRange, highPrimeRange)
		if(is_prime(p,confidence)):
				break
	return p

#is g a generator for the integers mod p
def is_generator(g,p):
	return not (pow(g,1,p)==1 or pow(g,2,p)==1 or pow(g,(p-1)/2,p)==1)

#returns a generator for the integers mod p
def find_generator(p):
	while 1:
			g = random.randrange(1,p-1)
			if(is_generator(g,p)):
					break
	return g

#security parameter k determines bit length of prime p
#confidence determines confidence that p is prime
#return a list of the public keys [p,g,b] and a secret key a
def eg_setup(k,confidence):
	p = gen_prime(k,confidence)
	print("Prime p = %d OK" %p)
	g = find_generator(p)
	print("Generator g = %d OK" %g)
	a = random.randrange(1,p-1)
	print("Secret Key a = %d OK" %a)
	b = pow(g,a,p)
	print("Public b = %d OK" %b)

	return ([p,g,b],a)

#use public generator g and public value b to compute:
#	v = g^u (mod p)
#	z = b^u (mod p)
#	encrypted_msg = msg*z (mod p)
#return the pair <v,encrypted_msg>
def eg_msg_mask_pair(msg,p,g,b):
	u = random.randrange(1,p-1)
	v = pow(g,u,p)	
	z = pow(b,u,p)
	#convert msg bytes into long and apply ElGamal encryption function
	encrypted_msg = (int(msg.encode('hex'),16)*z)%p
	return str((v,encrypted_msg))

#assumes messages were sent as bytes and converted to long for encryption
def eg_decrypt(encryptedMsg, halfMask, secKey, p):
	fullMask = pow(halfMask,secKey,p)
	decryptedMsgLong = (encryptedMsg*modinv(fullMask,p))%p
	decryptedMsgHex = hex(decryptedMsgLong)
	decryptedMsgBytes = decryptedMsgHex[2:-1].strip().decode('hex')
	return decryptedMsgBytes


def egcd(a, b):
	if a == 0:
		return (b, 0, 1)
	else:
		g, y, x = egcd(b % a, a)
		return (g, x - (b // a) * y, y)

def modinv(a, m):
	g, x, y = egcd(a, m)
	if g != 1:
		raise Exception('modular inverse does not exist')					    
	else:
		return x % m
