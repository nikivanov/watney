def pi():
    return FakePi()

OUTPUT = 0


class FakePi:
    def hardware_PWM(self, *args):
        pass

    def set_mode(self, *args):
        pass

    def write(self, *args):
        pass

    def set_PWM_frequency(self, *args):
        pass

    def set_PWM_dutycycle(self, *args):
        pass
