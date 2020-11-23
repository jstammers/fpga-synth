"""
oscillator.py: A module to define an Oscillator using myHDL
"""
from myhdl import block, Signal, enum, always_comb, always_seq, intbv, modbv, toVHDL, always, delay, ResetSignal
import math

osc_state = enum('SINE','SQUARE','TRIANGLE', 'SAWTOOTH', 'PWM', 'NOISE')
n_samps = 4096
bit_depth = 12
amp = 2**bit_depth - 1

sine = [intbv(int(amp * 0.5*(math.sin(2 * math.pi * x/n_samps)+1)),
              min=0, max=amp+1) for x in range(n_samps)]
square = [intbv(amp, min=0, max=amp+1) for _ in range(int(n_samps/2))] + [intbv(0, min=0, max=amp+1) for _ in range(int(n_samps/2))]

triangle = [intbv(n_samps//2 + int(2*amp/(n_samps) * math.fabs(x % (n_samps) - (n_samps)/2) - 2*amp/4), min=0, max=amp+1) for x in range(n_samps //4, 5 * n_samps //4)]

sawtooth = [intbv(int(amp * (x/n_samps - math.floor(0.5 + x/n_samps)) + amp//2), min=0, max=amp+1) for x in range(n_samps)]

@block
def Oscillator(z, state, clock: Signal, output_freq: int, reset, sampling_freq:int):

    count = Signal(modbv(0, min=0, max=2**24))
    inc = Signal(intbv(0, min=0, max=2**24))

    @always_seq(clock.posedge, reset=reset)
    def output():
        count.next = count + inc
        addr = count[24:12]
        if state == osc_state.SINE:
            z.next = sine[addr]
        elif state == osc_state.SQUARE:
            z.next = square[addr]
        elif state == osc_state.TRIANGLE:
            z.next = triangle[addr]
        elif state == osc_state.SAWTOOTH:
            z.next = sawtooth[addr]
        elif state == osc_state.PWM:
            pass
        elif state == osc_state.NOISE:
            pass

    @always_comb
    def increment():
        inc_val = intbv(int(n_samps * output_freq * 2**12 / sampling_freq), min=0, max=2**24)
        inc.val = inc_val

    return output


@block
def top():
    sampling_freq = 48000000
    clock = Signal(bool(0))
    reset = ResetSignal(bool(0), active=False, isasync=True)
    dout = Signal(0)
    state = Signal(osc_state.SINE)
    output_freq = Signal(440)

    @always(delay(10))
    def drive_clk():
        clock.next = not clock

    channel = Oscillator(dout, state, clock, output_freq, reset, sampling_freq)

    return channel


toVHDL(top)
