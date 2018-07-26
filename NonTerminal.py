class NonTerminal:

	def __init__(self, symbol):
		self.symbol=symbol
		self.first=set()
		

	def __str__(self):
		return self.symbol

	def add_first(self, symbols): self.first |= set(symbols) #union operation


