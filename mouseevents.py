__author__ = 'tr1b2669'
import pygame


def find_under_cursor(input_list):
    result = [s for s in input_list if s and s.abs_rect.collidepoint(pygame.mouse.get_pos())]
    if result:
        return result[0]
    return None


class MouseObserver:

    def __init__(self):
        self.current_pos = self.pos = pygame.mouse.get_pos()

    def fire(self, event):
        pass

    pass


class SurfaceMouseObserver(MouseObserver):

    def __init__(self, surface, game_accessor):
        MouseObserver.__init__(self)
        self.surface = surface
        self.mouse_events = {pygame.MOUSEBUTTONDOWN: self.mouse_down_cb,
                             pygame.MOUSEBUTTONUP: self.mouse_up_cb,
                             pygame.MOUSEMOTION: self.mouse_moved_cb}
        self._disabled = False
        self.game_accessor = game_accessor

    def get_disabled(self):
        if not self.game_accessor.playing or self.game_accessor.animating:
            return True
        return self._disabled

    def set_disabled(self, value):
        self._disabled = value

    def fire(self, event):
        abs_rec = self.get_abs_rect()
        outside = not abs_rec.collidepoint(pygame.mouse.get_pos())

        if not self.get_disabled() and event in self.mouse_events:
            self.mouse_events[event](outside)

    def get_abs_rect(self):
        abs_pos = self.surface.get_abs_offset()
        copy_rect = self.surface.get_rect().copy()
        copy_rect.x = abs_pos[0] + copy_rect.x
        copy_rect.y = abs_pos[1] + copy_rect.y
        return copy_rect

    def animating(self):
        return False

    def update(self):
        pass

    def mouse_up_cb(self, outside):
        pass

    def mouse_down_cb(self, outside):
        pass

    def mouse_moved_cb(self, outside):
        pass


class MouseActionNotifier:
    def __init__(self):
        self.observers = []

    def register(self, observers):
        for observer in observers:
            self.observers.append(observer)

    def fire(self, event):
        if event == pygame.QUIT:
            return True
        for observer in self.observers:
            observer.fire(event)