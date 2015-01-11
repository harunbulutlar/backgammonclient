from __future__ import division

__author__ = 'tr1b2669'
import pygame
import constants
import sprites
import Buttons
import messages
from mouseevents import SurfaceMouseObserver, find_under_cursor

BUTTON_COLOR = (31, 150, 166)
BUTTON_TEXT_COLOR = constants.WHITE
button_length = 150
button_height = 50
font_size = 27
empty_btw_buttons = 120


class InfoHolder(SurfaceMouseObserver):
    def __init__(self, surface, color, name, opponent_name, dice):
        SurfaceMouseObserver.__init__(self, surface)
        self.text_font = pygame.font.SysFont("tahoma", constants.font_size)
        self.color = color
        self.dice = dice
        self.opponent_name = opponent_name
        self.name = name
        self.label_name = self.text_font.render('You: ' + name, 1, constants.WHITE)
        self.label_opponent_name = self.text_font.render('Opponent: ' + opponent_name, 1, constants.WHITE)
        self.surface.blit(self.label_name, (0, 0))
        self.surface.blit(self.label_opponent_name, (0, constants.font_size + 5))


class ButtonHolder(SurfaceMouseObserver):
    def __init__(self, surface, color, board):
        SurfaceMouseObserver.__init__(self, surface)
        self.color = color
        self.board = board
        move_x = (constants.screen_width - button_length) / 2 - empty_btw_buttons
        move_y = (constants.panel_offset - button_height) / 2
        move_button = Buttons.Button(surface, BUTTON_COLOR, move_x, move_y, button_length, button_height, 10, "Move",
                                     BUTTON_TEXT_COLOR, font_size)

        w_move_x = constants.screen_width / 2 - button_length / 2 + empty_btw_buttons
        wrong_move_button = Buttons.Button(surface, BUTTON_COLOR, w_move_x, move_y, button_length, button_height, 10,
                                           "Wrong Move", BUTTON_TEXT_COLOR, font_size)
        undo_button = Buttons.Button(surface, BUTTON_COLOR, 5, move_y, button_length, button_height, 10,
                                     "Undo Move", BUTTON_TEXT_COLOR, font_size)

        self.buttons = [move_button, wrong_move_button, undo_button]
        self.draw()
        self.active_button = None

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
            self.button_clicked(self.active_button)


    def button_clicked(self, button):
        message_to_send = None
        if button.text == "Undo Move":
            self.board.undo_move()
        elif button.text == "Move":
            message_to_send = messages.MOVE()
            message_to_send.body.move = self.board.move
        elif button.text == "Wrong Move":
            message_to_send = messages.WRONGMOVE()
        self.board.message_to_send = message_to_send


    def draw(self):
        self.surface.fill(self.color)
        for button in self.buttons:
            button.draw_button()


class Board(SurfaceMouseObserver):
    def __init__(self, surface, color):
        SurfaceMouseObserver.__init__(self, surface)
        self.surface = surface
        self.checkers = sprites.Checkers(constants.column_size, constants.row_size)
        self.checkers.create_checkers(surface, constants.checker_length)
        self.image = pygame.image.load('Boardmedium.png').convert()
        self.pieces = pygame.sprite.Group()
        self.moving_piece = None
        self.previous_checker = None
        self.color = color
        self.move = []
        self.move_animation = None
        self.message_to_send = None

    def update(self):
        if self.move_animation:
            if self.move_animation.finished:
                self.move_animation = None
                self.disabled = False
            else:
                self.move_animation.move()

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
        if hit_checker.piece.color is not self.color:
            return

        if self.checkers.is_next_empty(hit_checker):
            self.previous_checker = hit_checker
            self.moving_piece = hit_checker.piece
            hit_checker.pop_piece()

    def mouse_up_cb(self, outside):
        final_checker = None
        if outside:
            self.moving_piece_to_prev_checker()
            return

        hit_checker = find_under_cursor(self.checkers)
        if not hit_checker or not self.moving_piece:
            return
        if hit_checker.is_reserved:
            self.moving_piece_to_prev_checker()
            return
        first_checker = self.checkers.get_checker((hit_checker.gammon_pos[0], 0))

        if not first_checker.is_empty:
            if first_checker.piece.color is not self.moving_piece.color:
                if self.checkers.is_next_empty(first_checker):
                    broken_piece = first_checker.pop_piece()
                    final_checker = self.add_broken_piece_holder(broken_piece)
                else:
                    self.moving_piece_to_prev_checker()
                    return

        for i in range(0, constants.max_piece_in_column):
            candidate_checker = self.checkers.get_checker((hit_checker.gammon_pos[0], i))

            if i == constants.max_piece_in_column - 1 or candidate_checker.is_empty:
                candidate_checker.piece = self.moving_piece
                final_checker = candidate_checker
                break
        self.moving_piece = None
        if final_checker:
            self.save_move(final_checker)

    def save_move(self, final_checker):
        self.move.append((self.previous_checker.gammon_pos, final_checker.gammon_pos))
        self.disabled = True if len(self.move) == 2 else False

    def undo_move(self):
        if len(self.move) > 0:
            gammon_pos = self.move.pop()
            moved_to_checker = self.checkers.get_checker(gammon_pos[1])
            moved_from_checker = self.checkers.get_checker(gammon_pos[0])
            if not moved_to_checker.is_empty:
                piece = moved_to_checker.pop_piece()
                self.disabled = True
                self.move_animation = MoveAnimation(moved_to_checker, moved_from_checker, piece)

    def opponent_move(self, move_message):
        moved_from_checker = self.checkers.get_checker(move_message[0])
        moved_to_checker = self.checkers.get_checker(move_message[1])
        if not moved_to_checker.is_empty:
            piece = moved_to_checker.pop_piece()
            self.disabled = True
            self.move_animation = MoveAnimation(moved_from_checker, moved_to_checker, piece)

    def add_broken_piece_holder(self, piece):
        if piece.color is constants.WHITE:
            broken_holder = self.checkers.get_checker((-25, 0))
            broken_holder.piece = piece
        else:
            broken_holder = self.checkers.get_checker((-1, 0))

        broken_holder.piece = piece
        return broken_holder


class MoveAnimation():
    def __init__(self, moved_from, moved_to, piece):
        self.moved_from = moved_from
        self.moved_to = moved_to
        self.line = Line(
            ((self.moved_from.rect.x, self.moved_from.rect.y), (self.moved_to.rect.x, self.moved_to.rect.y)))
        self.move_from_position = self.moved_from.rect
        self.move_to_position = self.moved_to.rect
        self.piece = piece
        self.finished = False
        self.speed = 10
        if self.line.slope is None:
            if self.moved_to.rect.y - self.moved_from.rect.y > 0:
                self.speed *= -1
        elif self.moved_to.rect.x - self.moved_from.rect.x < 0:
            if self.line.slope is not None:
                self.speed *= -1

    def move(self):
        self.finished = self.moved_to.rect.colliderect(self.piece.rect)
        if self.finished:
            self.piece.rect.x = self.moved_to.rect.x
            self.piece.rect.y = self.moved_to.rect.y
            self.moved_to.piece = self.piece
            return
        if self.line.slope is None:
            self.piece.rect.y -= self.speed
        else:
            self.piece.rect.x += self.speed
            self.piece.rect.y = self.line.solve_for_y(self.piece.rect.x)


class Line(object):
    def __init__(self, data):
        self.first, self.second = data

    @property
    def slope(self):
        (x1, y1), (x2, y2) = self.first, self.second
        try:
            return (float(y2) - y1) / (float(x2) - x1)
        except ZeroDivisionError:
            # line is vertical
            return None

    @property
    def y_intercept(self):
        x, y = self.first
        return y - self.slope * x

    def solve_for_y(self, x):
        return float(self.slope) * x + float(self.y_intercept)

    def solve_for_x(self, y):
        return float((y - float(self.y_intercept))) / float(self.slope)
