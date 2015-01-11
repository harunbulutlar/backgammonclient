__author__ = 'tr1b2669'
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LABEL = (250, 104, 0)
COLOR_KEY = (255, 255, 254)
SCREEN_COLOR = (78, 73, 93)
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
                 19: (WHITE, 5), 24: (BLACK, 1)}