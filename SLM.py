'''
SLM
    Display an image

'''



from PIL import Image
import numpy as np
from ctypes import *
import copy
import json
import time
from threading import Thread

import tango
from tango import AttrQuality, AttrWriteType, DevState, DispLevel, AttReqType, Database
from tango.server import Device, attribute, command
from tango.server import class_property, device_property

db = Database()
try:
   prop = db.get_property('ORBendPoint', 'Pool/' + instance_name)
   orb_end_point = prop['Pool/' + instance_name][0]
   os.environ["ORBendPoint"] = orb_end_point
except:
   pass

my_thread = None
pitch = 1

#LCOS pixel size
x = 1280
y = 1024

#LCOS-SML monitor number setting
monitorNo = 2
windowNo = 0
xShift = 0
yShift = 0

#pixel number
array_size = x * y

# make the 8bit unsigned integer array type
FARRAY = c_uint8 * array_size

# make the 8bit unsigned integer array instance
farray = FARRAY(0)
farray2 = FARRAY(0)
farray3 = FARRAY(0)

#Display cylindricalLens pattern array with using dll
forcus = 1000
wavelength = 1064
modeSelect = 0


def makeCylindricalLensArray(forcus, wavelength, pitch, modeSelect, x, y, array):
    Lcoslib = cdll.LoadLibrary("C:\\Users\\User\\Desktop\\Tango_Device_Test\\Tango_SLM\\Image_Control.dll")
    Lcoslib = windll.LoadLibrary("C:\\Users\\User\\Desktop\\Tango_Device_Test\\Tango_SLM\\Image_Control.dll")
    CylindricalLens = Lcoslib.CylindricalLens
    CylindricalLens.argtyes = [c_int, c_int, c_int, c_int, c_int, c_int, c_void_p, c_void_p]
    CylindricalLens.restype = c_int
    if(pitch != 0 and pitch != 1):
        print("Error: CylindricalLensFunction. invalid argument (pitch).")
        return -1
    CylindricalLens(forcus, wavelength, pitch, modeSelect, x, y, byref(c_int(x*y)), byref(array))
    return 0

'''
the function for showing on LCOS display
int monitorNo: 
int windowNo:
int x: Pixel number of x-dimension
int xShift: shift pixels of x-dimension
int y: Pixel number of y-dimension
int yShift: shift pixels of y-dimension
8bit unsigned int array array: output array
'''
def showOn2ndDisplay(monitorNo, windowNo, x, xShift, y, yShift, array):
    Lcoslib = windll.LoadLibrary("C:\\Users\\User\\Desktop\\Tango_Device_Test\\Tango_SLM\\Image_Control.dll")
    
    #Select LCOS window
    Window_Settings = Lcoslib.Window_Settings
    Window_Settings.argtypes = [c_int, c_int, c_int, c_int]
    Window_Settings.restype = c_int
    Window_Settings(monitorNo, windowNo, xShift, yShift)
    
    #Show pattern
    Window_Array_to_Display = Lcoslib.Window_Array_to_Display
    Window_Array_to_Display.argtypes = [c_void_p, c_int, c_int, c_int, c_int]
    Window_Array_to_Display.restype = c_int
    Window_Array_to_Display(array, x, y, windowNo, x*y)
    
    #wait until enter key input
    time.sleep(8)
    
    #close the window
    Window_Term = Lcoslib.Window_Term
    Window_Term.argtyes = [c_int]
    Window_Term.restype = c_int
    Window_Term(windowNo)
    
    return 0

def showOn2ndDisplay_all_time(monitorNo, windowNo, x, xShift, y, yShift, array):
    Lcoslib = windll.LoadLibrary("C:\\Users\\User\\Desktop\\Tango_Device_Test\\Tango_SLM\\Image_Control.dll")
    
    #Select LCOS window
    Window_Settings = Lcoslib.Window_Settings
    Window_Settings.argtypes = [c_int, c_int, c_int, c_int]
    Window_Settings.restype = c_int
    Window_Settings(monitorNo, windowNo, xShift, yShift)
    
    #Show pattern
    Window_Array_to_Display = Lcoslib.Window_Array_to_Display
    Window_Array_to_Display.argtypes = [c_void_p, c_int, c_int, c_int, c_int]
    Window_Array_to_Display.restype = c_int
    Window_Array_to_Display(array, x, y, windowNo, x*y)
    
    # #wait until enter key input
    # time.sleep(8)
    
    # #close the window
    # Window_Term = Lcoslib.Window_Term
    # Window_Term.argtyes = [c_int]
    # Window_Term.restype = c_int
    # Window_Term(windowNo)
    
    return 0

def makeLaguerreGaussModeArray(p, m, pitch, beamSize, x, y, array):
    Lcoslib = cdll.LoadLibrary("Image_Control.dll")
    Lcoslib = windll.LoadLibrary("Image_Control.dll")
    LaguerreGaussMode = Lcoslib.LaguerreGaussMode
    LaguerreGaussMode.argtyes = [c_int, c_int, c_int, c_double, c_int, c_int, c_void_p, c_void_p]
    LaguerreGaussMode.restype = c_int
    if(pitch != 0 and pitch != 1):
        print("Error: LaguerreGaussModeFunction. invalid argument (pitch).")
        return -1
    LaguerreGaussMode(p, m, pitch, c_double(beamSize), x, y, byref(c_int(x*y)), byref(array))
    return 0

class SLM(Device):

    host = device_property(dtype=str, default_value="localhost")
    port = class_property(dtype=int, default_value=10000)
    Lcoslib = windll.LoadLibrary("C:\\Users\\User\\Desktop\\Tango_Device_Test\\Tango_SLM\\Image_Control.dll")
    thread = None

    def init_device(self):
        super().init_device()
        self.info_stream(f"Connection details: {self.host}:{self.port}")
        self.set_state(DevState.ON)
        self.info_stream("\r Try to start the Thorlabs Driver \r")

    def __del__(self):
        try:
            self.thread.join()
        except:
            print("No theard ")
        return 

 


    @command(dtype_out=str)
    def LaguerreGauss(self):
        global my_thread
          #pixelpitch(0: 20um 1: 1.25um)
        p = 5
        m = 5
        pitch = 1
        beamSize = 20.0
        makeLaguerreGaussModeArray(p, m, pitch, beamSize, x, y, farray)
        # showOn2ndDisplay(monitorNo, windowNo, x, xShift, y, yShift, farray)
        my_thread = Thread(target = showOn2ndDisplay_all_time, args = (monitorNo, windowNo, x, xShift, y, yShift, farray, ))
        my_thread.start()
        return "Test"
    
    @command(dtype_out=str)
    def CylindricalLens(self):
        global my_thread
          #pixelpitch(0: 20um 1: 1.25um)

        makeCylindricalLensArray(forcus, wavelength, pitch, modeSelect, x, y, farray)
        # showOn2ndDisplay(monitorNo, windowNo, x, xShift, y, yShift, farray)
        my_thread = Thread(target = showOn2ndDisplay_all_time, args = (monitorNo, windowNo, x, xShift, y, yShift, farray, ))
        my_thread.start()
        return "Test"
    
    @command(dtype_out=str)
    def kill_theard(self):
        global my_thread
        try:
            my_thread.join()
            #close the window
            Window_Term = self.Lcoslib.Window_Term
            Window_Term.argtyes = [c_int]
            Window_Term.restype = c_int
            Window_Term(windowNo)     
            msg = "theard Stopped"
        except:
            msg = "No theard"

        return msg
if __name__ == "__main__":
    SLM.run_server()
