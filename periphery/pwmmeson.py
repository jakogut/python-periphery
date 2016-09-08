import os

from .pwm import PWMError

class MesonPWM(object):
    # Nice job implementing standardized kernel interfaces, Amlogic.
    sysfs_path = "/sys/devices/platform/pwm-ctrl/"

    freq_path = "freq{channel}"
    duty_pct_path = "duty{channel}"
    enable_path = "enable{channel}"

    def __init__(self, channel):
        self._fd = None
        self._channel = None
        
        self._period = None
        self._duty = None
        self._open(channel)

    def __del__(self):
        self.close()

    def __enter__(self):
        pass

    def __exit__(self, t, value, traceback):
        self.close()

    def _open(self, channel):
        if not isinstance(channel, int):
            raise TypeError("Invalid channel type, should be integer.")

        if not os.path.isdir(self.sysfs_path):
            raise AttributeError("PWM sysfs interface does not exist, check that the required modules are loaded.")

        try:
            self._fd = os.open(
                    os.path.join(
                        self.sysfs_path,
                        self.enable_path.format(channel=channel)),
                    os.O_RDWR)
        except OSError as e:
            raise PWMError(e.errno, "Opening PWM: " + e.strerror)

        self._channel = channel
        self._period = 1000000000 / (int(self._read_pin_attr(self.freq_path)) or 1)
        self._duty_cycle = self._period / 100.0 * int(self._read_pin_attr(self.duty_pct_path))
        self._enabled = self._read_pin_attr(self.enable_path)

    def close(self):
        pass

    def _write_pin_attr(self, attr, value):
        path = os.path.join(
                self.sysfs_path, attr.format(channel=self._channel))

        with open(path, 'w') as f_attr:
            f_attr.write(str(value))

    def _read_pin_attr(self, attr):
        path = os.path.join(
                self.sysfs_path, attr.format(channel=self._channel))

        with open(path, 'r') as f_attr:
            return f_attr.read()

    @property
    def fd(self):
        return self._fd

    @property
    def channel(self):
        return self._channel

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        if not isinstance(value, int):
            raise ValueError("Invalid frequency, must be integer.")
        if not 46 <= value <= 1000000: # min freq of 46 hz; max 1 MHz
            raise ValueError("Invalid frequency, must be in range 46 hz to 1 MHz")

        self._period = (1000000000 / value)
        self._write_pin_attr(self.freq_path, value)

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        if not isinstance(value, int):
            raise ValueError("Invalid period, must be integer.")

        self._period = value
        freq = (value * 1000000000)
        self._write_pin_attr(self.freq_path, freq)

    @property
    def duty_cycle(self):
        return self._duty_cycle_pct * self._period

    @duty_cycle.setter
    def duty_cycle(self, value):
        if not isinstance(value, int):
            raise ValueError("Invalid duty cycle, must be integer.")

        self._write_pin_attr(self.duty_pct_path, (100.0 / self._period * value))
        self._duty_cycle = value

    @property
    def duty_cycle_pct(self):
        return self._duty_cycle_pct

    @duty_cycle_pct.setter
    def duty_cycle_pct(self, value):
        if not isinstance(value, int) or not 0 <= value <= 100:
            raise ValueError("Invalid duty cycle pct, must be integer between 0-100")

        self._duty_cycle = value / 100.0 * self._period
        print("Writing duty cycle of: {}".format(value))
        self._write_pin_attr(self.duty_pct_path, value)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if not isinstance(value, int):
            raise ValueError("Invalid value for 'enable' must be integer.")

        self._write_pin_attr(self.enable_path, value)
        self._enabled = value

    def __str__(self):
        return ""
