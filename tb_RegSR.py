# -*- coding: utf-8 -*-
from py4hw.base import *
from py4hw.logic import *
from py4hw.storage import Reg
from py4hw.simulation import Simulator
from math import log2
import py4hw.debug

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

sys = HWSystem()

BusB = Wire(sys, "Bus", 32)
qS = Wire(sys, "S Out", 32)
qR = Wire(sys, "R Out", 32)
ld_s = Wire(sys, "Load S", 1)
ld_r = Wire(sys, "Load R", 1)
inic_rs = Wire(sys, "Iniciar R/S", 1)
zero = Wire(sys, "Zero", 1)

Constant(sys, "0", 0, zero)

s = RegSR(sys, "S", BusB, ld_s, qS, inic_rs, zero, 1)
r = RegSR(sys, "R", BusB, ld_r, qR, zero, inic_rs)

Scope(sys, "S Out", qS)
Scope(sys, "R Out", qR)

py4hw.debug.printHierarchy(sys)

print('RESET')
sim = Simulator(sys)

print()
print('CLK')
inic_rs.put(1)
ld_r.put(0)
ld_s.put(0)
sim.clk(1)

print()
print('CLK')
inic_rs.put(0)
ld_r.put(0)
ld_s.put(0)
BusB.put(42)
sim.clk(1)

print()
print('CLK')
ld_r.put(1)
ld_s.put(1)
sim.clk(1)

print()
print('CLK')
sim.clk(1)