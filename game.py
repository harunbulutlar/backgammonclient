"""
Use sprites to pick up blocks

Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/

Explanation video: http://youtu.be/iwLj7iJCFQM
"""
import pygame

import surfaces
import constants
from Tkinter import *
from mouseevents import MouseActionNotifier
# class SplashScreen(Frame):
#     def __init__(self, master=None, width=0.8, height=0.6, useFactor=True):
#         Frame.__init__(self, master)
#         self.pack(side=TOP, fill=BOTH, expand=YES)
#
#         # get screen width and height
#         ws = 100
#         hs = 100
#         w = (useFactor and ws*width) or width
#         h = (useFactor and ws*height) or height
#         # calculate position x, y
#         x = (ws/2) - (w/2)
#         y = (hs/2) - (h/2)
#         self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
#
#         self.master.overrideredirect(True)
#         self.lift()
#
# if __name__ == '__main__':
#     root = Tk()
#
#     sp = SplashScreen(root)
#     sp.config(bg="#3366ff")
#
#     m = Label(sp, text="This is a test of the splash screen\n\n\nThis is only a test.\nwww.sunjay-varma.com")
#     m.pack(side=TOP, expand=YES)
#     m.config(bg="#3366ff", justify=CENTER, font=("calibri", 29))
#
#     Button(sp, text="Press this button to kill the program", bg='red', command=root.destroy).pack(side=BOTTOM, fill=X)
#     root.mainloop()

class UserNameDialog(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.entry_variable = StringVar()
        self.entry = Entry(self,textvariable=self.entry_variable)
        self.initialize()
        self.master.overrideredirect(True)

    def initialize(self):
        self.grid()

        self.entry.grid(column=0,row=0,sticky='EW')
        self.entry.bind("<Return>", self.on_press_enter)
        self.entry_variable.set(u"Enter User Name")

        button = Button(self,text=u"Ok",
                                command=self.on_button_click)
        button.grid(column=1,row=0)

        self.grid_columnconfigure(0, weight=2)
        self.update()
        self.entry.focus_set()
        self.entry.selection_range(0, END)

    def on_button_click(self):
        self.entry.focus_set()
        self.entry.selection_range(0, END)

    def on_press_enter(self):
        self.entry.focus_set()
        self.entry.selection_range(0, END)


pygame.init()
screen = pygame.display.set_mode([constants.screen_width, constants.screen_height])
screen.fill(constants.SCREEN_COLOR)
mouse_notifier = MouseActionNotifier()
app = UserNameDialog(Tk())

app.mainloop()
button_surface_raw = screen.subsurface((0, constants.board_height + constants.panel_offset, constants.board_width, constants.panel_offset))
button_surface = surfaces.ButtonHolder(button_surface_raw, constants.SCREEN_COLOR)

board_surface_raw = screen.subsurface((0, constants.panel_offset, constants.board_width, constants.board_height))
board_surface = surfaces.Board(board_surface_raw)
board_surface.setup_pieces(constants.initial_setup)
registered_surfaces = [board_surface, button_surface]
mouse_notifier.register(registered_surfaces)
# Loop until the user clicks the close button.
done = False




# Used to manage how fast the screen updates
clock = pygame.time.Clock()
playtime = 0

# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():
        done = mouse_notifier.fire(event.type)
    for surface in registered_surfaces:
        surface.update()
    milli_sec = clock.tick(60)
    playtime += milli_sec / 1000.0
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
    # print"FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
    #                        clock.get_fps(), " "*5, playtime)

pygame.quit()