
import pygame
from pygame.locals import *
import surfaces
import constants
import client
from mouseevents import MouseActionNotifier
# username='dummy'
# opponent = 'dummer'
# color  = constants.WHITE
# dice = None
screen = pygame.display.set_mode([constants.screen_width, constants.screen_height], SWSURFACE)
screen.fill(constants.SCREEN_COLOR)

connector = client.ClientConnector(screen)
result = connector.connect_and_set_user()

response_message = result[1]
username = result[0]
opponent = response_message.body.opponent
dice = response_message.body.dice

connector.client_socket.setblocking(0)

pygame.init()
info_surface_raw = screen.subsurface((0, 0, constants.board_width, constants.panel_offset))
info_surface = surfaces.InfoHolder(info_surface_raw,constants.SCREEN_COLOR, username, opponent, dice)

# TODO: watch option too

mouse_notifier = MouseActionNotifier()


board_surface_raw = screen.subsurface((0, constants.panel_offset, constants.board_width, constants.board_height))
board_surface = surfaces.Board(board_surface_raw, color)
board_surface.setup_pieces(response_message.body.board)

button_surface_raw = screen.subsurface((0, constants.board_height + constants.panel_offset, constants.board_width, constants.panel_offset))
button_surface = surfaces.ButtonHolder(button_surface_raw, constants.SCREEN_COLOR, board_surface)


registered_surfaces = [board_surface, button_surface, info_surface]
mouse_notifier.register(registered_surfaces)


done = False

clock = pygame.time.Clock()
playtime = 0

# -------- Main Program Loop -----------
while not done:

    for event in pygame.event.get():
        done = mouse_notifier.fire(event.type)
    for surface in registered_surfaces:
        surface.update()



    pygame.display.flip()
    clock.tick(60)
pygame.quit()