# -*- coding: utf-8 -*-
from py4hw.base import *
from py4hw.logic import *
from py4hw.storage import *
import py4hw.debug
import nbwavedrom
class RegSR(Logic):
    """
    This is a D flip flop + Set/Reset feature
    """

    def __init__(self, parent, name:str, d:Wire, e:Wire, q:Wire, s:Wire, r:Wire, sVal:int = 0):
        super().__init__(parent, name)
        self.d = self.addIn("d", d)
        self.e = self.addIn("e", e)
        self.q = self.addOut("q", q)
        self.s = self.addIn("s", s)
        self.r = self.addIn("r", r)
        self.value = 0
        
        if (sVal > 0 and d.getWidth() < int(log2(sVal))+1):
            raise Exception('Invalid set value')

        sValWire = Wire(self, "setValue", 1)
        zero = Wire(self, "zero", 1)
        muxToMux = Wire(self, "muxToMux", self.d.getWidth())
        muxToReg = Wire(self, "muxToReg", self.d.getWidth())
        orWire = Wire(self, "orWire", 1)
        eWire = Wire(self, "enable", 1)

        Constant(self, "setValue", sVal, sValWire)
        Constant(self, "0", 0, zero)
    
        self.muxS = Mux2(self, "muxS", s, d, sValWire, muxToMux)
        self.muxR = Mux2(self, "muxr", r, muxToMux, zero, muxToReg)

        Or(self, "or0", s, r, orWire)
        Or(self, "or1", orWire, e, eWire)

        self.reg = Reg(self, "reg", muxToReg, eWire, q)     
            
class SumInc(Logic):
    """
    Configurable Incrementer/Adder

    a+b if sel = 1
    a+1 if sel = 0
    """

    def __init__(self, parent, name: str, a: Wire, b: Wire, sel: Wire, r: Wire):
        super().__init__(parent, name)
        self.a = self.addIn("a", a)
        self.b = self.addIn("b", b)
        self.sel = self.addIn("sum/inc", sel)
        self.r = self.addOut("r", r)
        
        one = Wire(self, "one", 1)
        muxOut = Wire(self, "muxOut", b.getWidth())

        Constant(self, "1", 1, one)

        self.mux = Mux2(self, "mux", sel, one, b, muxOut)
        self.add = Add(self, "add", a, muxOut, r)

class LEQ(Logic):
    """
    Less or Equal comparator.

    c = 1 if a <= b
    c = 0 otherwise
    """

    def __init__(self, parent, name: str, a: Wire, b: Wire, c: Wire):
        super().__init__(parent, name)
        self.a = self.addIn("a", a)
        self.b = self.addIn("b", b)
        self.c = self.addOut("c", c)
        
        dummy = Wire(self, "", 1)
        eq = Wire(self, "equal", 1)
        lt = Wire(self, "less", 1)
    
        Comparator(self, "comparator", a, b, dummy, eq, lt)
        Or(self, "or", eq, lt, c)

class ProcUnit(Logic):
    """
    Processing Unit for sqrt().
    """
    def __init__(self, parent, name:str, inic_rs:Wire, ld_s:Wire, ld_r:Wire, sabA:Wire, sum_inc:Wire,
        ld_root:Wire, X:Wire, rootOut:Wire, c:Wire):
        super().__init__(parent, name)

        # Init
        self.X = self.addIn(X.name, X)
        self.inic_rs = self.addIn(inic_rs.name, inic_rs)
        self.ld_s = self.addIn(ld_s.name, ld_s)
        self.ld_r = self.addIn(ld_r.name, ld_r)
        self.sabA = self.addIn(sabA.name, sabA)
        self.sum_inc = self.addIn(sum_inc.name, sum_inc)
        self.ld_root = self.addIn(ld_root.name, ld_root)

        self.rootOut = self.addOut(rootOut.name, rootOut)
        self.c = self.addOut(c.name, c)
       
        # Wires (The ones we want to draw will remain as attributes)
        self.s2Mux = Wire(self, "s2Mux", 32)
        self.r2Mux = Wire(self, "r2Mux", 32)
        BusA = Wire(self, "BusA", 32)
        BusB = Wire(self, "BusB", 32)
        zero = Wire(self, "zero", 1)

        # Constants
        Constant(self, "0", 0, zero)

        # Muxes
        self.mux = Mux2(self, "muxA", sabA, self.s2Mux, self.r2Mux, BusA)

        # Registers
        self.root = Reg(self, "Root", BusA, ld_root, rootOut)
        self.s = RegSR(self, "S", BusB, ld_s, self.s2Mux, inic_rs, zero)
        self.r = RegSR(self, "R", BusB, ld_r, self.r2Mux, zero, inic_rs)

        # Logic Gates
        self.sum = SumInc(self, "Sum/Inc", BusA, self.r2Mux, sum_inc, BusB)
        self.comp = LEQ(self, "Comp", BusA, X, c)

class CtrlUnit(Logic):
    """
    Control Unit for sqrt().
    """
    def __init__(self, parent, name:str, c:Wire, inicio:Wire, 
        inic_rs:Wire, ld_s:Wire, ld_r:Wire, sabA:Wire, sum_inc:Wire, ld_root:Wire, fin:Wire):
        super().__init__(parent, name)

        # Init
        self.c = self.addIn(c.name, c)
        self.inicio = self.addIn(inicio.name, inicio)

        self.inic_rs = self.addOut(inic_rs.name, inic_rs)
        self.ld_s = self.addOut(ld_s.name, ld_s)
        self.ld_r = self.addOut(ld_r.name, ld_r)
        self.sabA = self.addOut(sabA.name, sabA)
        self.sum_inc = self.addOut(sum_inc.name, sum_inc)
        self.ld_root = self.addOut(ld_root.name, ld_root)
        self.fin = self.addOut(fin.name, fin)
        
        # Wires (The ones we want to draw will remain as attributes)
        self.current_state = Wire(self, "CurrentState", 3)
        
        cmpOut = Wire(self, "cmpOut", 3)
        startOut = Wire(self, "startOut", 3)
        muxOut = Wire(self, "MuxOut", 3)

        eWire = Wire(self, "enableWire", 1)
        
        inic_rs_mid = Wire(self, "inic_rs_mid", 1)
        ld_r_mid = Wire(self, "ld_r_mid", 1)
        ld_s_mid = Wire(self, "ld_s_mid", 1)
        ld_root_mid = Wire(self, "ld_root_mid", 1)
        fin_mid = Wire(self, "fin_mid", 1)

        # Constants
        self.one = Constant(self, "one", 1, eWire)

        # Wire Bundles
        state_wires = self.wires("state_wire", 8, 3)
        for i, wire in enumerate(state_wires):
            Constant(self, f"{i:b}", i, wire)

        q = self.wires("q", 3, 1)
        q_not = self.wires("qNot", 3, 1)
        Bits(self, "state2q", self.current_state, q)
        for i, wire in enumerate(q):
            Not(self, f"not{i}", wire, q_not[i])

        # Muxes
        cmpMux = Mux2(self, "cmpMux", c, 
            state_wires[0b111], state_wires[0b011], cmpOut)

        startMux = Mux2(self, "startMux", inicio, 
            state_wires[0b000], state_wires[0b001], startOut)

        muxIn = [startOut,
                state_wires[0b010],
                cmpOut,
                state_wires[0b100],
                state_wires[0b101],
                state_wires[0b110],
                state_wires[0b010],
                state_wires[0b000]]
        mux = Mux(self, "MainMux", self.current_state, muxIn, muxOut)

        # Registers
        state_reg = Reg(self, "Estado", muxOut, eWire, self.current_state)

        # Logic Gates
        And(self, "inic_rs0", q_not[2], q_not[1], inic_rs_mid)
        And(self, "inic_rs1", inic_rs_mid, q[0], inic_rs)

        Or(self, "ld_s0", q_not[1], q_not[0], ld_s_mid)
        And(self, "ld_s1", ld_s_mid, q[2], ld_s)

        And(self, "ld_r0", q_not[2], q[1], ld_r_mid)
        And(self, "ld_r1", ld_r_mid, q[0], ld_r)

        And(self, "sabA0", q[1], q[0], sabA)

        Xor(self, "sum/inc0", q[1], q[0], sum_inc)

        And(self, "ld_root0", q[2], q[1], ld_root_mid)
        And(self, "ld_root1", ld_root_mid, q[0], ld_root)

        And(self, "fin0", q_not[2], q_not[1], fin_mid)
        And(self, "fin1", fin_mid, q_not[0], fin)

sys = HWSystem()

inic_rs = sys.wire("inic_rs")
ld_s = sys.wire("ld_s")
ld_r = sys.wire("ld_r") 
sabA = sys.wire("sabA")
sum_inc = sys.wire("sum_inc")
ld_root = sys.wire("ld_root")
X = sys.wire("X", 32)
root = sys.wire("root", 32)
c = sys.wire("c")
inicio = sys.wire("inicio")
fin = sys.wire("fin")

Constant(sys, "X", 25, X)
Constant(sys, "Inicio", 1, inicio)

proc = ProcUnit(sys, "UP", inic_rs, ld_s, ld_r, sabA, sum_inc, ld_root, X, root, c)
ctrl = CtrlUnit(sys, "UC", c, inicio, inic_rs, ld_s, ld_r, sabA, sum_inc, ld_root, fin)

#py4hw.debug.printHierarchyWithValues(sys)

waveform = {'signal': [
  {'name': 'CK', 'wave': 'P'},
  {'name': 'state', 'wave': 'x', 'data': []},
  {'name': 'root', 'wave': 'x', 'data': []},
  {'name': 'S', 'wave': 'x', 'data': []},
  {'name': 'R', 'wave': 'x', 'data': []},
],
 "head":{
   "text": 'Diagrama',
   "tock": 0,
 }
}

sim = sys.getSimulator()

val = [ctrl.current_state.get, root.get, proc.s2Mux.get, proc.r2Mux.get]

while root.get() == 0:
  sim.clk(1)

  waveform["signal"][0]["wave"] += "."
  for x, wave in enumerate(waveform["signal"][1:]):
    if len(wave["data"]) > 0 and wave["data"][-1] == val[x]():
      wave["wave"] += "."
    else:
      wave["wave"] += "2"
      wave["data"].append(val[x]())

waveform["signal"][0]["wave"] += "."
for wave in waveform["signal"][1:]:
  wave["wave"] += "x"

nbwavedrom.draw(waveform) # Only works in Notebook form