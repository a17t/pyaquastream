import sys
import threading
import time
import PySimpleGUI as sg
from aquastream import AquastreamUltimate
import hid

VENDOR_ID = 0x0c70
PRODUCT_ID = 0xf00b

device = hid.device()
device.open(VENDOR_ID, PRODUCT_ID)
pump = AquastreamUltimate(device)

time.sleep(3)

layout = [[sg.Text('WATER TEMP:'), sg.Text(key="waterTemp", text="0000")],
          [sg.Text('FANRPM:'), sg.Text(key="fanRpmTxt", text="0000")],
          [sg.Slider(key="fanRpmIn", default_value=(int(pump.getConfigFanRpm() / 100)), range=(0,100), orientation='h', size=(100,20))],
          [sg.Text('PUMPRPM:'), sg.Text(key="pumpRpmTxt", text="0000")],
          [sg.Slider(key="pumpRpmIn", default_value=(int(pump.getConfigRpm())), range=(3000,6000), orientation='h', size=(100,20))],
          [sg.Button('Apply'), sg.Button('Close')]]

# Create the window
window = sg.Window("Demo", layout)

class UIUpdateThread(threading.Thread):
    _stop = False
    def run(self):
        while not self._stop:
            try:
                time.sleep(1)
                window['fanRpmTxt'].update(str(pump.getReportedFanRpm()))
                window['pumpRpmTxt'].update(str(pump.getReportedRpm()))
                window['waterTemp'].update(str(pump.getWaterTemp()/100))
            except:
                continue
    def stop(self):
        self._stop = True



uiUpdateThread = UIUpdateThread()
uiUpdateThread.start()
# Create an event loop
while True:
    event, values = window.read()
    print(event, values)
    if event == "Apply":
        pump.setConfigFanRpm(int(values['fanRpmIn']) * 100)
        pump.setConfigRpm(int(values['pumpRpmIn']))
        continue
    # End program if user closes window or
    # presses the Close button
    if event == "Close" or event == sg.WIN_CLOSED:
        uiUpdateThread.stop()
        break

window.close()
sys.exit(0)
