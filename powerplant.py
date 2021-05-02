import smbus
DEVICE_BUS = 1
DEVICE_ADDR = 0x17

class PowerPlant:
    def __init__(self, config):
        self.bus = smbus.SMBus(DEVICE_BUS)
        powerplantConfig = config["POWERPLANT"]
        cutoffVoltage = int(powerplantConfig['CutoffVoltage'])
        self.bus.write_byte_data(DEVICE_ADDR, 17, cutoffVoltage & 0xFF)
        self.bus.write_byte_data(DEVICE_ADDR, 18, (cutoffVoltage >> 8)& 0xFF)
        print('Set powerplant cutoff voltage to {} mv'.format(cutoffVoltage))
        

    def getBatteryInfo(self):
        aReceiveBuf = []
        aReceiveBuf.append(0x00)   # Placeholder
        for i in range(1,255):
            aReceiveBuf.append(self.bus.read_byte_data(DEVICE_ADDR, i))
        percentage = aReceiveBuf[20] << 8 | aReceiveBuf[19]
        charging = (aReceiveBuf[10] << 8 | aReceiveBuf[9]) > 4000
        return [percentage, charging]



