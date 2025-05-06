from oxycloud import draw
from oxycloud import oxygui

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