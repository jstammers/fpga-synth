import ok
import myhdl
class FPGA:
    def __init__(self, serial=None):
        self.dev = ok.FrontPanel()

        self.dev.OpenBySerial()
        pll = ok.okCPLL22150()
        self.dev.GetEepromPLL22150Configuration(pll)
        self.dev.SetPLL22150Configuration(pll)
        self.sampling_freq = pll.GetOutputFrequency(0)

    def write(self):
        self.dev.ConfigureFPGA()
