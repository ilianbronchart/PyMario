from data import main
from data import menu
from data import config as c
import pygame as pg
import os
import sys

class App():
    def __init__(self):
        self.menu = None
        self.main = None

    def run(self):
        self.menu = menu.Menu() 
        self.menu.menu_loop()
        if self.menu.quit_state == 'play': #Check whether to continue to game or quit app
            self.main = main.Main()
            self.main.main_loop()
            if self.main.quit_state == 'menu':
                #If you think this is a cheat 
                #to avoid destroying instances,
                #you are right, I'm just too
                #lazy to do that.
                os.execl(sys.executable, sys.executable, *sys.argv) #Restart game

if __name__ == '__main__':
    pg.init() #Initialize pygame module
    c.screen = pg.display.set_mode((c.SCREEN_SIZE.x, c.SCREEN_SIZE.y))
    pg.display.set_caption(c.CAPTION)
    c.clock = pg.time.Clock()

    app = App()
    app.run()

    pg.quit()