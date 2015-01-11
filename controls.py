__author__ = 'tr1b2669'
import pygame
import sys
import constants
from pygame.locals import *
from pgu import gui

class BlockingDialogInternal(gui.Dialog):
    def __init__(self, title_txt,container, **params):
        self.dialog_container = container
        self.title = gui.Label(title_txt)
        self.main = gui.Table()
        gui.Dialog.__init__(self, self.title, self.main)

    def done_action(self, value):
        self.dialog_container.done = True
        pass

    def exit_action(self, value):
        sys.exit()


class BlockingDialog():
    def __init__(self, screen, real_dialog, callback=None):
        self.app = gui.App()
        self.screen = screen
        self.callback = callback
        self.real_dialog = real_dialog
        self.container = gui.Container()
        self.container.add(self.real_dialog, 0, 0)
        self.app.init(self.container)
        self.done = False

    def show(self):
        while not self.done:

            for e in pygame.event.get():
                if e.type is QUIT or e.type is KEYDOWN and e.key == K_ESCAPE:
                    self.done = True
                self.app.event(e)

            self.app.paint(self.screen)
            pygame.display.flip()
            pygame.time.wait(10)

            if self.callback:
                self.done = self.callback()


        self.screen.fill(constants.SCREEN_COLOR)
        pygame.display.flip()
        self.done = False


class UserNameDialogInternal(BlockingDialogInternal):
    def __init__(self, container, **params):

        BlockingDialogInternal.__init__(self, "Enter Username to Match", container, **params)
        self.txt = gui.Input("", size=15)
        self.main.tr()
        self.main.td(self.txt, colspan=3)
        button = gui.Button("Play")
        button.connect(gui.CLICK, self.dialog_container.username_cb, self.txt)
        self.main.td(button, colspan=1)


class UserNameDialog(BlockingDialog):
    def __init__(self, screen):
        BlockingDialog.__init__(self, screen, UserNameDialogInternal(self))
        self.username = None
    def get_username(self):
        self.show()
        return self.username

    def username_cb(self, txt):
        if txt.value is not None or txt.value is not '':
            self.username = txt.value
            self.done = True



class ConnectionErrorInternal(BlockingDialogInternal):
    def __init__(self, container, **params):
        BlockingDialogInternal.__init__(self, "Connection Error", container, **params)
        self.main.tr()
        retry_button = gui.Button("Retry")
        retry_button.connect(gui.CLICK, self.retried, None)
        exit_button = gui.Button("Exit")
        exit_button.connect(gui.CLICK, self.exit_action, None)
        self.main.td(retry_button, colspan=1)
        self.main.td(exit_button, colspan=1)

    def retried(self, value):
        self.dialog_container.retry = True
        self.dialog_container.done = True


class ConnectionErrorDialog(BlockingDialog):
    def __init__(self, screen):
        BlockingDialog.__init__(self, screen, ConnectionErrorInternal(self))
        self.retry = False

    def does_retry(self):
        self.show()
        return self.retry


class MatchOrWatchInternal(BlockingDialogInternal):
    def __init__(self, container, **params):
        self.retry = False
        BlockingDialogInternal.__init__(self, "What do you want to do?", container, **params)
        self.main.tr()
        self.find_match_btn = gui.Button("Find Match")
        self.find_match_btn.connect(gui.CLICK, self.match_or_watch, True)
        self.find_watch_btn = gui.Button("Watch")
        self.find_watch_btn.connect(gui.CLICK, self.match_or_watch, False)
        self.main.td(self.find_match_btn, colspan=1)
        self.main.td(self.find_watch_btn, colspan=1)

    def match_or_watch(self, value):
        self.dialog_container.match = value
        self.dialog_container.done = True


class MatchOrWatchDialog(BlockingDialog):
    def __init__(self, screen):
        BlockingDialog.__init__(self, screen, MatchOrWatchInternal(self))
        self.match = False

    def get_answer(self):
        self.show()
        return self.match


class FindingInternal(BlockingDialogInternal):
    def __init__(self, container, **params):
        self.retry = False
        BlockingDialogInternal.__init__(self, "Finding match", container, **params)
        self.main.tr()


class FindingDialog(BlockingDialog):
    def __init__(self, screen, callback):
        BlockingDialog.__init__(self, screen, FindingInternal(self), callback)





