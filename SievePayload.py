#Sieve payload, XYZ12
import math

def DistSieveTarget((n, tlow, thigh), B=None):
	#sieve for use in threads of DistributedSieve
	#n == number to sieve
	#B = list of primes used to sieve
	#A = partition we want to sieve
	#tindex = first number A represents

	list1 = [True for _ in xrange(0, n+1)]#list of all numbers to sieve

	list2 = [True for _ in xrange(0, thigh-tlow+1)]#list of numbers in this partition

	outerlimit = math.sqrt(n)
	i = 2
	
	while i <= outerlimit:
		if list1[i]:
			p = i ** 2
			while p <= n:
				list1[p] = False
				p += i
				
			q = i ** 2
			while q <= thigh:
				if q < tlow:
					q += i
					continue
				try:
					list2[q-tlow] = False
				except:
					print tlow, thigh
					print q-tlow
					print list2
					print thigh-tlow+1
					raise IndexError
				q += i
		i += 1

	C = [val+tlow for val, j in enumerate(list2) if j]

	return C

def execute():
	return DistSieveTarget((n, tlow, thigh))

n = 101
tlow = 2
thigh = 101
