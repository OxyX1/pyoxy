from oxycloud import draw
from oxycloud import oxygui
from oxycloud import nshell

# example of window api

app = oxygui.OxyuGui.Window()
app.CreateWindowWidget()
app.width = 10
app.height = 10
app.title = "my oxyum app!"
app.show()

# example of window overlay api.

# example of esp like window.
overlay = draw.Overlay() # init window
overlay.rect_width = 50 # set width
overlay.rect_height = 100 # set height
overlay.redraw() # udpate the overlay
overlay.message_loop() # loop it; keep running

# example of nshell
# WARNING: NSHELL IS NOT AN ENCRYPTED REVERSE SHELL. WHICH MEANS THE USER CAN TRACE YOUR IP.
# WARNING: CONNECT YOUR IP TO A VPN IF USE FOR MALICIOUS REASONS

my_ip = "127.0.0.1"
my_port = 8080

nshell.sockets.multiclient.createTCPServer()
nshell.sockets.multiclient.bind(my_ip, my_port)
nshell.sockets.multiclient.listen(1)