
import pygame
from pygame.locals import *
import surfaces
import constants
import client
import messages
import util
from mouseevents import MouseActionNotifier

# connector = client.ClientConnector(screen)
# result = connector.connect_and_set_user()

# connector.client_socket.setblocking(0)
# response_message = None


class PyGameMain():
    username='dummy'
    opponent = 'dummer'
    dice = None
    setup = constants.initial_setup
    is_white = False
    message = messages.MOVE()
    message.body.move = [((12, 4), (22, 0)), ((22, 0), (2, 0))]
    dump = message.deserialize()
    re_parsed = util.parse(dump)
    response_message = messages.RSPMOVE()
    response_message.body.dice = [4,3]
    response_message.body.move = re_parsed.body.move

    def __init__(self, game_screen, client_connector, username, message):
        self.game_accessor = GameAccessor(message.body.is_white)
        self.game_accessor.dice = message.body.dice
        self.mouse_notifier = MouseActionNotifier()
        self.screen = game_screen
        self.connector = client_connector
        self.info_surface_raw = self.screen.subsurface((0, 0, constants.board_width, constants.panel_offset))
        self.info_surface = surfaces.InfoHolder(self.info_surface_raw, self.game_accessor,constants.SCREEN_COLOR, username, message.body.opponent)

        self.board_surface_raw = self.screen.subsurface((0, constants.panel_offset, constants.board_width, constants.board_height))
        self.board_surface = surfaces.Board(self.board_surface_raw,self.game_accessor,constants.WHITE if message.body.is_white else constants.BLACK)
        self.board_surface.setup_pieces(message.body.board)

        self.button_surface_raw = self.screen.subsurface((0, constants.board_height + constants.panel_offset, constants.board_width, constants.panel_offset))
        self.button_surface = surfaces.ButtonHolder(self.button_surface_raw, self.game_accessor, constants.SCREEN_COLOR, self.board_surface)
        self.registered_surfaces = [self.board_surface, self.button_surface, self.info_surface]
        self.mouse_notifier.register(self.registered_surfaces)
        self.done = False
        self.clock = pygame.time.Clock()
        self.error = False

    def run(self):
        # -------- Main Program Loop -----------
        while not self.done:

            for event in pygame.event.get():
                self.done = self.mouse_notifier.fire(event.type)
            for surface in self.registered_surfaces:
                surface.update()

            if self.game_accessor.playing:
                if self.game_accessor.send_message:
                    if not self.connector.send_message(self.game_accessor.send_message):
                        self.error = self.done = True
                        break
                    self.game_accessor.send_message = None
                    self.game_accessor.playing = False

            received_message = self.connector.receive_message()
            if not received_message[0]:
                self.error = self.done = True
                break
            if received_message[1]:
                if isinstance(received_message[1], messages.RSPMOVE):
                    self.board_surface.opponent_move(received_message[1].body.move)
                    self.game_accessor.playing = True
                    self.game_accessor.dice = received_message[1].body.dice
                elif isinstance(received_message[1], messages.RSPDICE):
                    self.game_accessor.dice = received_message[1].body.dice
                elif isinstance(received_message[1], messages.RSPWRONGMOVE):
                    self.board_surface.setup_pieces(received_message[1].body.board)
                    if self.game_accessor.wrong_move_pushed:
                        self.game_accessor.wrong_move_pushed = False
                        self.game_accessor.playing = False
                    else:
                        self.game_accessor.playing = True
                elif isinstance(received_message[1], messages.RSPOPDISCON):
                    self.error = self.done = True
                    break
                elif isinstance(received_message[1], messages.RSPERROR):
                    self.game_accessor.playing = True
                    pass

            pygame.display.flip()
            self.clock.tick(60)
        return self.error



class GameAccessor():
    def __init__(self, playing):
        self.playing = playing
        self.animating = False
        self.send_message = None
        self.dice = None
        self.wrong_move_pushed=False

pygame.init()
constants.text_font = pygame.font.SysFont("tahoma", 25)
screen = pygame.display.set_mode([constants.screen_width, constants.screen_height], SWSURFACE)
screen.fill(constants.SCREEN_COLOR)
connector = client.ClientConnector(screen)


pygame_result = True
first = messages.RSPFIRST()
result = ['harun',first]
while pygame_result:
    result = connector.connect_and_set_user()
    timeout = connector.connection.socket.gettimeout()
    connector.connection.socket.settimeout(0.0)
    pygame_main = PyGameMain(screen, connector, result[0], result[1])
    pygame_result = pygame_main.run()
    del pygame_main
    screen.fill(constants.SCREEN_COLOR)

pygame.quit()









