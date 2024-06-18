# SLM - Tango Device Server 
This repository contains the driver to control a SLM with the Tango Control. After you clone this repository by using the follow command:

```
git clone https://github.com/Golp-Voxel/Tango_SLM.git
```

It is need to create the `tango-env` using the following command:

```
python -m venv tango-env
```

After activating it you can install all the models to run this tool by using the command:

```
pip install -r Requirements.txt
```

To finalize the installation, it is need to copy the `SLM.bat` and `SLM_P.bat` templates and change the paths to the installation folder. And the call command to the execute the `tango-env\Scripts\activate` script.





## Comands that are aviable 
After installing the Tango Device server, you can display a LaguerreGauss or a CylindricalLens or even a CustomImage by calling the corresponding function:

```python 
LaguerreGauss()
```

```python 
CylindricalLens()
```

```python 
CustomImage(User_Image)
```
In the case of the CustomImage it is recuired to send a 1D array (size 1280x1024) that is going to be converted in to a 2D array 1280 by 1024 (`User_Image`).

So you can use the function `User_Image.reshape(1280*1024)` to convert your 2D Image array to 1D. The convertion made by the function is the following:
```
User_Image = np.array(User_Image).reshape(x, y)
```

To stop the display of the SLM you need to call the following function:

```
StopDisplay()
```

## Exemple of Tango Client code to send a LaguerreGauss to be displayed
```python
import tango
import time
SLM = tango.DeviceProxy(<SLM_Tango_location_on_the_database>)
print(SLM.state())
# Change this time out if need
SLM.set_timeout_millis(9000) 

# This function returns a list with all the command aviable on the device server
SLM.get_command_list()
#['CylindricalLens', 'CustomImage', 'LaguerreGauss', 'kill_theard']

SLM.LaguerreGauss()
time.sleep(10)
SLM.StopDisplay()
```
