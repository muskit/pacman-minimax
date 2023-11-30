import pygame as pg
import application as app

class Scoreboard():
    dot_food_points = 10
    power_pellet_points = 50
    bonus_fruit = 100
    ghost_points = 200

    def __init__(self, play): # game is an instance of application class/game
        # what is settings in this case if we compare with the space invaders ?
        self.score = 0
        self.level = 0
        self.high_score = 0
        self.play = play # using the entire application class by using its instance game ?
        self.screen = play.screen # accessing application screen variable ?
        self.screen_rect = self.screen.get_rect() 
        self.text_color = (255, 255, 255) # white color
        self.font = pg.font.Font(f'{app.Application.PROJECT_DIR}/resources/fonts/Press Start 2P.ttf', 24)
        
        self.score_header = self.font.render("SCORE", True, self.text_color)
        self.score_header_rect = self.score_header.get_rect()
        self.score_header_rect.topleft = (self.screen_rect.right - 280, 30)
        self.score_image = None 
        self.score_rect = None
        self.high_score_header = self.font.render("HIGH SCORE", True, self.text_color)
        self.high_score_header_rect = self.score_header.get_rect()
        self.high_score_header_rect.topleft = (self.screen_rect.right - 280, 104)
        self.high_score_image = None
        self.high_score_rect = None
        self.load_high_score()
        self.prep_score_graphics()
        
    def load_high_score(self):
        try:
            with open(f'{app.Application.PROJECT_DIR}/high_score.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        print(f'Attempting to save our score ({self.score}/{self.high_score})')
        self.high_score = self.score if self.high_score < self.score else self.high_score
        with open(f'{app.Application.PROJECT_DIR}/high_score.txt', 'w') as f:
            f.write(str(self.high_score))
        self.prep_score_graphics()


    def increment_points_power_pellet(self):
        self.score = self.score + Scoreboard.power_pellet_points
        self.prep_score_graphics()

    def increment_points_ghost(self):
        self.score = self.score + Scoreboard.ghost_points
        self.prep_score_graphics()

    def increment_points_dot(self):
        self.score = self.score + Scoreboard.dot_food_points
        self.prep_score_graphics()
    def increment_points_fruit(self):
        self.score = self.score + Scoreboard.bonus_fruit
        self.prep_score_graphics()
    


    def prep_score_graphics(self):
        # graphics prep
        score_str = str(self.score)
        high_score_str = str(self.high_score)
        self.score_image = self.font.render(score_str, True, self.text_color)
        self.high_score_image = self.font.render(high_score_str, True, self.text_color)

        # rects prep
        self.score_rect = self.score_image.get_rect()
        self.score_rect.left = self.screen_rect.right - 280
        self.score_rect.top = 54

        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.left = self.screen_rect.right - 280
        self.high_score_rect.top = 128


    def reset(self):
        self.save_high_score()
        self.score = 0
        self.update()

    def draw(self):
        self.screen.blit(self.score_header, self.score_header_rect)
        self.screen.blit(self.high_score_header, self.high_score_header_rect)
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)

    def update(self):
        self.prep_score_graphics()
        self.draw()