from __future__ import division, print_function

from myhdl import *

from rhea.system import Barebone
from . import SPIBus


def spi_controller_model(clock, reset, ibus, spibus):
    """

      ibus   : internal bus
      spibus : SPI interface (SPIBus)
    """
    assert isinstance(ibus, Barebone)
    assert isinstance(spibus, SPIBus)

    @instance
    def decode_ibus():
        while True:
            yield clock.posedge
            ibus.ack.next = False  # default value

            if ibus.write:
                yield spibus.writeread(ibus.data_in)
                ibus.ack.next = True
            elif ibus.read:
                yield spibus.writeread(0x55)
                ibus.data_out.next = spibus.ival
                ibus.ack.next = True

    return decode_ibus


class SPISlave(object):
    def __init__(self):
        self.reg = intbv(0)[8:]

    def process(self, spibus):
        mosi = spibus.mosi
        miso = spibus.miso
        sck = spibus.sck
        csn = spibus.csn

        @instance
        def gproc():
            while True:
                yield csn.negedge
                bcnt = 8
                while not csn:
                    if bcnt > 0:
                        miso.next = self.reg[bcnt-1]
                        yield sck.posedge
                        bcnt -= bcnt
                        self.reg[bcnt] = mosi
                    else:
                        yield delay(10)

        return gproc