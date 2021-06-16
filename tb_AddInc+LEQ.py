# -*- coding: utf-8 -*-
from py4hw.base import *
from py4hw.logic import *
from py4hw.storage import Reg
import py4hw.debug

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


sys = HWSystem()

a = sys.wire("a", 32)
b = sys.wire("b", 32)
c = sys.wire("c", 32)
d = sys.wire("d", 32)
r1 = sys.wire("r", 32)
r2 = sys.wire("r2", 32)
r3 = sys.wire("r3", 1)
sel1 = sys.wire("sel1")
sel2 = sys.wire("sel2")

SumInc(sys, "sum", a, b, sel1, r1)
SumInc(sys, "inc", r1, c, sel2, r2)
LEQ(sys, "comparator", r2, d, r3)

Constant(sys, "a", 10, a)
Constant(sys, "b", 20, b)
Constant(sys, "c", 5, c)
Constant(sys, "d", 31, d)
Constant(sys, "sel1", 1, sel1)
Constant(sys, "sel2", 0, sel2)

Scope(sys, "r2", r2)
Scope(sys, "r3", r3)

py4hw.gui.Workbench(sys)
