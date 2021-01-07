import time

from crcmod import crcmod
import threading

fullSpeed = [0x03, 0x00, 0x02, 0x11, 0x06, 0x01, 0x17, 0x70,
             0x15, 0x7c, 0x04, 0xa1, 0x00, 0x06, 0x00, 0xa9,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x1e, 0xc7, 0xff, 0xff, 0xff, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x01, 0x0e, 0x10, 0x0b, 0xb8,
             0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
             0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
             0x01, 0x02, 0x03, 0xe8, 0x27, 0x10, 0x04, 0xb0,
             0x00, 0x27, 0x10, 0x00, 0x00, 0x0a, 0xf0, 0x0a,
             0x28, 0x09, 0x60, 0x08, 0xfc, 0x09, 0x42, 0x09,
             0x7e, 0x09, 0xc4, 0x0a, 0x0a, 0x0a, 0x46, 0x0a,
             0x8c, 0x0a, 0xd2, 0x0b, 0x0e, 0x0b, 0x54, 0x0b,
             0x9a, 0x0b, 0xd6, 0x0c, 0x1c, 0x0c, 0x62, 0x0c,
             0x9d, 0x0c, 0xe4, 0x00, 0x00, 0x02, 0x9a, 0x05,
             0x35, 0x07, 0xd0, 0x0a, 0x6a, 0x0d, 0x05, 0x0f,
             0xa0, 0x12, 0x3a, 0x14, 0xd5, 0x17, 0x70, 0x1a,
             0x0a, 0x1c, 0xa5, 0x1f, 0x40, 0x21, 0xda, 0x24,
             0x75, 0x27, 0x10, 0x0d, 0xac, 0x03, 0xe8, 0x03,
             0xe8, 0x00, 0x00, 0x00, 0x01, 0x00, 0x0a, 0x00,
             0x01, 0x00, 0x00, 0x0a, 0xf0, 0x0a, 0x28, 0x08,
             0xfc, 0x08, 0x98, 0x08, 0xde, 0x09, 0x1a, 0x09,
             0x60, 0x09, 0xa6, 0x09, 0xe2, 0x0a, 0x28, 0x0a,
             0x6e, 0x0a, 0xaa, 0x0a, 0xf0, 0x0b, 0x36, 0x0b,
             0x72, 0x0b, 0xb8, 0x0b, 0xfe, 0x0c, 0x3a, 0x0c,
             0x80, 0x00, 0x00, 0x02, 0x9a, 0x05, 0x35, 0x07,
             0xd0, 0x0a, 0x6a, 0x0d, 0x05, 0x0f, 0xa0, 0x12,
             0x3a, 0x14, 0xd5, 0x17, 0x70, 0x1a, 0x0a, 0x1c,
             0xa5, 0x1f, 0x40, 0x21, 0xda, 0x24, 0x75, 0x27,
             0x10, 0x0d, 0xac, 0x03, 0xe8, 0x03, 0xe8, 0x00,
             0x00, 0x00, 0x01, 0x00, 0x0a, 0x00, 0x01, 0x05,
             0x00, 0x10, 0x01, 0x90, 0x01, 0x90, 0x13, 0x88,
             0x13, 0x88, 0x21, 0x34, 0x21, 0x34, 0x89, 0x60]

CONFIG_REPORT_ID = 0
SENSOR_REPORT_ID = 1
##READ
CONFIG_FAN_VOLT_OFFSET = 3
CONFIG_READ_FAN_RPM_OFFSET = 7
CONFIG_FAN_RPM_OFFSET = 11
CONFIG_READ_RPM_OFFSET = 17
CONFIG_RPM_OFFSET = 25

CONFIG_RPM_LENGTH = 2
CONFIG_FAN_RPM_LEN = 2
CONFIG_FAN_VOLT_LEN = 2

SENSOR_WATER_TEMP_OFFSET = 53

SENSOR_WATER_TEMP_LEN = 2
##SET

PUMP_RPM_LEN = 2
FAN_RPM_LEN = 2

PUMP_RPM_OFFSET = 7
FAN_RPM_OFFSET = 74


class AquastreamUltimate:
    _device = None
    _readThread = None
    _configPumpRpm = 0
    _configFanRpm = 0
    _readFanRpm = 0
    _readPumpRpm = 0
    _readFanVolts = 0
    _waterTemp = 0
    _lastConfigReport = None
    _lastSensorsReport = None

    def __init__(self, device):
        self._device = device
        self._readThread = threading.Thread(target=self.readReports, daemon=True)
        self._readThread.start()

    def readReports(self):
        while True:
            data = self._device.read(128, 30)
            if (len(data) > 0 and data[0] == CONFIG_REPORT_ID):
                self._lastConfigReport = data
                self._configPumpRpm = int.from_bytes(data[CONFIG_RPM_OFFSET:CONFIG_RPM_OFFSET + CONFIG_RPM_LENGTH],
                                                     byteorder="big",
                                                     signed=False)
                self._readPumpRpm = int.from_bytes(
                    data[CONFIG_READ_RPM_OFFSET:CONFIG_READ_RPM_OFFSET + CONFIG_RPM_LENGTH], byteorder="big",
                    signed=False)
                self._readFanVolts = int.from_bytes(data[CONFIG_FAN_VOLT_OFFSET:CONFIG_FAN_VOLT_OFFSET + CONFIG_FAN_VOLT_LEN],
                              byteorder="big",
                              signed=False)
                self._configFanRpm = int.from_bytes(data[CONFIG_FAN_RPM_OFFSET:CONFIG_FAN_RPM_OFFSET + CONFIG_FAN_RPM_LEN],
                              byteorder="big",
                              signed=False)
                self._readFanRpm = int.from_bytes(data[CONFIG_READ_FAN_RPM_OFFSET:CONFIG_READ_FAN_RPM_OFFSET + CONFIG_FAN_RPM_LEN],
                              byteorder="big",
                              signed=False)
            if (len(data) > 0 and data[0] == SENSOR_REPORT_ID):
                self._lastSensorsReport = data
                self._waterTemp = int.from_bytes(data[SENSOR_WATER_TEMP_OFFSET:SENSOR_WATER_TEMP_OFFSET + SENSOR_WATER_TEMP_LEN],
                               byteorder="big",
                               signed=False)


    def getConfigReport(self):
        return self._lastConfigReport

    def getSensorReport(self):
        return self._lastSensorsReport

    def getConfigRpm(self):
        return self._configPumpRpm

    def getReportedRpm(self):
        return self._readPumpRpm

    def getFanVolt(self):
        return self._readFanVolts

    def getConfigFanRpm(self):
        return self._configFanRpm

    def getReportedFanRpm(self):
        return self._readFanRpm

    def getWaterTemp(self):
        return self._waterTemp

    def setConfigRpm(self, speed):
        minRpm = 3000;
        maxRpm = 6000;

        if speed >= minRpm and speed <= maxRpm:
            self._configPumpRpm = speed
            self.sendConfig()

    def setConfigFanRpm(self, speed):
        minRpm = 0
        maxRpm = 10000
        if speed >= minRpm and speed <= maxRpm:
            self._configFanRpm = speed
            self.sendConfig()

    def sendConfig(self):
        crc = crcmod.predefined.mkPredefinedCrcFun("crc-16-usb")
        setting = bytearray(fullSpeed[0:PUMP_RPM_OFFSET - 1])
        setting.extend(bytearray(self._configPumpRpm.to_bytes(2, byteorder="big", signed=False)))
        setting.extend(fullSpeed[PUMP_RPM_OFFSET - 1 + PUMP_RPM_LEN:FAN_RPM_OFFSET - 1])
        setting.extend(bytearray(self._configFanRpm.to_bytes(2, byteorder="big", signed=False)))
        setting.extend(fullSpeed[FAN_RPM_OFFSET - 1 + FAN_RPM_LEN:262])
        setting.extend(int(crc(bytearray(setting[1:]))).to_bytes(2, byteorder="big", signed=False))
        self._device.send_feature_report(setting)
        ##Wait one second not to "kill the pump controller"
        time.sleep(1)

    def getDevice(self):
        return self._device
