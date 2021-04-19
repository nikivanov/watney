import smbus
DEVICE_BUS = 1
DEVICE_ADDR = 0x17

class PowerPlant:
    def __init__(self):
        self.bus = smbus.SMBus(DEVICE_BUS)

    def getBatteryInfo(self):
        aReceiveBuf = []
        aReceiveBuf.append(0x00)   # Placeholder
        for i in range(1,255):
            aReceiveBuf.append(self.bus.read_byte_data(DEVICE_ADDR, i))
        percentage = aReceiveBuf[20] << 8 | aReceiveBuf[19]
        charging = (aReceiveBuf[10] << 8 | aReceiveBuf[9]) > 4000
        return [percentage, charging]



