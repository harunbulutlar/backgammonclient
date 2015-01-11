__author__ = 'tr1b2669'
import pygame
import constants
import random


class Checkers(pygame.sprite.Group):
    def __init__(self, length, width, *sprites):
        pygame.sprite.Group.__init__(self, *sprites)
        self.length = length
        self.width = width
        self.checker_dict = {}

    def create_checkers(self, surface, size):
        for x in range(0, self.width):
            for y in range(0, self.length):
                new_checker = Checker(surface, [x, y], size)
                self.add_checker(new_checker.gammon_pos, new_checker)

    def add_checker(self, key, checker):
        self.add(checker)
        self.checker_dict[key] = checker

    def is_next_empty(self, checker):
        if checker.next_gmy_pos not in self.checker_dict or self.checker_dict[checker.next_gmy_pos].is_empty:
            return True
        else:
            return False

    def get_checker(self, key):
        if key in self.checker_dict:
            return self.checker_dict[key]


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, surface, position, length):
        super(BaseSprite, self).__init__()
        self.position = position
        self.length = length
        self.image = pygame.Surface((length, length))
        self.image.fill(constants.COLOR_KEY)
        self.image.set_colorkey(constants.COLOR_KEY)
        self.surface = surface

        self.rect = self.image.get_rect()
        self.previous_rect = self.image.get_rect()
        self.set_all_pos(position, length)

    @staticmethod
    def set_pos(rect, position, multiplier=1):
        if hasattr(position, 'x') and hasattr(position, 'y'):
            rect.x = position.x * multiplier
            rect.y = position.y * multiplier
        else:
            rect.x = position[0] * multiplier
            rect.y = position[1] * multiplier

    def set_current_pos(self, position, multiplier=1):
        self.set_pos(self.rect, position, multiplier)

    def set_prev_pos(self, position, multiplier=1):
        self.set_pos(self.previous_rect, position, multiplier)

    def set_all_pos(self, position, multiplier=1):
        self.set_prev_pos(position, multiplier)
        self.set_current_pos(position, multiplier)

    def current_pos_to_prev(self):
        self.set_pos(self.previous_rect, self.rect)
        pass

    def prev_pos_to_current(self):
        self.set_pos(self.rect, self.previous_rect)
        pass

    def log(self):
        return str(self.position[0]) + ',' + str(self.position[1])

    @property
    def abs_rect(self):
        abs_pos = self.surface.get_abs_offset()
        copy_rect = self.image.get_rect().copy()
        copy_rect.x = abs_pos[0] + self.rect.x
        copy_rect.y = abs_pos[1] + self.rect.y
        return copy_rect


class Piece(BaseSprite):
    def __init__(self, surface, color, position, radius):
        BaseSprite.__init__(self, surface, position, radius * 2)
        self.radius = radius
        self.color = color
        self.draw_piece()

    def draw_piece(self):
        pygame.draw.circle(self.image, self.color, (int(self.radius), int(self.radius)), int(self.radius), 0)


class Checker(BaseSprite):
    def __init__(self, surface, position, length):
        BaseSprite.__init__(self, surface, position, length)
        self.gammon_pos = (-1, -1)
        self._pieces = []
        self.text_font = pygame.font.SysFont("tahoma", constants.font_size)
        empty_column_start_top = constants.column_count + constants.column_count / 2
        empty_column_finish_top = empty_column_start_top + constants.empty_columns + 1
        empty_column_start_bottom = constants.column_count - constants.column_count / 2 + 1
        empty_column_finish_bottom = empty_column_start_bottom - constants.empty_columns - 1

        if self.position[1] < constants.max_piece_in_column:
            x_pos = self.position[0] + constants.column_count + 1
            if empty_column_start_top < x_pos < empty_column_finish_top:
                x_pos = -1 * (constants.column_count_finish + x_pos - empty_column_start_top)
            elif empty_column_finish_top <= x_pos:
                x_pos -= constants.empty_columns
            self.gammon_pos = (x_pos, self.position[1])
        elif self.position[1] >= constants.max_piece_in_column + constants.empty_rows:
            x_pos = constants.column_count - self.position[0]
            if empty_column_finish_bottom < x_pos < empty_column_start_bottom:
                x_pos -= empty_column_start_bottom
            elif empty_column_finish_bottom >= x_pos:
                x_pos += constants.empty_columns
            self.gammon_pos = (x_pos, constants.max_piece_in_column * 2 + constants.empty_rows - 1 - self.position[1])
        else:
            self.gammon_pos = (self.position[0] + constants.column_count + 1, - self.position[1])
        print 'normal ' + self.log()
        print 'gammon ' + self.gammon_log()

        # self.show_block()

    def show_block(self):
        self.image.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        label_pos = self.text_font.render(self.log(), 1, constants.WHITE)
        label_gammon = self.text_font.render(self.gammon_log(), 1, constants.WHITE)
        self.image.blit(label_pos, (0, 0))
        self.image.blit(label_gammon, (0, self.length - constants.font_size))

    @property
    def piece(self):
        if self._pieces:
            return self._pieces[-1]
        else:
            return None

    @piece.setter
    def piece(self, my_piece):
        self._pieces.append(my_piece)
        my_piece.set_all_pos(self.rect)
        my_piece.label = len(self._pieces)
        self.paint_label()

    def paint_label(self):
        self.image.fill(constants.COLOR_KEY)
        label = len(self._pieces)
        if label > 1:
            label_pos = self.text_font.render(str(label), 1, constants.LABEL)
            self.image.blit(label_pos,
                            (self.length / 2 - constants.font_size / 3, self.length / 2 - constants.font_size / 2))

    def pop_piece(self):
        popped_piece = self._pieces.pop()
        self.paint_label()
        return popped_piece

    @property
    def is_reserved(self):
        return self.gammon_pos[1] < 0 or self.gammon_pos[0] < 0

    @property
    def is_empty(self):
        if not self._pieces or len(self._pieces) == 0:
            return True
        else:
            return False

    @property
    def next_gmy_pos(self):
        return self.gammon_pos[0], self.gammon_pos[1] + 1

    def gammon_log(self):
        return str(self.gammon_pos[0]) + ',' + str(self.gammon_pos[1])
