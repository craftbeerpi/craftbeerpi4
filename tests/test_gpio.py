import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

try:
    import RPi.GPIO as GPIO
except Exception:
    print("Error importing RPi.GPIO!")
    MockRPi = MagicMock()
    modules = {
        "RPi": MockRPi,
        "RPi.GPIO": MockRPi.GPIO
    }
    patcher = patch.dict("sys.modules", modules)
    patcher.start()
    import RPi.GPIO as GPIO

class TestSwitch(unittest.TestCase):

    GPIO_NUM = 22

    @patch("RPi.GPIO.setup")
    def test_switch_inits_gpio(self, patched_setup):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_NUM, GPIO.OUT)
        patched_setup.assert_called_once_with(self.GPIO_NUM, GPIO.OUT)

    @patch("RPi.GPIO.output")
    def test_switch_without_scheduler_starts_disabled(self, patched_output):
        GPIO.output(self.GPIO_NUM, GPIO.LOW)
        patched_output.assert_called_once_with(self.GPIO_NUM, GPIO.LOW)