from ppadb.client import Client as AdbClient
import time

ligue = "ligue1"

def connect():
    adb = AdbClient(host="127.0.0.1", port=5037)
    #print(adb.version())
    #adb connect 192.168.0.11:5555

    devices = adb.devices()
    if len(devices) == 0:
        print("no devices attached")
        quit()

    device = devices[0]
    print("connected")
    device.shell("input keyevent 3")
    return device

def mpg(device):
    device.shell("monkey -p com.monpetitgazon.monpetitgazonapp -c android.intent.category.LAUNCHER 1")
    time.sleep(5)
    device.shell("input tap 1000 2000")
    device.shell("input tap 600 1100")
    time.sleep(0.5)
    device.shell("input tap 430 610")
    time.sleep(0.5)
    device.shell("input tap 220 478")
    #device.shell("input keyevent 3")




device = connect()
mpg(device)


#------------------------------------------------------------

#swipe all phone from bottom left to corner down rigt
#device.shell("input touchscreen swipe 0 0 1000 2000 1000")

#device.shell("input tap 500 500")
#device.shell("input touchscreen swipe 100 500 100 500 1000")

#useful
#66: enter 277: cut 278: copy 279: paste 64: internet 3: home


