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

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
font_size = 15
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


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, position, length):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.length = length
        self.image = pygame.Surface((length, length))
        self.image.fill((255, 255, 130))
        self.image.set_colorkey((255, 255, 130))

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


class Piece(BaseSprite):
    def __init__(self, color, position, radius):
        BaseSprite.__init__(self, position, radius * 2)
        self.radius = radius
        self.color = color
        self.draw_piece()

    def draw_piece(self):
        pygame.draw.circle(self.image, self.color, (int(self.radius), int(self.radius)), int(self.radius), 0)


class Checker(BaseSprite):
    def __init__(self, position, length):
        BaseSprite.__init__(self, position, length)
        self.gammon_pos = (-1, -1)
        self.pieces = []
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
        self.show_block()

    def show_block(self):
        self.image.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        label_pos = text_font.render(self.log(), 1, WHITE)
        label_gammon = text_font.render(self.gammon_log(), 1, WHITE)
        self.image.blit(label_pos, (0, 0))
        self.image.blit(label_gammon, (0, self.length - font_size))

    def add_piece(self, my_piece):
        self.pieces.append(my_piece)
        my_piece.set_all_pos(self.rect)
        my_piece.label = len(self.pieces)

        if len(self.pieces) > 1:
            self.image.fill((255, 255, 130))
            self.paint_label(len(self.pieces))
        else:
            self.image.fill((255, 255, 130))

    def paint_label(self, label):
        label_pos = text_font.render(str(label), 1, WHITE)
        self.image.blit(label_pos, (self.length / 2 - font_size / 3, self.length / 2 - font_size / 2))

    def get_piece(self):
        if self.pieces:
            return self.pieces[-1]

    def pop_piece(self):
        return self.pieces.pop()

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
            self.carry_checker.get_piece().rect.x -= diff_x
            self.carry_checker.get_piece().rect.y -= diff_y

        # Now wet the player object to the mouse location
        self.pos = current_pos


def collide_point(block_list, mouse_point):
    result = [s for s in checkers_list if s and s.rect.collidepoint((mouse_point[0],mouse_point[1] -70))]
    if result:
        return result[0]

    return None

# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode([screen_width, screen_height])
screen.fill((78,73,93))
text_font = pygame.font.SysFont("monospace", font_size)
board_image = pygame.image.load('Boardmedium.png').convert()
board_surface = screen.subsurface((0,panel_offset,board_width,board_height)) # A sky surface
piece_list = pygame.sprite.Group()
checkers_list = pygame.sprite.Group()
checkers_dict = {}
for x in range(0, row_size):
    for y in range(0, column_size):
        checker = Checker([x, y], checker_length)
        checkers_list.add(checker)
        checkers_dict[checker.gammon_pos] = checker

for column, row_and_color in initial_setup.iteritems():
# This represents a block
    for number in range(0, row_and_color[1]):
        print 'point: ' + str(column) + ' number:' + str(number)
        checker = checkers_dict[(column, number)]
        if checker:
            print checker.log()
            piece = Piece(row_and_color[0], checker.position, piece_radius)
            checker.add_piece(piece)
            piece_list.add(piece)

mouse = Mouse()
# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()
playtime = 0
# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            checker = collide_point(checkers_list, pygame.mouse.get_pos())

            print 'here - 1'
            if checker and len(checker.pieces) > 0:
                print 'here 3'
                one_high_up =(checker.gammon_pos[0],checker.gammon_pos[1] + 1)
                if one_high_up not in checkers_dict or len(checkers_dict[one_high_up].pieces) == 0:
                    print 'here 2'
                    mouse.carry_checker = checker

        elif event.type == pygame.MOUSEBUTTONUP:
            if mouse.carry_checker:
                current_piece = mouse.carry_checker.get_piece()
                hit_checker = collide_point(checkers_list, pygame.mouse.get_pos())
                if hit_checker and hit_checker.gammon_pos[1] < 0 or hit_checker.gammon_pos[0] < 0:
                    current_piece.prev_pos_to_current()
                    mouse.carry_checker = None
                elif hit_checker:
                    for i in range(0, max_piece_in_column):
                        candidate_checker = checkers_dict[(hit_checker.gammon_pos[0], i)]

                        if candidate_checker.get_piece() == mouse.carry_checker.get_piece():
                            mouse.carry_checker.get_piece().prev_pos_to_current()
                            mouse.carry_checker = None
                            break
                        elif i == max_piece_in_column - 1 or not candidate_checker.pieces:
                            candidate_checker.add_piece(current_piece)
                            mouse.carry_checker.pop_piece()
                            mouse.carry_checker = None
                            break


    piece_list.update()
    mouse.update()
    asd = board_surface.get_abs_offset()
    board_surface.blit(board_image,(0,0))
    piece_list.draw(board_surface)
    # checkers_list.draw(board_surface)
    # screen.blit(board_surface,(0,panel_offset))
    # for debugging



    # Limit to 60 frames per second
    milisec = clock.tick(60)
    playtime += milisec / 1000.0
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
    # print"FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
    #                        clock.get_fps(), " "*5, playtime)

pygame.quit()