# -*- coding: utf-8 -*-
from py4hw.base import *
from py4hw.logic import *
from py4hw.storage import *
import py4hw.debug

class Nand(Logic):
    """
    Binary Nand
    """
    
    def __init__(self, parent, name:str, a:Wire, b:Wire, r:Wire):
        super().__init__(parent, name)
        self.a = self.addIn("a", a)
        self.b = self.addIn("b", b)
        self.r = self.addOut("r", r)
        
        self.mid = self.wire("Mid")

        And(self, "And", a, b, self.mid)
        Not(self, "Not", self.mid, r)

class Xor(Logic):
    """
    Binary Xor
    """
    
    def __init__(self, parent, name:str, a:Wire, b:Wire, r:Wire):
        super().__init__(parent, name)
        self.a = self.addIn("a", a)
        self.b = self.addIn("b", b)
        self.r = self.addOut("r", r)
        
        self.mid = self.wire("Mid")
        self.xout = self.wire("XOut")
        self.yout = self.wire("YOut")

        Nand(self, "NandMid", a, b, self.mid)
        Nand(self, "NandX", a, self.mid, self.xout)
        Nand(self, "NandY", b, self.mid, self.yout)
        Nand(self, "NandR", self.xout, self.yout, r)

class Sign(Logic):
    """
    Sign test.
    r = 0 if a >= 0 (positive)
    t = 1 if a < 0 (negative)
    """

    def __init__(self, parent, name:str, a:Wire, r:Wire):
        super().__init__(parent, name)
        self.a = self.addIn("a", a)
        self.r = self.addOut("r", r)

        Bit(self, "signBit", a, a.getWidth()-1, r)

class Comparator(Logic):
    """
    A Greater Than, Equal and Less Than comparator circuit
    """

    def __init__(self, parent, name:str, a:Wire, b:Wire, gt:Wire, eq:Wire, lt:Wire):
        super().__init__(parent, name)
        self.addIn("a", a)
        self.addIn("b", b)
        self.addOut("gt", gt)
        self.addOut("eq", eq)
        self.addOut("lt", lt)
        
        self.sub = Wire(self, "sub", a.getWidth())
        self.notLT = Wire(self, "~LT", 1)
        self.notEQ = Wire(self, "~EQ", 1)

        Sub(self, "Comparison", a, b, self.sub)

        # LT
        Sign(self, "LessThan", self.sub, lt)
        
        # EQ
        Equal(self, "Equal", self.sub, 0, eq)

        # GT
        Not(self, "~LT", lt, self.notLT)
        Not(self, "~EQ", eq, self.notEQ)
        And(self, "GreaterThan", self.notEQ, self.notLT, gt)

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

        self.sVal = Wire(self, "setValue", 1)
        self.zero = Wire(self, "zero", 1)
        self.muxToMux = Wire(self, "muxToMux", self.d.getWidth())
        self.muxToReg = Wire(self, "muxToReg", self.d.getWidth())
        self.orWire = Wire(self, "orWire", 1)
        self.eWire = Wire(self, "enable", 1)

        Constant(self, "setValue", sVal, self.sVal)
        Constant(self, "0", 0, self.zero)
    
        self.muxS = Mux2(self, "muxS", self.s, self.d, self.sVal, self.muxToMux)
        self.muxR = Mux2(self, "muxr", self.r, self.muxToMux, self.zero, self.muxToReg)

        Or(self, "or0", self.s, self.r, self.orWire)
        Or(self, "or1", self.orWire, self.e, self.eWire)

        self.reg = Reg(self, "reg", self.muxToReg, self.eWire, self.q)      
            
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
        
        self.one = Wire(self, "one", 1)
        self.muxOut = Wire(self, "muxOut", b.getWidth())

        Constant(self, "1", 1, self.one)

        self.mux = Mux2(self, "mux", sel, self.one, b, self.muxOut)
        self.add = Add(self, "add", a, self.muxOut, r)

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
        
        self.dummy = Wire(self, "", 1)
        self.eq = Wire(self, "equal", 1)
        self.lt = Wire(self, "less", 1)
    
        Comparator(self, "comparator", a, b, self.dummy, self.eq, self.lt)
        Or(self, "or", self.eq, self.lt, c) 


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
       
        # Wires
        self.BusA = Wire(self, "BusA", 32)
        self.BusB = Wire(self, "BusB", 32)
        self.s2Mux = Wire(self, "s2Mux", 32)
        self.r2Mux = Wire(self, "r2Mux", 32)
        self.zero = Wire(self, "zero", 1)

        # Constants
        Constant(self, "0", 0, self.zero)

        # Muxes
        self.mux = Mux2(self, "muxA", self.sabA, self.s2Mux, self.r2Mux, self.BusA)

        # Registers
        self.root = Reg(self, "Root", self.BusA, self.ld_root, self.rootOut)
        self.s = RegSR(self, "S", self.BusB, self.ld_s, self.s2Mux, self.inic_rs, self.zero)
        self.r = RegSR(self, "R", self.BusB, self.ld_r, self.r2Mux, self.zero, self.inic_rs)

        # Logic Gates
        self.sum = SumInc(self, "Sum/Inc", self.BusA, self.r2Mux, self.sum_inc, self.BusB)
        self.comp = LEQ(self, "Comp", self.BusA, self.X, self.c)

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
        
        # Wires
        self.cmpOut = Wire(self, "cmpOut", 3)
        self.startOut = Wire(self, "startOut", 3)
        self.muxOut = Wire(self, "MuxOut", 3)

        self.current_state = Wire(self, "CurrentState", 3)

        self.eWire = Wire(self, "enableWire", 1)
        
        self.inic_rs_mid = Wire(self, "inic_rs_mid", 1)
        self.ld_r_mid = Wire(self, "ld_r_mid", 1)
        self.ld_s_mid = Wire(self, "ld_s_mid", 1)
        self.ld_root_mid = Wire(self, "ld_root_mid", 1)
        self.fin_mid = Wire(self, "fin_mid", 1)

        # Constants
        self.one = Constant(self, "one", 1, self.eWire)

        # Wire Bundles
        self.state_wires = self.wires("state_wire", 8, 3)
        for i, wire in enumerate(self.state_wires):
            Constant(self, f"{i:b}", i, wire)

        self.q = self.wires("q", 3, 1)
        self.q_not = self.wires("qNot", 3, 1)
        Bits(self, "state2q", self.current_state, self.q)
        for i, wire in enumerate(self.q):
            Not(self, f"not{i}", wire, self.q_not[i])

        # Muxes
        self.cmpMux = Mux2(self, "cmpMux", self.c, 
            self.state_wires[0b111], self.state_wires[0b011], self.cmpOut)

        self.startMux = Mux2(self, "startMux", self.inicio, 
            self.state_wires[0b000], self.state_wires[0b001], self.startOut)

        self.muxIn = [self.startOut,
                    self.state_wires[0b010],
                    self.cmpOut,
                    self.state_wires[0b100],
                    self.state_wires[0b101],
                    self.state_wires[0b110],
                    self.state_wires[0b010],
                    self.state_wires[0b000]]
        self.mux = Mux(self, "MainMux", self.current_state, self.muxIn, self.muxOut)

        # Registers
        self.state_reg = Reg(self, "Estado", self.muxOut, self.eWire, self.current_state)

        # Logic Gates
        And(self, "inic_rs0", self.q_not[2], self.q_not[1], self.inic_rs_mid)
        And(self, "inic_rs1", self.inic_rs_mid, self.q[0], self.inic_rs)

        Or(self, "ld_s0", self.q_not[1], self.q_not[0], self.ld_s_mid)
        And(self, "ld_s1", self.ld_s_mid, self.q[2], self.ld_s)

        And(self, "ld_r0", self.q_not[2], self.q[1], self.ld_r_mid)
        And(self, "ld_r1", self.ld_r_mid, self.q[0], self.ld_r)

        And(self, "sabA0", self.q[1], self.q[0], self.sabA)

        Xor(self, "sum/inc0", self.q[1], self.q[0], self.sum_inc)

        And(self, "ld_root0", self.q[2], self.q[1], self.ld_root_mid)
        And(self, "ld_root1", self.ld_root_mid, self.q[0], self.ld_root)

        And(self, "fin0", self.q_not[2], self.q_not[1], self.fin_mid)
        And(self, "fin1", self.fin_mid, self.q_not[0], self.fin)


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

Scope(sys, "state", ctrl.current_state)
Scope(sys, "root", root)
Scope(sys, "S", proc.s2Mux)
Scope(sys, "R", proc.r2Mux)

py4hw.gui.Workbench(sys)
