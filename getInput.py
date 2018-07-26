from collections import OrderedDict
from NonTerminal import NonTerminal
from Terminal import Terminal
from re import *

t_list = OrderedDict()
nt_list = OrderedDict()
production_list = []


def main():
	global production_list, t_list, nt_list
	ctr=1
	t_regex, nt_regex = r'[a-z\W]', r'[A-Z]'
	while True:
		production_list.append(input().replace(' ', ''))
		if production_list[-1].lower() in ['end', '']: 
			del production_list[-1]
			break

		head, body = production_list[ctr-1].split('->')

		if head not in nt_list.keys():
			nt_list[head] = NonTerminal(head)

		#for all terminals in the body of the production
		for i in finditer(t_regex, body):	#returns an iterator object in the ordered matched.
			s = i.group()			#since the group argument is empty, it'll return whatever it matched completely
			if s not in t_list.keys():
				t_list[s] = Terminal(s)

		#for all non-terminals in the body of the production
		for i in finditer(nt_regex, body):
			s = i.group()
			if s not in nt_list.keys():
				nt_list[s] = NonTerminal(s)
				
		ctr+=1


