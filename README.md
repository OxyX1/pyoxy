# pyoxy
a python module made by oxyus

an example of use:

import pyoxy

def triggered_function():
    pyoxy.tools.console.write('this function was triggered by a sensor function!')

pyoxy.tools.console.write('hello, world!') #this is how you write hello, world!
pyoxy.tools.console.read('input: ') # how to use inputs
pyoxy.tools.system.edit.move('path/to/your/file', 'path/to/your/destination') #how to move files
pyoxy.tools.system.control.mouse(x=100, y=100) # how to move your cursor
pyoxy.tools.system.control.keyboard('hello, world!') # this will type on your keyboard automatically
pyoxy.tools.system.Detection.imgesp('path/to/your/img', confidence=8.0, action=triggered_function())
pyoxy.tools.system.Detection.coloresp(X=0, Y=0, R=10, G=5, B=150, tol=10, action=triggered_function())
pyoxy.tools.override.screen.gdi32_force_pixel_color_change(X=0, Y=0, COLOR=0x0000FF) #this will change the pixel on the screen
pyoxy.tools.info.web.get_chrome_data() # this will get your chrome account information : I AM NOT RESPONSIBLE FOR ANY MALICIOUS USES
pyoxy.tools.info.web.get_chrome_history() # this will get your chrome history : I AM NOT RESPONSIBLE FOR ANY MALICIOUS USES
# pyoxy.tools.Network() # this class is still a work in progress.
