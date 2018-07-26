from collections import deque
from collections import OrderedDict
from pprint import pprint
import first
import getInput
from getInput import production_list, nt_list as ntl, t_list as tl
from Stack import Stack
nt_list, t_list=[], []

class State:
	_id=0
	def __init__(self, closure):
		self.closure = closure
		self.no = State._id
		State._id += 1

class Item(str):
	def __new__(cls, item, lookahead = list()):
		self = str.__new__(cls, item)
		self.lookahead = lookahead
		return self

	def __str__(self):
		return super(Item, self).__str__()+", "+'|'.join(self.lookahead)
		

def closure(items):

	def exists(newitem, items):

		for i in items:
			if i==newitem and sorted(set(i.lookahead)) == sorted(set(newitem.lookahead)):
				return True
		return False


	global production_list

	while True:
		flag=0
		for i in items:	
			
			if i.index('.') == len(i)-1:      #if the "." is at the end of the prod, do nothing
				continue

			Y = i.split('->')[1].split('.')[1][0]	#get the non - terminal after the "."

			if i.index('.') + 1 < len(i) - 1: #In the grammar of the form S->a.BY,$ compute the first(Y)
				lastr = list(first.compute_first(i[i.index('.')+2])-set(chr(1013)))	
				
			else:
				#if the dot was at the end i.e. of the form S->AB.,$, then the first will be the lookhead itself
				lastr = i.lookahead
			#Populate the itemset with the corresponding Non - Terminal's productions and lookahead for it
			for prod in production_list:
				head, body=prod.split('->')
				
				if head!=Y:
					continue
				
				newitem = Item(Y+'->.'+body, lastr)
				#if that correspondin item doesn't exist in the item list we add it
				if not exists(newitem, items):
					#print("EEEEEEEEEEEEXXXXXXXXISSSSSTSSSSS",newitem,items)
					items.append(newitem)
					#print("AFTER ADDING",items)
					flag = 1
		if flag == 0:
			break

	return items

def goto(items, symbol):

	global production_list
	initial=[]

	for i in items:
		if i.index('.') == len(i)-1: #if all the symbols r seen, i.e. of the form S->B.
			continue

		head, body = i.split('->')
		seen, unseen = body.split('.') #split the RHS of productions into seen and unseen, i.e. before and after the "."


		if unseen[0] == symbol and len(unseen) >= 1:	#the symbol can be an epsilon too
			initial.append(Item(head+'->'+seen+unseen[0]+'.'+unseen[1:], i.lookahead))

	return closure(initial)	


def calc_states():

	def contains(states, t):

		for s in states:
			if len(s) != len(t): continue

			if sorted(s)==sorted(t):
				for i in range(len(s)):
						if s[i].lookahead!=t[i].lookahead: break
				else: return True

		return False

	global production_list, nt_list, t_list

	head, body=production_list[0].split('->')

	
	states = [closure([Item(head+'->.'+body, ['$'])])] #get first state wrt "Z->.S,$"

	
	while True:
		flag=0
		for s in states:

			for e in nt_list+t_list:	#for every non - terminal or terminal compute the goto for it
				#here we are performing goto for a state with every Symbol and performing a closure on that production there itself
				t = goto(s, e)
				if t == [] or contains(states, t):	#TOSEE
					continue

				states.append(t)
				flag = 1

		if not flag:
			break
	
	return states 


def make_table(states):

	global nt_list, t_list

	def getstateno(t):

		for s in states:
			if len(s.closure) != len(t):
				continue

			if sorted(s.closure)==sorted(t):
				for i in range(len(s.closure)):
						if s.closure[i].lookahead != t[i].lookahead:
							break
				else:
					return s.no

		return -1

	def getprodno(closure):		#returns the corresponding production number without considering the augmented production

		closure=''.join(closure).replace('.', '')
		return production_list.index(closure)

	SLR_Table = OrderedDict()
#	print(states)
	#convert the states to a list of object of states
	for i in range(len(states)):
		states[i] = State(states[i])
		#print("S?TAASDFS???????",states[i])

	#print("%%%%%%%%%%%%%%%%",states[0].closure)
	for s in states:
		SLR_Table[s.no] = OrderedDict()

		for item in s.closure:
			head, body = item.split('->')
			'''
			if body == '.': 
				print("TOOOOOOOOOOOOOORU")
				for term in item.lookahead: 
					if term not in SLR_Table[s.no].keys():
						SLR_Table[s.no][term]={'r'+str(getprodno(item))}
					else: SLR_Table[s.no][term] |= {'r'+str(getprodno(item))}
				continue
			'''
			nextsym = body.split('.')[1]
			#if we have seeen till the end of the production body and since it involves reduce operation, we denot it by r+production number
			if nextsym == '':
				if getprodno(item) == 0:	#if its the first production and we have a $ then we accept.
					SLR_Table[s.no]['$'] = 'accept'
				else:
					for term in item.lookahead: 
						if term not in SLR_Table[s.no].keys():	
							SLR_Table[s.no][term]={'r'+str(getprodno(item))}
						else: SLR_Table[s.no][term] |= {'r'+str(getprodno(item))}
				continue
			#Here we perform a shift operation by denoting s+the corresponding production number
			nextsym = nextsym[0]
			t = goto(s.closure, nextsym)
			if t != []: 
				if nextsym in t_list:	#This is only for a terminal
					if nextsym not in SLR_Table[s.no].keys():
						SLR_Table[s.no][nextsym]={'s'+str(getstateno(t))}
					else: SLR_Table[s.no][nextsym] |= {'s'+str(getstateno(t))}

				else:	#This is for nextsym being a non - terminal
					SLR_Table[s.no][nextsym] = str(getstateno(t))

	return SLR_Table

#Augment with that non terminal symbol which is not present in the given grammar.
def augment_grammar():
	for i in range(ord('Z'), ord('A')-1, -1):
		if chr(i) not in nt_list:
			start_prod=production_list[0]
			production_list.insert(0, chr(i)+'->'+start_prod.split('->')[0]) 
			return

def run():

	global production_list, ntl, nt_list, tl, t_list	

	getInput.main()

	print("\tFIRST OF NON-TERMINALS")
	for nt in ntl:
		first.compute_first(nt)
		print(nt)
		print("\tFirst:\t", first.get_first(nt))
		
	
	augment_grammar()
	nt_list = list(ntl.keys())
	t_list = list(tl.keys()) + ['$']

	#print(nt_list)
	#print(t_list)

	j = calc_states()	#compute the states for the automaton
	
	#for i in j:
	#	print(j)
	#PRINT THE STATES
	ctr=0
	for s in j:
		print("Item{}:".format(ctr))
		for i in s:
			print("\t", i)
		ctr+=1
	
	table = make_table(j)

	print("\n\tCLR(1) TABLE\n")

	sr, rr = 0, 0

	for i, j in table.items():
		print(i, "\t", j)
		s, r=0, 0

		for p in j.values():
			if p!='accept' and len(p)>1:
				p = list(p)
				if('r' in p[0]): r+=1
				else: s+=1
				if('r' in p[1]): r+=1
				else: s+=1		
		if r>0 and s>0: sr+=1
		elif r>0: rr+=1

	print("\n", sr, "s/r conflicts |", rr, "r/r conflicts")
	

	return table

def count_alphas(word):
	cnt = 0
	for i in word:
		if(ord(i) >= 65 and ord(i) <= 90):
			cnt += 1
	return cnt

if __name__=="__main__":
	table = run()
	
inp = "i*$"
inpstack = Stack()
for i in reversed(inp):
	inpstack.push(i)
consumstack = Stack()
statestack = Stack()
actionstack = Stack()
print("Stack\tConsumed\tInput\tAction")
statestack.push(0)
#actionstack.push("s")
consumstack.push("")
#actionstack.push("")
#print(statestack,"\t",consumstack,"\t",inpstack,"\t",actionstack)
#shiftedto = table[statestack.peek()][inpstack.peek()]
#nextaction = table[statestack.peek()][inpstack.peek()]
#actionstack.push(nextaction)
#act_alpha = list(nextaction)[0]
#print(list(nextaction))
#act = int(list(nextaction)[0][1])
#statestack.push(int(act))
#consumstack.push(inpstack.pop())
#print("IIIIIIIIIIIIII",table[3]["*"])
flag = 1
try:
	while flag:
		nextaction = table[statestack.peek()][inpstack.peek()]
	#print("!!!!!!!!!",inpstack.peek())
	#print("----------",nextaction)
		if(nextaction == "accept"):
			print("Accepted")
			break
		act_alpha = list(nextaction)[0][0]
	#print("----------",act_alpha)
		act = int(list(nextaction)[0][1])
		actionstack.push(nextaction)
		print(statestack.printItems(),"\t\t",consumstack.printItems(),"\t\t",inpstack.printItems(),"\t\t",actionstack.printItems())
		#print(">>>>>>>>>>>>>",act)
		if(act_alpha == "r"):
#			cnt = 0
#			print("NOOOOOOW",statestack.peek())
			#statestack.pop()
			reduction = production_list[act]
			#print(reduction)
			head, body = reduction.split('->')
			l = len(body)
			cnt = count_alphas(body)
#			print("IIIIII",consumstack.printItems(),body)
			for i in range(l):
				consumstack.pop()
			#consumstack.push(head)
			#if(cnt > 1):
			#	for i in range(cnt - 1):
				statestack.pop()
			consumstack.push(head)
			#else:
#				consumstack.push(head)
#			print("!!!!!!!!!!!!!!!",statestack.peek(),consumstack.peek())
			nextstate = int(table[statestack.peek()][consumstack.peek()])
			#print(">>>>>>>>>>>",nextstate)
			statestack.push(nextstate)
		elif(act_alpha == "s"):
			statestack.push(act)
			consumstack.push(inpstack.pop())
except KeyError:
	print("Rejected")
	

	#print(statestack.peek(),"\t",consumstack.peek(),"\t",inpstack.peek(),"\t",actionstack.peek())
	#if(inpstack.peek() == "$" and consumstack.peek() == "E"):
	#	print("Accepted")
	#	print(statestack.printItems(),"\t",consumstack.printItems(),"\t",inpstack.printItems(),"\t",actionstack.printItems())
	#	break
	#elif(inpstack.peek() == "$" and consumstack.peek() != "E"):
	#	print("PPPPPPPPPPPPPPPPPPP",inpstack.peek())
	#	print("Rejected")
	#	break
	#print(">>>>>>",statestack.peek())
	#nextaction = table[statestack.peek()][inpstack.peek()]
	#print("----------",nextaction)
	#act_alpha = list(nextaction)[0][0]
	#print("----------",act_alpha)
	#act = int(list(nextaction)[0][1])
	#print(">>>>>>>>>>>>>",act)



