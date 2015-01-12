from __future__ import division

__author__ = 'tr1b2669'
import pygame
import constants
import sprites
import Buttons
import messages
import Queue
import copy
import math
from mouseevents import SurfaceMouseObserver, find_under_cursor

BUTTON_COLOR = (31, 150, 166)
BUTTON_TEXT_COLOR = constants.WHITE
button_length = 150
button_height = 50
font_size = 27
empty_btw_buttons = 120


class InfoHolder(SurfaceMouseObserver):
    def __init__(self, surface, game_accessor, color, name, opponent_name):
        SurfaceMouseObserver.__init__(self, surface, game_accessor)
        self.text_font = pygame.font.SysFont("tahoma", constants.font_size)
        self.color = color
        self.opponent_name = opponent_name
        self.name = name
        self.you_txt = 'You: ' + name
        self.opponent_txt = 'Opponent: ' + opponent_name
        self.turn = '<-- Playing'

    def update(self):
        opponent_txt = self.opponent_txt
        you_txt = self.you_txt
        if self.game_accessor.playing:
            you_txt = self.you_txt + self.turn
        else:
            opponent_txt = self.opponent_txt + self.turn

        self.surface.fill(self.color)
        rendered_you = self.text_font.render(you_txt, 1, constants.WHITE)
        rendered_opponent = self.text_font.render(opponent_txt, 1, constants.WHITE)
        rendered_dice = self.text_font.render(str(self.game_accessor.dice), 1, constants.WHITE)
        self.surface.blit(rendered_you, (0, 0))
        self.surface.blit(rendered_opponent, (0, constants.font_size + 5))
        self.surface.blit(rendered_dice, (constants.screen_width / 2 - 10, constants.font_size + 5))


class ButtonHolder(SurfaceMouseObserver):
    def __init__(self, surface, game_accessor, color, board):
        SurfaceMouseObserver.__init__(self, surface, game_accessor)
        self.color = color
        self.board = board
        move_x = (constants.screen_width - button_length) / 2 - empty_btw_buttons
        move_y = (constants.panel_offset - button_height) / 2
        self.move_button = Buttons.Button(surface, BUTTON_COLOR, move_x, move_y, button_length, button_height, 10,
                                          "Move",
                                          BUTTON_TEXT_COLOR, font_size)

        w_move_x = constants.screen_width / 2 - button_length / 2 + empty_btw_buttons
        self.wrong_move_button = Buttons.Button(surface, BUTTON_COLOR, w_move_x, move_y, button_length, button_height,
                                                10,
                                                "Wrong Move", BUTTON_TEXT_COLOR, font_size)
        self.undo_button = Buttons.Button(surface, BUTTON_COLOR, 5, move_y, button_length, button_height, 10,
                                          "Undo Move", BUTTON_TEXT_COLOR, font_size)

        self.buttons = [self.move_button, self.wrong_move_button, self.undo_button]
        self.click_dictionary = {self.move_button: self.move_button_clicked,
                                 self.undo_button: self.undo_button_clicked,
                                 self.wrong_move_button: self.wrong_move_button_clicked}
        self.active_button = None

    def mouse_moved_cb(self, outside):
        button = find_under_cursor(self.buttons)
        if button:
            self.active_button = button
            button.mouse_in()
        elif self.active_button:
            self.active_button.mouse_out()
            self.active_button = None

    def update(self):
        if not self.get_disabled():
            self.undo_button.set_disabled(not self.board.has_move())
            self.move_button.set_disabled(self.board.can_move())
            self.wrong_move_button.set_disabled(False)
        else:
            self.set_disabled(True)
        self.draw()

    def mouse_down_cb(self, outside):
        if outside:
            return
        if self.active_button:
            self.active_button.mouse_down()

    def mouse_up_cb(self, outside):
        if outside:
            return
        if self.active_button:
            self.active_button.mouse_up()
            self.click_dictionary[self.active_button]()

    def undo_button_clicked(self):
        self.board.undo_move()
        pass

    def move_button_clicked(self):
        message_to_send = messages.MOVE()
        message_to_send.body.move = copy.deepcopy(self.board.pop_moves_to_list())
        self.game_accessor.send_message = message_to_send
        self.board.clear_saved_move()

    def wrong_move_button_clicked(self):
        message_to_send = messages.WRONGMOVE()
        self.game_accessor.send_message = message_to_send
        self.game_accessor.wrong_move_pushed = True

    def draw(self):
        self.surface.fill(self.color)
        for button in self.buttons:
            button.draw_button()

    def set_disabled(self, value):
        for button in self.buttons:
            if button.get_disabled() is not value:
                button.set_disabled(value)


class Board(SurfaceMouseObserver):
    def __init__(self, surface, game_accessor, color):
        SurfaceMouseObserver.__init__(self, surface, game_accessor)
        self.surface = surface
        self.checkers = sprites.Checkers(constants.column_size, constants.row_size)
        self.checkers.create_checkers(surface, constants.checker_length)
        self.image = pygame.image.load('Boardmedium.png').convert()
        self.pieces = pygame.sprite.Group()
        self.moving_piece = None
        self.previous_checker = None
        self.color = color
        self.saved_moves = []
        self.move_animations = Queue.Queue()
        self.current_animation = MoveAnimation(self, None)
        self.message_to_send = None

    def update(self):
        if self.animating():
            self.game_accessor.animating = True
            self.current_animation.run()
        else:
            self.game_accessor.animating = False

        self.surface.blit(self.image, (0, 0))
        self.pieces.update()
        self.pieces.draw(self.surface)
        self.checkers.draw(self.surface)

    def animating(self):
        if self.current_animation.finished:
            if not self.move_animations.empty():
                self.current_animation = self.move_animations.get_nowait()
                return self.animating()
            return False
        return True

    def setup_pieces(self, setup):
        self.pieces = pygame.sprite.Group()
        self.checkers.clear_checkers()
        for column, row_and_color in setup.iteritems():
            if row_and_color[0] == 'EMPTY':
                continue
            for number in range(0, int(row_and_color[1])):
                print 'point: ' + str(column) + ' number:' + str(number)
                created_checker = self.checkers.get_checker((int(column), number))
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
        if outside:
            self.moving_piece_to_prev_checker()
            return

        hit_checker = find_under_cursor(self.checkers)
        if not hit_checker or not self.moving_piece:
            return
        if hit_checker.is_reserved:
            self.moving_piece_to_prev_checker()
            self.moving_piece = None
            return

        if not self.can_place_piece(hit_checker, self.moving_piece):
            self.moving_piece_to_prev_checker()
            self.moving_piece = None
            return

        broken_holder = self.try_break_piece(hit_checker, self.moving_piece)
        break_move = None
        placed_checker = self.stack_piece_to_column(hit_checker, self.moving_piece)
        if broken_holder:
            break_move = Move(placed_checker, broken_holder)


        if placed_checker.gammon_pos != self.previous_checker.gammon_pos:
            move = Move(self.previous_checker, placed_checker, break_move)
            self.save_move(move)

        self.moving_piece = None

    def stack_piece_to_column(self, checker, piece):
        resulting_checker = self.checkers.find_empty_checker(checker)
        if resulting_checker is None:
            resulting_checker = self.checkers.get_last_in_column(checker)

        resulting_checker.piece = piece
        return resulting_checker

    def can_place_piece(self, checker, piece):
        first_checker = self.checkers.get_first_in_column(checker)
        if first_checker.is_full:
            if self.checkers.is_next_empty(first_checker):
                return True
            elif first_checker.piece.color != piece.color:
                return False
        return True

    def try_break_piece(self, checker, piece):
        first_checker = self.checkers.get_first_in_column(checker)
        if first_checker.is_empty:
            return None
        if first_checker.piece.color == piece.color:
            return None
        if not self.checkers.is_next_empty(first_checker):
            return None

        holder = self.add_to_broken_piece_holder(first_checker)
        return holder

    def save_move(self, move):
        self.saved_moves.append(move)
        self.decide_board_disable()

    def pop_moves_to_list(self):
        move_list = []
        while self.has_move():
            move = self.saved_moves.pop()
            linked_move = move.linked_move
            while linked_move:
                move_list.append((linked_move.start_checker.gammon_pos, linked_move.finish_checker.gammon_pos))
                linked_move = linked_move.linked_move
            move_list.append((move.start_checker.gammon_pos, move.finish_checker.gammon_pos))
        move_list.reverse()
        return move_list

    def clear_saved_move(self):
        if self.has_move():
            del self.saved_moves[:]
        self.decide_board_disable()

    def decide_board_disable(self):
        self.set_disabled(not self.can_move())

    def can_move(self):
        return False if len(self.saved_moves) == 2 else True

    def has_move(self):
        return len(self.saved_moves) > 0

    def undo_move(self):
        if self.has_move():
            move = self.saved_moves.pop()
            self.decide_board_disable()
            self.register_move_animation(move, True)

    def opponent_move(self, move_message):
        i = 0
        while i < len(move_message):
            column1 = move_message[i]
            column2 = None
            if i + 1 < len(move_message):
                column2 = move_message[i + 1]
                if column2[1][0] < 0:
                    checker20 = self.checkers.get_checker(column2[0])
                    checker21 = self.checkers.get_checker(column2[1])
                    move = Move(checker20, checker21)
                    self.register_move_animation(move)
                    i += 1
            checker10 = self.checkers.get_checker(column1[0])
            checker11 = self.checkers.get_checker(column1[1])
            move = Move(checker10, checker11)
            self.register_move_animation(move)
            i += 1

    def register_move_animation(self, move, reverse=False):
        animation = MoveAnimation(self, move, reverse)
        animation.init()
        self.move_animations.put(animation)

    def add_to_broken_piece_holder(self, checker):
        piece = checker.pop_piece()
        if piece.color is constants.WHITE:
            broken_holder = self.checkers.get_checker((-25, 0))
        else:
            broken_holder = self.checkers.get_checker((-1, 0))

        broken_holder.piece = piece
        return broken_holder


class MoveAnimation():
    def __init__(self, board, move=None, reverse=False):
        self.board = board
        self.move = move
        self.start_checker = None
        self.finish_checker = None
        self.vector = None
        self.piece = None
        self.finished = True
        self.speed = 15
        self.reverse = reverse

    def init(self):
        self.finished = False
        if self.reverse:
            self.start_checker = self.move.finish_checker
            self.finish_checker = self.move.start_checker
        else:
            self.start_checker = self.move.start_checker
            self.finish_checker = self.move.finish_checker
        self.vector = Vector((self.move.start_checker, self.move.finish_checker))

    def run(self):
        if not self.start_checker.is_empty:
            self.piece = self.start_checker.pop_piece()
        if not self.finished:
            self.piece.rect.x = round(self.piece.rect.x + self.vector.direction_x * self.speed)
            self.piece.rect.y = round(self.piece.rect.y + self.vector.direction_y * self.speed)
            if self.vector.traveled_distance(self.piece) >= self.vector.distance:
                self.piece.rect.x = self.finish_checker.rect.x
                self.piece.rect.y = self.finish_checker.rect.y
                if self.reverse:
                    self.board.try_break_piece(self.finish_checker, self.piece)
                self.finish_checker.piece = self.piece
                if self.move.linked_move:
                    self.move = self.move.linked_move
                    self.init()
                else:
                    self.finished = True


class Vector(object):
    def __init__(self, data):
        self.start, self.finish = data
        (self.start_x, self.start_y), (self.finish_x, self.finish_y) = \
            (self.start.rect.x, self.start.rect.y), (self.finish.rect.x, self.finish.rect.y)

    @property
    def slope(self):
        try:
            return (float(self.finish_y) - self.start_y) / (float(self.finish_x) - self.start_x)
        except ZeroDivisionError:
            # line is vertical
            return None

    @property
    def direction_x(self):
        return (self.finish_x - self.start_x) / self.distance

    @property
    def direction_y(self):
        return (self.finish_y - self.start_y) / self.distance

    @property
    def distance(self):
        return self.traveled_distance(self.finish)

    def traveled_distance(self, position):
        return math.sqrt(math.pow(position.rect.x - self.start_x, 2) + math.pow(
            position.rect.y - self.start_y, 2))

    @property
    def y_intercept(self):
        return self.start_y - self.slope * self.start_x

    def solve_for_y(self, x):
        return float(self.slope) * x + float(self.y_intercept)

    def solve_for_x(self, y):
        return float((y - float(self.y_intercept))) / float(self.slope)


class Move():
    def __init__(self, start, finish, linked_move=None):
        self.start_checker = start
        self.finish_checker = finish
        self.start_pos = start.gammon_pos
        self.finish_pos = finish.gammon_pos
        self.linked_move = linked_move
