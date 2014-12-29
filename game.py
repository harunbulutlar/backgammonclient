"""
Use sprites to pick up blocks

Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/

Explanation video: http://youtu.be/iwLj7iJCFQM
"""
import pygame
import random
import Buttons

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LABEL = (250, 104, 0)
COLOR_KEY = (255, 255, 254)
font_size = 25
column_count = 12
column_count_finish = 12 * 2
piece_radius = 37.5
max_piece_in_column = 5
empty_rows = 1
empty_columns = 1

checker_length = piece_radius * 2
column_size = max_piece_in_column * 2 + empty_rows
row_size = column_count + empty_columns
board_width = 975
board_height = 825
panel_offset = 70
screen_width = board_width
screen_height = board_height + panel_offset * 2

initial_setup = {1: (WHITE, 2), 6: (BLACK, 5),
                 8: (BLACK, 3), 12: (WHITE, 5),
                 13: (BLACK, 5), 17: (WHITE, 3),
                 19: (WHITE, 5), 24: (BLACK, 2)}


class Checkers(pygame.sprite.Group):
    def __init__(self, *sprites):
        pygame.sprite.Group.__init__(self, *sprites)
        self.checker_dict = {}

    def add_checker(self, key, checker):
        self.add(checker)
        self.checker_dict[key] = checker

    def checker_is_empty(self, key):
        if key not in self.checker_dict or self.checker_dict[key].is_empty:
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
        self.image.fill(COLOR_KEY)
        self.image.set_colorkey(COLOR_KEY)
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
        empty_column_start_top = column_count + column_count / 2
        empty_column_finish_top = empty_column_start_top + empty_columns + 1
        empty_column_start_bottom = column_count - column_count / 2 + 1
        empty_column_finish_bottom = empty_column_start_bottom - empty_columns - 1

        if self.position[1] < max_piece_in_column:
            x_pos = self.position[0] + column_count + 1
            if empty_column_start_top < x_pos < empty_column_finish_top:
                x_pos = -1 * (column_count_finish + x_pos - empty_column_start_top)
            elif empty_column_finish_top <= x_pos:
                x_pos -= empty_columns
            self.gammon_pos = (x_pos, self.position[1])
        elif self.position[1] >= max_piece_in_column + empty_rows:
            x_pos = column_count - self.position[0]
            if empty_column_finish_bottom < x_pos < empty_column_start_bottom:
                x_pos -= empty_column_start_bottom
            elif empty_column_finish_bottom >= x_pos:
                x_pos += empty_columns
            self.gammon_pos = (x_pos
                               , max_piece_in_column * 2 + empty_rows - 1 - self.position[1])
        else:
            self.gammon_pos = (self.position[0] + column_count + 1, - self.position[1])
        print 'normal ' + self.log()
        print 'gammon ' + self.gammon_log()
        # self.show_block()

    def show_block(self):
        self.image.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        label_pos = text_font.render(self.log(), 1, WHITE)
        label_gammon = text_font.render(self.gammon_log(), 1, WHITE)
        self.image.blit(label_pos, (0, 0))
        self.image.blit(label_gammon, (0, self.length - font_size))


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
        self.image.fill(COLOR_KEY)
        label = len(self._pieces)
        if label > 1:
            label_pos = text_font.render(str(label), 1, LABEL)
            self.image.blit(label_pos, (self.length / 2 - font_size / 3, self.length / 2 - font_size / 2))

    def pop_piece(self):
        popped_piece = self._pieces.pop()
        self.paint_label()
        return popped_piece

        return
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


class Mouse():
    """ This class represents the player. It derives from block and thus gets the same
    ___init___ method we defined above. """
    carry_block_list = []

    # List of all the blocks we are carrying

    def __init__(self):
        self.pos = pygame.mouse.get_pos()
        self.carry_checker = None
    def update(self):
        """ Method called when updating a sprite. """

        # Get the current mouse position. This returns the position
        # as a list of two numbers.
        current_pos = pygame.mouse.get_pos()

        # Now see how the mouse position is different from the current
        # player position. (How far did we move?)
        diff_x = self.pos[0] - current_pos[0]
        diff_y = self.pos[1] - current_pos[1]

        # Loop through each block that we are carrying and adjust
        # it by the amount we moved.
        if self.carry_checker:
            self.carry_checker.piece.rect.x -= diff_x
            self.carry_checker.piece.rect.y -= diff_y

        # Now wet the player object to the mouse location
        self.pos = current_pos

    @staticmethod
    def find_under_cursor(input_list):
        result = [s for s in input_list if s and s.abs_rect.collidepoint(pygame.mouse.get_pos())]
        if result:
            return result[0]
        return None

    @staticmethod
    def get_abs_rect(surface):
        abs_pos = surface.get_abs_offset()
        copy_rect = surface.get_rect().copy()
        copy_rect.x = abs_pos[0] + copy_rect.x
        copy_rect.y = abs_pos[1] + copy_rect.y
        return copy_rect

    def mouse_down_cb(self):
        hit_checker = mouse.find_under_cursor(checkers)
        if not hit_checker:
            return
        if not hit_checker.is_empty:
            next_pos = hit_checker.next_gmy_pos
            if checkers.checker_is_empty(next_pos):
                self.carry_checker = hit_checker

    def mouse_up_cb(self):
        hit_checker = mouse.find_under_cursor(checkers)
        if not hit_checker:
            return
        if self.carry_checker and hit_checker.is_reserved:
                self.carry_checker.piece.prev_pos_to_current()
                self.carry_checker = None
        elif self.carry_checker:
            for i in range(0, max_piece_in_column):
                candidate_checker = checkers.get_checker((hit_checker.gammon_pos[0], i))
                if candidate_checker.piece == self.carry_checker.piece:
                    self.carry_checker.piece.prev_pos_to_current()
                    mouse.carry_checker = None
                    break
                elif i == max_piece_in_column - 1 or candidate_checker.is_empty:
                    candidate_checker.piece = self.carry_checker.piece
                    mouse.carry_checker.pop_piece()
                    mouse.carry_checker = None
                    break

    def process_mouse_event(self, in_event, in_surface, events_dict):
        abs_rec = self.get_abs_rect(in_surface)
        if in_event == pygame.QUIT:
            return True
        if abs_rec.collidepoint(pygame.mouse.get_pos()):
            if in_event in events_dict:
                print 'hereeee'
                events_dict[in_event]()



pygame.init()
screen = pygame.display.set_mode([screen_width, screen_height])
screen.fill((78, 73, 93))
text_font = pygame.font.SysFont("tahoma", font_size)
board_image = pygame.image.load('Boardmedium.png').convert()
board_surface = screen.subsurface((0, panel_offset, board_width, board_height))

button_surface = screen.subsurface((0, board_height + panel_offset, board_width, panel_offset))

piece_list = pygame.sprite.Group()
checkers = Checkers()
debug_list = pygame.sprite.Group()
for x in range(0, row_size):
    for y in range(0, column_size):
        new_checker = Checker(board_surface, [x, y], checker_length)
        checkers.add_checker(new_checker.gammon_pos, new_checker)

for column, row_and_color in initial_setup.iteritems():
    for number in range(0, row_and_color[1]):
        print 'point: ' + str(column) + ' number:' + str(number)
        created_checker = checkers.get_checker((column, number))
        if created_checker:
            print created_checker.log()
            created_checker.piece = Piece(board_surface, row_and_color[0], created_checker.position, piece_radius)
            piece_list.add(created_checker.piece)

mouse = Mouse()

move_button = Buttons.Button()
move_button.create_button(button_surface, (107,142,35), 0, 0, 100, 50, 0, "Move", (255, 255, 255))
wrong_move_button = Buttons.Button()
wrong_move_button.create_button(button_surface, (107,142,35), 0, 0, 100, 50, 0, "Move", (255, 255, 255))
board_events = {pygame.MOUSEBUTTONUP: mouse.mouse_up_cb, pygame.MOUSEBUTTONDOWN: mouse.mouse_down_cb}
# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()
playtime = 0
# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():
        done = mouse.process_mouse_event(event.type, board_surface, board_events)

    piece_list.update()
    mouse.update()
    board_surface.blit(board_image, (0, 0))

    piece_list.draw(board_surface)
    checkers.draw(board_surface)
    milli_sec = clock.tick(60)
    playtime += milli_sec / 1000.0
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
    # print"FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
    #                        clock.get_fps(), " "*5, playtime)

pygame.quit()