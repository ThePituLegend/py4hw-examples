from py4hw import *

"""
class Seq(Logic):
	def __init__(self, parent: Logic, name: str, ld: Wire, SnA: Wire, q: Wire):
		super().__init__(parent, name)

		self.load = self.addIn(ld.name, ld)
		self.SnA = self.addIn(SnA.name, SnA)

		self.q = self.addOut(q.name, q)

		one = self.wire("one")
		zero = self.wire("zero")
		incW = self.wire("incW", q.getWidth())
		snaMW = self.wire("SnAMuxWire", ld.getWidth())

		Constant(self, "1", 1, one)

		Add(self, "inc", one, self.q, incW)
		Mux2(self, "SnAMux", self.SnA, incW, self.load, snaMW)

		Reg(self, "Counter", snaMW, one, self.q)
"""

class Seq(Logic):
	def __init__(self, parent: Logic, name: str, ld: Wire, SnA: Wire, q: Wire):
		super().__init__(parent, name)

		self.load = self.addIn(ld.name, ld)
		self.SnA = self.addIn(SnA.name, SnA)

		self.q = self.addOut(q.name, q)

		self.value = -1

	def clock(self):
		if self.SnA.get() == 0:
			self.value +=1 
		else:
			self.value = self.load.get()
	
		self.q.prepare(self.value)

sys = HWSystem()

SnA = sys.wire("SnA")
load = sys.wire("Load", 4)
out = sys.wire("Output", 4)

Scope(sys, "OUT", out)

seq = Seq(sys, "Sequentiator", load, SnA, out)

sim = sys.getSimulator()

for i in range(20):
	if i == 10:
		load.put(5)
		SnA.put(1)
	elif i == 11:
		SnA.put(0)

	sim.clk(1)
