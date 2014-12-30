__author__ = 'tr1b2669'
import pygame
import constants
import sprites
import Buttons
from mouseevents import SurfaceMouseObserver, find_under_cursor

BUTTON_COLOR = (31,150,166)
BUTTON_TEXT_COLOR = constants.WHITE
button_length = 150
button_height = 50
font_size = 27
empty_btw_buttons = 120
class ButtonHolder(SurfaceMouseObserver):
    def __init__(self, surface, color):
        SurfaceMouseObserver.__init__(self, surface)
        self.color = color
        move_x = constants.screen_width/2 - button_length/2 - empty_btw_buttons
        move_y = constants.panel_offset/2 - button_height/2
        move_button = Buttons.Button(surface, BUTTON_COLOR, move_x, move_y, button_length, button_height, 200, "Move", BUTTON_TEXT_COLOR, font_size)

        w_move_x = constants.screen_width/2 - button_length/2 + empty_btw_buttons
        w_move_y = move_y
        wrong_move_button = Buttons.Button(surface, BUTTON_COLOR, w_move_x, w_move_y, button_length, button_height, 10, "Wrong Move", BUTTON_TEXT_COLOR, font_size)
        self.buttons = [move_button, wrong_move_button]
        self.draw()
        self.active_button = None
        self.color = color

    def mouse_moved_cb(self, outside):
        button = find_under_cursor(self.buttons)
        if button:
            self.active_button = button
            button.mouse_in()
            self.draw()
        elif self.active_button:
            self.active_button.mouse_out()
            self.active_button = None
            self.draw()

    def mouse_down_cb(self, outside):

        if outside:
            return
        if self.active_button:
            self.active_button.mouse_down()
            self.draw()

    def mouse_up_cb(self, outside):
        if outside:
            return
        if self.active_button:
            self.active_button.mouse_up()
            self.draw()

    def draw(self):
        self.surface.fill(self.color)
        for button in self.buttons:
            button.draw_button()


class Board(SurfaceMouseObserver):
    def __init__(self, surface):
        SurfaceMouseObserver.__init__(self, surface)
        self.surface = surface
        self.checkers = sprites.Checkers(constants.column_size, constants.row_size)
        self.checkers.create_checkers(surface, constants.checker_length)
        self.image = pygame.image.load('Boardmedium.png').convert()
        self.pieces = pygame.sprite.Group()
        self.moving_piece = None
        self.previous_checker = None

    def update(self):
        self.surface.blit(self.image, (0, 0))
        self.pieces.update()
        self.pieces.draw(self.surface)
        self.checkers.draw(self.surface)

    def setup_pieces(self, setup):
        self.pieces = pygame.sprite.Group()
        for column, row_and_color in setup.iteritems():
            for number in range(0, row_and_color[1]):
                print 'point: ' + str(column) + ' number:' + str(number)
                created_checker = self.checkers.get_checker((column, number))
                if created_checker:
                    print created_checker.log()
                    created_checker.piece = sprites.Piece(self.surface, row_and_color[0],
                                                          created_checker.position,
                                                          constants.piece_radius)
                    self.pieces.add(created_checker.piece)

    def moving_piece_to_prev_checker(self):
        if self.moving_piece:
            self.moving_piece.prev_pos_to_current()
            self.previous_checker.piece = self.moving_piece
            self.previous_checker = None
            self.moving_piece = None

    def mouse_moved_cb(self, outside):
        if outside:
            return
        self.current_pos = pygame.mouse.get_pos()
        # Now see how the mouse position is different from the current
        # player position. (How far did we move?)
        diff_x = self.pos[0] - self.current_pos[0]
        diff_y = self.pos[1] - self.current_pos[1]
        self.pos = self.current_pos
        if self.moving_piece:
            self.moving_piece.rect.x -= diff_x
            self.moving_piece.rect.y -= diff_y

    def mouse_down_cb(self, outside):
        if outside:
            return
        hit_checker = find_under_cursor(self.checkers)
        if not hit_checker or hit_checker.is_empty:
            return
        if self.checkers.is_top_filled_checker(hit_checker):
            self.previous_checker = hit_checker
            self.moving_piece = hit_checker.piece
            hit_checker.pop_piece()

    def mouse_up_cb(self, outside):
        if outside:
            self.moving_piece_to_prev_checker()

        hit_checker = find_under_cursor(self.checkers)
        if not hit_checker or not self.moving_piece:
            return

        if self.moving_piece and hit_checker.is_reserved:
            self.moving_piece_to_prev_checker()
            return
        for i in range(0, constants.max_piece_in_column):
            candidate_checker = self.checkers.get_checker((hit_checker.gammon_pos[0], i))
            if i == constants.max_piece_in_column - 1 or candidate_checker.is_empty:
                candidate_checker.piece = self.moving_piece
                break
        self.moving_piece = None
