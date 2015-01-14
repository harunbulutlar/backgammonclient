# -*- coding: cp1252 -*-
# /usr/bin/env python
#Simon H. Larsen
#Buttons
#Project startet: d. 26. august 2012
import pygame
import uuid

DISABLED_COLOR = (192, 192, 192)


class Button:
    def __init__(self, surface, color, x, y, length, height, width, text, text_color, font_size):
        self.surface = surface
        self.rect = pygame.Rect(x, y, length, height)
        self.main_color = color
        self.current_color = color
        self.clicked_color = (255 - color[0], 255 - color[1], 255 - color[2])
        self.hovered_color = self.color_variant(color, 15)
        self.x = x
        self.y = y
        self.guid = uuid.uuid1()
        self.length = length
        self. height = height
        self.width = width
        self.text = text
        self.text_color = text_color
        self.font_size = font_size
        self.__disabled = False
        self.font = pygame.font.SysFont("Calibri", self.font_size)
        self.text = self.font.render(self.text, 1, self.text_color)
        self.dirty = True

    def get_disabled(self):
        return self.__disabled

    def set_disabled(self, value):
        if self.__disabled != value:
            self.current_color = DISABLED_COLOR if value else self.main_color
            self.__disabled = value
            self.dirty = True

    def draw_button(self):
        pygame.draw.rect(self.surface, self.current_color, (self.x, self.y, self.length, self.height), 0)
        pygame.draw.rect(self.surface, self.current_color, (self.x, self.y, self.length, self.height), 1)
        self.surface.blit(self.text,
                          ((self.x + self.length / 2) - self.text.get_width() / 2, (self.y + self.height / 2) - self.text.get_height() / 2))
        self.dirty = False

    @property
    def abs_rect(self):
        abs_pos = self.surface.get_abs_offset()
        copy_rect = self.rect.copy()
        copy_rect.x = abs_pos[0] + self.rect.x
        copy_rect.y = abs_pos[1] + self.rect.y
        return copy_rect

    def mouse_in(self):
        self.change_color(self.hovered_color)

    def mouse_out(self):
        self.change_color(self.main_color)

    def mouse_down(self):
        self.change_color(self.clicked_color)

    def mouse_up(self):
        self.change_color(self.main_color)

    def change_color(self, color):
        if not self.get_disabled() and self.current_color != color:
            self.current_color = color
            self.dirty = True

    def color_variant(self, in_color, brightness_offset=1):
        hex_color = '#%02x%02x%02x' % (in_color[0], in_color[1], in_color[2])
        """ takes a color like #87c95f and produces a lighter or darker variant """
        if len(hex_color) != 7:
            raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
        rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
        new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
        new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255
        # hex() produces "0x88", we want just "88"
        new_hex = "#" + "".join([hex(i)[2:] for i in new_rgb_int])
        return self.hex_to_rgb(new_hex)

    @staticmethod
    def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def __eq__(self, another):
        return hasattr(another, 'guid') and self.guid == another.guid

    def __hash__(self):
        return hash(self.guid)

