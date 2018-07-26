from re import *
from collections import OrderedDict
from NonTerminal import NonTerminal
from Terminal import Terminal
from getInput import production_list, nt_list , t_list 


def compute_first(symbol): #chr(1013) corresponds (ϵ) in Unicode

	global production_list, nt_list, t_list
# if X is a terminal then first(X) = X
	if symbol in t_list:
		return set(symbol)

	for prod in production_list:
		head, body = prod.split('->')
		
		if head != symbol: continue

# if X -> is a production, then first(X) = epsilon
		if body == '':
			nt_list[symbol].add_first(chr(1013))
			continue

		if body[0] == symbol: continue

		for i, Y in enumerate(body):
# for X -> Y1 Y2 ... Yn, first(X) = non-epsilon symbols in first(Y1)
# if first(Y1) contains epsilon, 
#	first(X) = non-epsilon symbols in first(Y2)
#	if first(Y2) contains epsilon
#   ...
			t = compute_first(Y)
			nt_list[symbol].add_first(t - set(chr(1013)))
			if chr(1013) not in t:
				break 
# for i=1 to n, if Yi contains epsilon, then first(X)=epsilon
			if i == len(body)-1: 
				nt_list[symbol].add_first(chr(1013))

	return nt_list[symbol].first

# ------------------------------------------------------------------

def get_first(symbol): 

	return compute_first(symbol)

# ------------------------------------------------------------------

