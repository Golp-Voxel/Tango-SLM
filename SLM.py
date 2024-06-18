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

Path_to_DLL = "C:\\Users\\Voxel\\Desktop\\Tango_Device\\Tango_SLM\\"


def makeCylindricalLensArray(forcus, wavelength, pitch, modeSelect, x, y, array):
    Lcoslib = cdll.LoadLibrary(Path_to_DLL+"Image_Control.dll")
    Lcoslib = windll.LoadLibrary(Path_to_DLL+"Image_Control.dll")
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
    Lcoslib = windll.LoadLibrary(Path_to_DLL+"Image_Control.dll")
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


'''
the function for making FresnelLens pattern array
String filepath: image file path.
int x: Pixel number of x-dimension
int y: Pixel number of y-dimension
8bit unsigned int array outArray: output array
'''

def makeBmpArray(image, x, y, outArray):
    imageWidth,imageHeight = np.shape(image)
    print(len(np.array(outArray)))
    
    print("Imagesize = {} x {}".format(imageWidth, imageHeight))
    
    for i in range(imageWidth):
        for j in range(imageHeight):
            outArray[i+imageWidth*j] = image[i,j]
    
    # print(len(np.array(outArray)))
    
    
    Lcoslib = windll.LoadLibrary(Path_to_DLL+"Image_Control.dll")
    
    # #Create CGH
    # inArray = copy.deepcopy(outArray)
    # Create_CGH_OC = Lcoslib.Create_CGH_OC
    # Create_CGH_OC.argtyes = [c_void_p, c_int, c_int, c_int, c_int, c_void_p, c_void_p]
    # Create_CGH_OC.restype = c_int
    
    # repNo = 100
    # progressBar = 1
    # Create_CGH_OC(byref(inArray), repNo, progressBar, imageWidth, imageHeight, byref(c_int(imageHeight*imageWidth)), byref(outArray))
    
    #Tilling the image
    inArray = copy.deepcopy(outArray)
    # print(np.array(inArray))
    print(len(np.array(inArray)))
    Image_Tiling = Lcoslib.Image_Tiling
    Image_Tiling.argtyes = [c_void_p, c_int, c_int, c_int, c_int, c_int, c_void_p, c_void_p]
    Image_Tiling.restype = c_int
    
    Image_Tiling(byref(inArray), imageWidth, imageHeight, imageHeight*imageWidth, x, y, byref(c_int(x*y)), byref(outArray))
    
    return 0



def showOn2ndDisplay_all_time(monitorNo, windowNo, x, xShift, y, yShift, array):
    Lcoslib = windll.LoadLibrary(Path_to_DLL+"Image_Control.dll")
    
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
    Lcoslib = windll.LoadLibrary(Path_to_DLL+"Image_Control.dll")
    
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
    Lcoslib = windll.LoadLibrary(Path_to_DLL+"Image_Control.dll")
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
    
    # TODO: tango only accepts 1D arrays, so we can send JSON or a 1D array with specific formatting.
    @command(dtype_in=(int,),dtype_out=str)
    def CustomImage(self,User_Image):
        global my_thread
          #pixelpitch(0: 20um 1: 1.25um)
        p = 5
        m = 5
        pitch = 1
        beamSize = 20.0
        #Display CGH pattern from image file with using dll
        # N = (1280,1024)
        # image = np.random.randint(0, 255, size=N)
        # print(image)
        User_Image = np.array(User_Image).reshape(x, y)
        makeBmpArray(User_Image, x, y, farray)
        showOn2ndDisplay(monitorNo, windowNo, x, xShift, y, yShift, farray)
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
    def StopDisplay(self):
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
