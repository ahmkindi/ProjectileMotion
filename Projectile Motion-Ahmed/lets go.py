import pygame, pygame.font, pygame.event, pygame.draw
import math
from tkinter import *
from tkinter import messagebox
pygame.font.init()
pygame.init()
pygame.mixer.init()

blue = [0, 0, 255]
white = [255, 255, 255]
grey = [192, 192, 192]
black = [0, 0, 0]
red = [255, 0 , 0]
yellow = [255, 255, 0]
light_red = [175, 140, 140]

gameDisplay = pygame.display.set_mode((1250, 600))
pygame.display.set_caption("Projectile motion.")
clock = pygame.time.Clock()

Options = pygame.image.load("Options.png").convert()
Start_Screen = pygame.image.load("Start Screen.png").convert()
Flat_Moon = pygame.image.load("Flat Moon.png").convert()
Flat_Earth = pygame.image.load("Flat Earth.png").convert()
Flat_Custom = pygame.image.load("Flat Custom.png").convert()
Enter_Digits_Earth = pygame.image.load("Enter digits Earth.png").convert()
Enter_Digits_Moon = pygame.image.load("Enter digits Moon.png").convert()
Enter_Digits_Custom = pygame.image.load("Enter digits Custom.png").convert()
Instructions = pygame.image.load("Instructions.png").convert()
# Shooting = pygame.mixer.Sound("Shooting.wav")
# Landing = pygame.mixer.Sound("Landing.wav")
#the sound recording was quite weird and was removed, hopefully to be added in maintenance later on.

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)
axis_font = pygame.font.SysFont('Comic Sans MS', 10)

#These values will be needed to import into a function and used when drawing the graph.
maxy_g = 0
distance_g = 0
angle_g = 0
Vx = 0
Vy = 0
inst_time = 0
grav = 0
#reshoot is used to limit the amount of times a user can reshoot the ball, as it resulted in a maximum recusrsion error
#if the user had unlimited times to rethrow.
reshoot = 0


class InputBox:
    # https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame

    def __init__(self, x, y, w, h, text = ""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.final_text = ""

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.final_text = self.text
                    #New variable with the users final answer is created if the press answer. This is done so that the
                    #value can be used later on in calculations
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                if len(self.text) <= 15:
                    # I edited the text input to only take numbers and one period, as the program will only be working
                    # with floats. It will also only allow up to 15 characters as it should be enough for user.
                    if event.key == pygame.K_0 or event.key == pygame.K_1 or event.key == pygame.K_2 or \
                            event.key == pygame.K_3 or event.key == pygame.K_4:
                        self.text += event.unicode
                    elif event.key == pygame.K_5 or event.key == pygame.K_6 or event.key == pygame.K_7 or \
                                    event.key == pygame.K_8 or event.key == pygame.K_9:
                        self.text += event.unicode
                    elif event.key == pygame.K_PERIOD and self.text.count(".") == 0:
                        self.text += event.unicode
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width
    #this is to increase the width if the numbers are too long

    def draw(self, gameDisplay):
        # Blit the text.
        gameDisplay.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(gameDisplay, self.color, self.rect, 2)

    def get_text(self):
        return self.final_text
    # to get the text that they input and pressed enter for.

    def enter_text(self, new_text):
        self.text = new_text
        self.txt_surface = FONT.render(self.text, True, self.color)
    #For the program to enter numbers later on its own.


def button(msg, text_size, text_color, x_msg, y_msg, x_rec, y_rec, width, height, inactive, active, pressed):
#https://pythonprogramming.net/making-interactive-pygame-buttons/

#This function was edited to take in the text, and everything related to the the text to put it all in one simple
#function.
    global reshoot
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
#Check if the mouse coincides with the box to make it look interactive by changing colors.
    if x_rec + width > mouse[0] > x_rec and y_rec + height > mouse[1] > y_rec:
        pygame.draw.rect(gameDisplay, active, (x_rec, y_rec, width, height))
        if click[0] == 1:
            if pressed == "Start":
                options()
            elif pressed == "Restart":
                simulation_intro()
            elif pressed == "Earth":
                enter_values("Earth", "View", 9.80665)
            elif pressed == "Moon":
                enter_values("Moon", "View moon", 1.625)
            elif pressed == "Custom":
                enter_values("Custom", "View custom")
            elif pressed == "View":
                reshoot += 1
                simulation("Earth", "View")
            elif pressed == "View moon":
                reshoot += 1
                simulation("Moon", "View moon")
            elif pressed == "View custom":
                reshoot += 1
                simulation("Custom", "View custom")
            elif pressed == "Instructions":
                instructions()
            elif pressed == "quit":
                pygame.quit()
                quit()
    else:
        pygame.draw.rect(gameDisplay, inactive, (x_rec, y_rec, width, height))

    myfont = pygame.font.SysFont("Arial.fft", text_size)
    label = myfont.render(msg, 1, text_color)
    gameDisplay.blit(label, (x_msg, y_msg))


def ball(x_pos, y_pos, color):
    #this function is simply to blit the ball in the simulation for easier use later one.
    pygame.draw.circle(gameDisplay, color, (x_pos, y_pos), 10, 0)


def instructions():
    # This fucntions will explain instructions to the game for new users.
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        gameDisplay.blit(Instructions, (0, 0))

        button("Back", 37, red, 15, 573, 15, 567, 65, 32, white, grey, "Restart")

        pygame.display.update()
        clock.tick(60)


def options():
    # The screen is to pick whether the simulation will be on Earth, moon or a custom planet.
    options_screen = True
    while options_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        gameDisplay.blit(Options, (0, 0))

        button("EARTH", 70, red, 111, 50, 108, 50, 190, 50, white, grey, "Earth")
        button("MOON", 70, red, 528, 50, 525, 50, 180, 50, white, grey, "Moon")
        button("CUSTOM", 70, red, 944, 50, 941, 50, 225, 50, white, grey, "Custom")

        pygame.display.update()
        clock.tick(60)


def simulation_intro():
#start screen
    global reshoot
    reshoot = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        gameDisplay.blit(Start_Screen, (0, 0))

        button("Start", 115, red, 515, 355, 475, 350, 280, 85, white, grey, "Start")
        button("Instructions", 37, red, 533, 460, 527, 458, 170, 32, white, grey, "Instructions")
        button("Quit", 37, red, 580, 515, 580, 515, 60, 32, white, grey, "quit")
        pygame.display.update()
        clock.tick(15)


def calculations_gravity_known(angle, velocity, h_velocity, v_velocity, time_value, maxy, distance, g, place, answer,
                               view):

    # This function is created to run calculations if gravity is known. This is because all the calculations are the
    # same just with different values of gravity.
    # many conditions are possible as the user can enter two values to calculate the rest (in most cases.)

    if (len(v_velocity) or len(angle) or len(h_velocity) or len(time_value) or len(maxy) > 0) and len(velocity) > 0:

        velocity = float(velocity)

        if len(v_velocity) > 0:
            v_velocity = float(v_velocity)
            time_value = (2 * v_velocity) / g
            maxy = (v_velocity ** 2) / (2 * g)
            check_values(0, velocity, 0, v_velocity, place)
            angle = math.asin(v_velocity / velocity)
            h_velocity = math.cos(angle) * velocity
            distance = 2 * h_velocity * v_velocity / g

        elif len(angle) > 0:
            angle = float(angle)
            check_values(angle, 2, 0, 0, place)
            angle = math.radians(angle)
            v_velocity = math.sin(angle) * velocity
            h_velocity = math.cos(angle) * velocity
            maxy = (v_velocity ** 2) / (2 * g)
            time_value = (2 * v_velocity) / g
            distance = 2 * h_velocity * v_velocity / g

        elif len(h_velocity) > 0:
            h_velocity = float(h_velocity)
            check_values(0, velocity, h_velocity, 0, place)
            angle = math.acos(h_velocity / velocity)
            v_velocity = math.sin(angle) * velocity
            time_value = (2 * v_velocity) / g
            maxy = (v_velocity ** 2) / (2 * g)
            distance = 2 * h_velocity * v_velocity / g

        elif len(time_value) > 0:
            time_value = float(time_value)
            v_velocity = (time_value * g) / 2
            maxy = (v_velocity ** 2) / (2 * g)
            check_values(0, velocity, 0, v_velocity, place)
            angle = math.asin(v_velocity / velocity)
            h_velocity = math.cos(angle) * velocity
            distance = 2 * h_velocity * v_velocity / g

        elif len(maxy) > 0:
            maxy = float(maxy)
            v_velocity = (2 * g * maxy) ** 0.5
            check_values(0, velocity, 0, v_velocity, place)
            time_value = (2 * v_velocity) / g
            angle = math.asin(v_velocity / velocity)
            h_velocity = math.cos(angle) * velocity
            distance = 2 * h_velocity * v_velocity / g

        #only after all calculations are done will the user see the button to view the simulation. This is because the
        # program needs all the informations before drawing the graph.

        button("View projectile", 37, red, 900, 18, 880, 15, 230, 32, white, grey, view)

        if answer == "angle":
            return angle
        elif answer == "velocity":
            return velocity
        elif answer == "hvelocity":
            return h_velocity
        elif answer == "vvelocity":
            return v_velocity
        elif answer == "maxy":
            return maxy
        elif answer == "distance":
            return distance
        elif answer == "time":
            return  time_value

    elif (len(v_velocity) or len(time_value) or len(maxy) or len(distance) or len(angle) > 0) and len(h_velocity) > 0:

        h_velocity = float(h_velocity)

        if len(v_velocity) > 0:
            v_velocity = float(v_velocity)
            time_value = (2 * v_velocity) / g
            maxy = (v_velocity ** 2) / (2 * g)
            velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
            distance = 2 * h_velocity * v_velocity / g
            check_values(0, velocity, h_velocity, 0, place)
            angle = math.acos(h_velocity / velocity)

        elif len(time_value) > 0:
            time_value = float(time_value)
            v_velocity = (time_value * g) / 2
            maxy = (v_velocity ** 2) / (2 * g)
            velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
            distance = 2 * h_velocity * v_velocity / g
            check_values(0, velocity, 0, v_velocity, place)
            angle = math.acos(h_velocity / velocity)

        elif len(maxy) > 0:
            maxy = float(maxy)
            v_velocity = (2 * g * maxy) ** 0.5
            time_value = (2 * v_velocity) / g
            velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
            distance = 2 * h_velocity * v_velocity / g
            check_values(0, velocity, h_velocity, 0, place)
            angle = math.acos(h_velocity / velocity)

        elif len(distance) > 0:
            distance = float(distance)
            v_velocity = (distance * g) / (2 * h_velocity)
            velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
            time_value = (2 * v_velocity) / g
            check_values(0, velocity, h_velocity, 0, place)
            angle = math.acos(h_velocity/velocity)
            maxy = (v_velocity ** 2) / (2 * g)

        elif len(angle) > 0:
            angle = float(angle)
            check_values(angle, (10000 ** 10000), h_velocity, 0, place)
            angle = math.radians(angle)
            velocity = h_velocity / math.cos(angle)
            v_velocity = math.sin(angle) * velocity
            maxy = (v_velocity ** 2) / (2 * g)
            time_value = (2 * v_velocity) / g
            distance = 2 * h_velocity * v_velocity / g

        button("View projectile", 37, red, 900, 18, 880, 15, 230, 32, white, grey, view)

        if answer == "angle":
            return angle
        elif answer == "velocity":
            return velocity
        elif answer == "hvelocity":
            return h_velocity
        elif answer == "vvelocity":
            return v_velocity
        elif answer == "maxy":
            return maxy
        elif answer == "distance":
            return distance
        elif answer == "time":
            return  time_value

    elif (len(distance) or len(angle) > 0) and (len(v_velocity) or len(maxy) or len(time_value) > 0):

        if len(distance) > 0 and len(v_velocity) > 0:
            v_velocity = float(v_velocity)
            distance = float(distance)
            h_velocity = (distance * g) / (2 * v_velocity)
            velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
            time_value = (2 * v_velocity) / g
            check_values(0, velocity, h_velocity, 0, place)
            angle = math.acos(h_velocity / velocity)
            maxy = (v_velocity ** 2) / (2 * g)

        elif len(angle) > 0 and len(v_velocity) > 0:
            v_velocity = float(v_velocity)
            angle = float(angle)
            check_values(angle, 2, 1, 1, place)
            angle = math.radians(angle)
            velocity = v_velocity / math.sin(angle)
            maxy = (v_velocity ** 2) / (2 * g)
            time_value = (2 * v_velocity) / g
            if math.degrees(angle) == 90:
                h_velocity = 0.0
                distance = 0.0
            else:
                h_velocity = math.cos(angle) * velocity
                distance = 2 * h_velocity * v_velocity / g

        elif len(distance) > 0 and len(maxy) > 0:
            maxy = float(maxy)
            distance = float(distance)
            v_velocity = (2 * g * maxy) ** 0.5
            h_velocity = (distance * g) / (2 * v_velocity)
            velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
            time_value = (2 * v_velocity) / g
            check_values(0, velocity, h_velocity, 0, place)
            angle = math.acos(h_velocity / velocity)

        elif len(angle) > 0 and len(maxy) > 0:
            maxy = float(maxy)
            angle = float(angle)
            check_values(angle, 2, 1, 1, place)
            angle = math.radians(angle)
            velocity = v_velocity / math.sin(angle)
            v_velocity = (2 * g * maxy) ** 0.5
            time_value = (2 * v_velocity) / g
            #due to changing the angle from degrees to radians the angle is not exactly pi/2 and the calculated
            #horizontal velocity is not 0, to fix this either the number is roundeed or the followin if statement can
            #be made.
            if math.degrees(angle) == 90:
                h_velocity = 0.0
                distance = 0.0
            else:
                h_velocity = math.cos(angle) * velocity
                distance = 2 * h_velocity * v_velocity / g

        elif len(distance) > 0 and len(time_value) > 0:
            distance = float(distance)
            time_value = float(time_value)
            v_velocity = (time_value * g) / 2
            maxy = (v_velocity ** 2) / (2 * g)
            h_velocity = (distance * g) / (2 * v_velocity)
            velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
            check_values(0, velocity, h_velocity, 0, place)
            angle = math.acos(h_velocity / velocity)

        elif len(angle) > 0 and len(time_value) > 0:
            angle = float(angle)
            time_value = float(time_value)
            check_values(angle, 2, 1, 1, place)
            angle = math.radians(angle)
            v_velocity = (time_value * g) / 2
            maxy = (v_velocity ** 2) / (2 * g)
            velocity = v_velocity / math.sin(angle)
            if math.degrees(angle) == 90:
                h_velocity = 0.0
                distance = 0.0
            else:
                h_velocity = math.cos(angle) * velocity
                distance = 2 * h_velocity * v_velocity / g

        button("View projectile", 37, red, 900, 18, 880, 15, 230, 32, white, grey, view)
        if answer == "angle":
            return angle
        elif answer == "velocity":
            return velocity
        elif answer == "hvelocity":
            return h_velocity
        elif answer == "vvelocity":
            return v_velocity
        elif answer == "maxy":
            return maxy
        elif answer == "distance":
            return distance
        elif answer == "time":
            return  time_value

    elif len(v_velocity) > 0:
        v_velocity = float(v_velocity)
        time_value = (2 * v_velocity) / g
        maxy = (v_velocity ** 2) / (2 * g)
        if answer == "vvelocity":
            return v_velocity
        elif answer == "maxy":
            return maxy
        elif answer == "time":
            return  time_value

    elif len(time_value) > 0:
        time_value = float(time_value)
        v_velocity = (time_value * g) / 2
        maxy = (v_velocity ** 2) / (2 * g)
        if answer == "vvelocity":
            return v_velocity
        elif answer == "maxy":
            return maxy
        elif answer == "time":
            return  time_value

    elif len(maxy) > 0:
        maxy = float(maxy)
        v_velocity = (2 * g * maxy) ** 0.5
        time_value = (2 * v_velocity) / g
        if answer == "vvelocity":
            return v_velocity
        elif answer == "maxy":
            return maxy
        elif answer == "time":
            return  time_value


def check_values(angle, velocity, h_velocity, v_velocity, place):
    # This funstion is to check some rare cases which could cause errors if the user makes the mistakes.
    #these parameters are used to compare eachother and place is used to return it back to its place after repeating
    #the function, so that the wrong values are deleted.
    if (velocity < h_velocity) or (velocity < v_velocity):
        Tk().wm_withdraw() #this will hide the Tkinter window
        messagebox.showinfo("oops", "horizontal velocity and vertical velocity cannot be greater than total"
                                    " velocity. This is because horizontal velocity, vertical velocity and"
                                    " total velocity form a right triangle such that velocity is the"
                                    " hypotenuse.")
        if place == "Earth":
            enter_values("Earth", "View", 9.80665)
        elif place == "Moon":
            enter_values("Moon", "View moon", 1.625)
        elif place == "Custom":
            enter_values("Custom", "View custom")
    if angle > 90:
        Tk().wm_withdraw()
        messagebox.showinfo("oops", "The angle should be the angle with the horizontal. That means in"
                                    "projectile motion the angle should not exceed 90 degrees, otherwise"
                                    "it is being thrown backwards. If you would like a demonstration of an"
                                    "angle above 90 do (the angle you like - 90)")
        if place == "Earth":
            enter_values("Earth", "View", 9.80665)
        elif place == "Moon":
            enter_values("Moon", "View moon", 1.625)
        elif place == "Custom":
            enter_values("Custom", "View custom")
    elif angle == 90 and h_velocity != 0:
        Tk().wm_withdraw()
        messagebox.showinfo("oops", "At 90 degrees the projectile should have no horizontal velocity, as "
                                    "it is thrown directly upwards.")
        if place == "Earth":
            enter_values("Earth", "View", 9.80665)
        elif place == "Moon":
            enter_values("Moon", "View moon", 1.625)
        elif place == "Custom":
            enter_values("Custom", "View custom")


def enter_values(place, view, g = 0.0):
    #This function will allow the users to input their values.
    global maxy_g, distance_g, angle_g, Vx, Vy, inst_time, grav, reshoot
    reshoot = 0
    # The custom needs an extra input box to enter the value of gravity
    if place == "Custom":
        gravity_input = InputBox(741, 69, 140, 32)
    velocity_input = InputBox(413, 128, 140, 32)
    h_velocity_input = InputBox(649, 187, 140, 32)
    v_velocity_input = InputBox(601, 246, 140, 32)
    time_input = InputBox(452, 305, 140, 32)
    angle_input = InputBox(553, 364, 140, 32)
    distance_input = InputBox(383, 423, 140, 32)
    maxy_input = InputBox(633, 482, 140, 32)
    #all the boxes are placed in a list to run them through functions all at once
    if place == "Custom":
        input_boxes = [gravity_input, velocity_input, h_velocity_input, v_velocity_input, time_input, angle_input,
                       distance_input, maxy_input]
    else:
        input_boxes = [velocity_input, h_velocity_input, v_velocity_input, time_input, angle_input, distance_input,
                       maxy_input]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
            for box in input_boxes:
                box.handle_event(event)
                #adds text to box, and makes it look interactive
        for box in input_boxes:
            box.update()
            #change width of box

        if place == "Earth":
            gameDisplay.blit(Enter_Digits_Earth, (0, 0))
        elif place == "Moon":
            gameDisplay.blit(Enter_Digits_Moon, (0, 0))
        elif place == "Custom":
            gameDisplay.blit(Enter_Digits_Custom, (0, 0))
        button("Back", 37, red, 15, 573, 15, 567, 65, 32, white, grey, "Start")
        button("Clear", 37, red, 1150, 18, 1148, 15, 74, 32, white, grey, place)
        button("MAIN MENU", 37, red, 111, 573, 109, 567, 156, 32, white, grey, "Restart")

        for box in input_boxes:
            box.draw(gameDisplay)
            #simply displays all the input boxes on th screen

        if place == "Custom":
            g = gravity_input.get_text()
        velocity = velocity_input.get_text()
        h_velocity = h_velocity_input.get_text()
        v_velocity = v_velocity_input.get_text()
        time_value = time_input.get_text()
        angle = angle_input.get_text()
        distance = distance_input.get_text()
        maxy = maxy_input.get_text()

        #Only if the gravity is known do the following steps:
        if (place == "Custom" and len(g) > 0) or (place == "Earth") or (place == "Moon"):
            g = float(g)
            # changing the global variables is key so they can be used in moving the ball
            grav = g
            #check which ones the user input and pressed enter for.
            if ((len(velocity) > 0) and (len(v_velocity) or len(h_velocity) or len(angle) or len(time_value) or
                                len(maxy) > 0)) or ((len(h_velocity) > 0) and (len(v_velocity) or len(angle) or
                                len(time_value) or len(maxy) or len(distance) > 0)) or ((len(distance) or
                                len(angle) > 0) and (len(v_velocity) or len(maxy) or len(time_value) > 0)):
                #change the global variables so that other functions can use the answers found.
                maxy_g = calculations_gravity_known(angle, velocity, h_velocity, v_velocity, time_value, maxy, distance,
                                g, place, "maxy", view)
                distance_g = calculations_gravity_known(angle, velocity, h_velocity, v_velocity, time_value, maxy,
                                distance, g, place, "distance", view)
                angle_g = calculations_gravity_known(angle, velocity, h_velocity, v_velocity, time_value, maxy,
                                distance, g, place, "angle", view)
                Vy = calculations_gravity_known(angle, velocity, h_velocity, v_velocity, time_value, maxy, distance, g,
                                place, "vvelocity", view)
                Vx = calculations_gravity_known(angle, velocity, h_velocity, v_velocity, time_value, maxy, distance, g,
                                place, "hvelocity", view)
                inst_time = calculations_gravity_known(angle, velocity, h_velocity, v_velocity,
                                time_value, maxy, distance, g, place, "time", view)
                #enter the numbers found into the input boxes for the user to see.
                velocity_input.enter_text(str(round(calculations_gravity_known(angle, velocity, h_velocity, v_velocity,
                                time_value, maxy, distance, g, place, "velocity", view), 5)))
                h_velocity_input.enter_text(str(round(Vx, 5)))
                v_velocity_input.enter_text(str(round(Vy, 5)))
                time_input.enter_text(str(round(inst_time, 5)))
                maxy_input.enter_text(str(round(maxy_g, 5)))
                distance_input.enter_text(str(round(distance_g, 5)))
                angle_input.enter_text(str(round(math.degrees(angle_g), 5)))
            if len(v_velocity) or len(maxy) or len(time_value) > 0:
                v_velocity_input.enter_text(str(round(calculations_gravity_known(angle, velocity, h_velocity, v_velocity,
                                time_value, maxy, distance, g, place, "vvelocity", view), 5)))
                time_input.enter_text(str(round(calculations_gravity_known(angle, velocity, h_velocity, v_velocity,
                                time_value, maxy, distance, g, place, "time", view), 5)))
                maxy_input.enter_text(str(round(calculations_gravity_known(angle, velocity, h_velocity, v_velocity,
                                time_value, maxy, distance, g, place, "maxy", view), 5)))

        #The following are cases only for the custom if gravity is not given as Earth and Moon will always have gravity.
        elif place == "Custom":
            # if (len(velocity) > 0 or len(v_velocity) > 0 or len(h_velocity) > 0) and len(angle) > 0:
            #     angle = float(angle)
            #     check_values(angle, 2, 0, 0, place)
            #     angle = math.radians(angle)
            #     if len(h_velocity) > 0:
            #         h_velocity = float(h_velocity)
            #         velocity_input.enter_text(str(h_velocity / math.cos(angle)))
            #         velocity = h_velocity / math.cos(angle)
            #         v_velocity_input.enter_text(str(math.sin(angle) * velocity))
            #         v_velocity = math.sin(angle) * velocity
            #     elif len(v_velocity) > 0:
            #         v_velocity = float(v_velocity)
            #         velocity_input.enter_text(str(v_velocity / math.sin(angle)))
            #         velocity = v_velocity / math.sin(angle)
            #         h_velocity_input.enter_text(str(math.cos(angle) * velocity))
            #         h_velocity = math.cos(angle) * velocity
            #     elif len(velocity) > 0:
            #         velocity = float(velocity)
            #         v_velocity_input.enter_text(str(math.sin(angle) * velocity))
            #         v_velocity = math.sin(angle) * velocity
            #         h_velocity_input.enter_text(str(math.cos(angle) * velocity))
            #         h_velocity = math.cos(angle) * velocity
            #     velocity_input.enter_text(str(round(velocity, 5)))
            #     v_velocity_input.enter_text(str(round(v_velocity, 5)))
            #     h_velocity_input.enter_text(str(round(h_velocity, 5)))

            #all the cases when they are typed the rest are calculated:
            if (len(time_value) > 0) and ((len(v_velocity) > 0 and (len(h_velocity) or len(angle) > 0)) or
                                (len(velocity) > 0 and (len(h_velocity) or len(angle) or len(v_velocity) or len(maxy) or
                                len(distance) > 0)) or (len(h_velocity) and len(angle) > 0)):
                time_value = float(time_value)
                if len(v_velocity) > 0:
                    v_velocity = float(v_velocity)
                    if len(h_velocity) > 0:
                        h_velocity = float(h_velocity)
                        g = (2 * v_velocity) / time_value
                        distance = 2 * h_velocity * v_velocity / g
                        velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
                        check_values(0, velocity, h_velocity, v_velocity, place)
                        angle = math.acos(h_velocity / velocity)
                        maxy = (v_velocity ** 2) / (2 * g)

                    elif len(angle) > 0:
                        angle = float(angle)
                        check_values(angle, 2, 0, 0, place)
                        angle = math.radians(angle)
                        velocity = v_velocity / math.sin(angle)
                        h_velocity = math.cos(angle) * velocity
                        g = (2 * v_velocity) / time_value
                        maxy = (v_velocity ** 2) / (2 * g)
                        distance = 2 * h_velocity * v_velocity / g

                    elif len(velocity) > 0:
                        velocity = float(velocity)
                        check_values(0, velocity, 0, v_velocity, place)
                        angle = math.asin(v_velocity / velocity)
                        h_velocity = math.cos(angle) * velocity
                        g = (2 * v_velocity) / time_value
                        maxy = (v_velocity ** 2) / (2 * g)
                        distance = 2 * h_velocity * v_velocity / g

                elif len(velocity) > 0:
                    velocity = float(velocity)
                    if len(h_velocity) > 0:
                        h_velocity = float(h_velocity)
                        check_values(0, velocity, h_velocity, 0, place)
                        angle = math.acos(h_velocity / velocity)
                        v_velocity = math.sin(angle) * velocity
                        g = (2 * v_velocity) / time_value
                        maxy = (v_velocity ** 2) / (2 * g)
                        distance = 2 * h_velocity * v_velocity / g
                    elif len(angle) > 0:
                        angle = float(angle)
                        check_values(angle, 2, 0, 0, place)
                        angle = math.radians(angle)
                        v_velocity = math.sin(angle) * velocity
                        h_velocity = math.cos(angle) * velocity
                        g = (2 * v_velocity) / time_value
                        maxy = (v_velocity ** 2) / (2 * g)
                        if math.degrees(angle) == 90:
                            h_velocity = 0.0
                            distance = 0.0
                        else:
                            h_velocity = math.cos(angle) * velocity
                            distance = h_velocity * time_value
                    elif len(distance) > 0:
                        distance = float(distance)
                        h_velocity = distance / time_value
                        check_values(0, velocity, h_velocity, 0, place)
                        angle = math.acos(h_velocity / velocity)
                        v_velocity = math.sin(angle) * velocity
                        g = (2 * v_velocity) / time_value
                        maxy = (v_velocity ** 2) / (2 * g)
                    elif len(maxy) > 0:
                        maxy = float(maxy)
                        v_velocity = (4 * maxy)/time_value
                        angle = angle = math.asin(v_velocity / velocity)
                        h_velocity = math.cos(angle) * velocity
                        distance = h_velocity * time_value
                        g = (2 * v_velocity) / time_value

                elif len(h_velocity) and len(angle) > 0:
                    h_velocity = float(h_velocity)
                    angle = float(angle)
                    check_values(angle, (10000 ** 10000), h_velocity, 0, place)
                    angle = math.radians(angle)
                    velocity = h_velocity / math.cos(angle)
                    v_velocity = math.sin(angle) * velocity
                    g = (2 * v_velocity) / time_value
                    maxy = (v_velocity ** 2) / (2 * g)
                    distance = 2 * h_velocity * v_velocity / g

                # input the answers found into the text boxes for the user to see
                velocity_input.enter_text(str(round(velocity, 5)))
                v_velocity_input.enter_text(str(round(v_velocity, 5)))
                h_velocity_input.enter_text(str(round(h_velocity, 5)))
                angle_input.enter_text(str(round(math.degrees(angle), 5)))
                time_input.enter_text(str(round(time_value, 5)))
                distance_input.enter_text(str(round(distance, 5)))
                maxy_input.enter_text(str(round(maxy, 5)))
                gravity_input.enter_text(str(round(g, 5)))
                #change global variables to be used throughout the simulation.
                maxy_g = maxy
                distance_g = distance
                angle_g = angle
                grav = g
                Vx = h_velocity
                Vy = v_velocity
                inst_time = time_value
                button("View projectile", 37, red, 900, 18, 880, 15, 230, 32, white, grey, view)

            elif (len(maxy) > 0) and ((len(v_velocity) > 0 and (len(h_velocity) or len(angle) or len(velocity) > 0)) or
                                (len(velocity) > 0 and (len(h_velocity) or len(angle) > 0)) or
                                (len(h_velocity) and len(angle) > 0)):
                maxy = float(maxy)
                if len(v_velocity) > 0:
                    v_velocity = float(v_velocity)
                    if len(h_velocity) > 0:
                        h_velocity = float(h_velocity)
                        g = (v_velocity ** 2) / (2 * maxy)
                        distance = 2 * h_velocity * v_velocity / g
                        velocity = math.sqrt((h_velocity ** 2) + (v_velocity ** 2))
                        check_values(0, velocity, h_velocity, v_velocity, place)
                        angle = math.acos(h_velocity / velocity)
                        time_value = (2 * v_velocity) / g
                    elif len(angle) > 0:
                        angle = float(angle)
                        check_values(angle, 2, 0, 0, place)
                        angle = math.radians(angle)
                        velocity = v_velocity / math.sin(angle)
                        g = (v_velocity ** 2) / (2 * maxy)
                        time_value = (2 * v_velocity) / g
                        if math.degrees(angle) == 90:
                            h_velocity = 0.0
                            distance = 0.0
                        else:
                            h_velocity = math.cos(angle) * velocity
                            distance = h_velocity * time_value
                    elif len(velocity) > 0:
                        velocity = float(velocity)
                        check_values(0, velocity, 0, v_velocity, place)
                        angle = math.asin(v_velocity / velocity)
                        h_velocity = math.cos(angle) * velocity
                        g = (v_velocity ** 2) / (2 * maxy)
                        time_value = (2 * v_velocity) / g
                        distance = 2 * h_velocity * v_velocity / g
                elif len(velocity) > 0:
                    velocity = float(velocity)
                    if len(angle) > 0:
                        angle = float(angle)
                        check_values(angle, 2, 0, 0, place)
                        angle = math.radians(angle)
                        v_velocity = math.sin(angle) * velocity
                        g = (v_velocity ** 2) / (2 * maxy)
                        time_value = (2 * v_velocity) / g
                        if math.degrees(angle) == 90:
                            h_velocity = 0.0
                            distance = 0.0
                        else:
                            h_velocity = math.cos(angle) * velocity
                            distance = h_velocity * time_value
                    elif len(h_velocity) > 0:
                        h_velocity = float(h_velocity)
                        h_velocity = float(h_velocity)
                        velocity = float(velocity)
                        check_values(0, velocity, h_velocity, 0, place)
                        angle = math.acos(h_velocity / velocity)
                        v_velocity = math.sin(angle) * velocity
                        g = (v_velocity ** 2) / (2 * maxy)
                        time_value = (2 * v_velocity) / g
                        distance = 2 * h_velocity * v_velocity / g
                elif len(h_velocity) and len(angle) > 0:
                    h_velocity = float(h_velocity)
                    angle = float(angle)
                    # check_values(angle, (1000 ** 1000), h_velocity, 0, place)
                    angle = math.radians(angle)
                    velocity = h_velocity / math.cos(angle)
                    v_velocity = math.sin(angle) * velocity
                    g = (v_velocity ** 2) / (2 * maxy)
                    time_value = (2 * v_velocity) / g
                    distance = 2 * h_velocity * v_velocity / g

                velocity_input.enter_text(str(round(velocity, 5)))
                v_velocity_input.enter_text(str(round(v_velocity, 5)))
                h_velocity_input.enter_text(str(round(h_velocity, 5)))
                angle_input.enter_text(str(round(math.degrees(angle), 5)))
                time_input.enter_text(str(round(time_value, 5)))
                distance_input.enter_text(str(round(distance, 5)))
                maxy_input.enter_text(str(round(maxy, 5)))
                gravity_input.enter_text(str(round(g, 5)))
                maxy_g = maxy
                distance_g = distance
                angle_g = angle
                grav = g
                Vx = h_velocity
                Vy = v_velocity
                inst_time = time_value
                button("View projectile", 37, red, 900, 18, 880, 15, 230, 32, white, grey, view)

            elif (len(velocity) and len(distance) > 0) and (len(angle) or len(v_velocity) or len(h_velocity) > 0):
                velocity = float(velocity)
                distance = float(distance)
                if len(angle) > 0:
                    angle = float(angle)
                    check_values(angle, 2, 0, 0, place)
                    angle = math.radians(angle)
                    v_velocity = math.sin(angle) * velocity
                    check_values(angle, 2, 1, 1, "Custom")
                    if math.degrees(angle) == 90:
                        h_velocity = 0.0
                        distance = 0.0
                    else:
                        h_velocity = math.cos(angle) * velocity
                    g = ((velocity ** 2) * (math.sin(2 * angle)))/distance
                    time_value = (2 * v_velocity) / g
                    maxy = (v_velocity ** 2) / (2 * g)
                elif len(v_velocity) > 0:
                    v_velocity = float(v_velocity)
                    check_values(0, velocity, 0, v_velocity, place)
                    angle = math.asin(v_velocity / velocity)
                    h_velocity = math.cos(angle) * velocity
                    g = ((velocity ** 2) * (math.sin(2 * angle))) / distance
                    time_value = (2 * v_velocity) / g
                    maxy = (v_velocity ** 2) / (2 * g)
                elif len(h_velocity) > 0:
                    h_velocity = float(h_velocity)
                    check_values(0, velocity, h_velocity, 0, place)
                    angle = math.acos(h_velocity / velocity)
                    v_velocity = math.sin(angle) * velocity
                    g = ((velocity ** 2) * (math.sin(2 * angle))) / distance
                    time_value = (2 * v_velocity) / g
                    maxy = (v_velocity ** 2) / (2 * g)


            # if len(velocity) and len(v_velocity) and len(h_velocity) and len(angle) and len(time_value) and
            #     len(distance) and len(maxy) and len(g)
                velocity_input.enter_text(str(round(velocity, 5)))
                v_velocity_input.enter_text(str(round(v_velocity, 5)))
                h_velocity_input.enter_text(str(round(h_velocity, 5)))
                angle_input.enter_text(str(round(math.degrees(angle), 5)))
                time_input.enter_text(str(round(time_value, 5)))
                distance_input.enter_text(str(round(distance, 5)))
                maxy_input.enter_text(str(round(maxy, 5)))
                gravity_input.enter_text(str(round(g, 5)))
                maxy_g = maxy
                distance_g = distance
                angle_g = angle
                grav = g
                Vx = h_velocity
                Vy = v_velocity
                inst_time = time_value
                button("View projectile", 37, red, 900, 18, 880, 15, 230, 32, white, grey, view)

        pygame.display.update()
        clock.tick(30)


def simulation(place, view):
    #This is the function to move the ball
    global maxy_g, distance_g, angle_g, Vx, Vy, grav, inst_time, reshoot

    x_pos = 0
    y_pos = 542
    t = 0
    countx = 500
    county = 220
    counter_x = 0
    counter_y = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        if place == "Earth":
            gameDisplay.blit(Flat_Earth, (0, 0))
        elif place == "Moon":
            gameDisplay.blit(Flat_Moon, (0, 0))
        elif place == "Custom":
            gameDisplay.blit(Flat_Custom, (0, 0))

        #Drawing horizontal and vertical lines to shown clearly how many meters the ball is moving. These lines will act
        #as graph lines.

        for i in range(0, 26):
            pygame.draw.line(gameDisplay, light_red, (i * 50, 550), (i * 50, 0), 1)
        for i in range(0, 13):
            pygame.draw.line(gameDisplay, white, (0, i * 50), (1250, i * 50), 1)

        #All have different background colors, so a suitable color must be chosen for each when displaying the data
        #found on the screen.

        if place == "Moon":
            color = yellow
        else:
            color = blue
        gravity = axis_font.render("g = " + str(round(grav, 4)), False, color)
        time_view = axis_font.render("t = " + str(round(inst_time, 4)), False, color)
        h_v = axis_font.render("Vx = " + str(round(Vx, 4)), False, color)
        v_v = axis_font.render("Vy = " + str(round(Vy, 4)), False, color)
        angle = axis_font.render("L = " + str(round(angle_g, 4)), False, color)
        distance = axis_font.render("d = " + str(round(distance_g, 4)), False, color)
        max_height = axis_font.render("ymax = " + str(round(maxy_g, 4)), False, color)

        gameDisplay.blit(gravity, (3, 135))
        gameDisplay.blit(h_v, (3, 160))
        gameDisplay.blit(v_v, (3, 180))
        gameDisplay.blit(angle, (3, 200))
        gameDisplay.blit(distance, (3, 220))
        gameDisplay.blit(max_height, (3, 235))
        gameDisplay.blit(time_view, (3, 250))


        button("MAIN MENU", 20, red, 16, 20, 15, 15, 79, 25, white, grey, "Restart")
        button("RE-ENTER VALUES", 20, red, 121, 20, 118, 15, 131, 25, white, grey, place)
        if reshoot != 200:
            button("RE-THROW", 20, red, 17, 55, 16, 51, 78, 25, white, grey, view)
        ball(x_pos, y_pos, red)

        # this part is to change position of the ball relative to horizontal and vertical velocity, time and
        # gravity.
        # To ensure the ball doesnt fly off the screen a countx and county are used to change the values respectively
        # such that the curve is still correct, simply re-scaled.

        for i in range (1, 1000000000):
            if (countx - 500) <= int(distance_g) <= countx:
                print(countx)
                break
            # elif int(distance_g) > 5000000:
            else:
                countx += 500

        for i in range(1, 1000000000):
            if (county - 220) <= int(maxy_g) <= county:
                print(county)
                break
            else:
                county += 220

        #Showing the user the distance between each line by labeling the y-axis and x-axis.
        x_axis = axis_font.render(str(countx/25) + " m", False, color)
        y_axis = axis_font.render(str(county/11) + " m", False, color)
        gameDisplay.blit(x_axis, (1, 570))
        gameDisplay.blit(y_axis, (12, 512))

        #moving the ball according to projectile motion equations:
        # horizontal displacement = horizontal speed * time
        # vertical displacement = (vertical velocity)(time) - (0.5)(g)(t ** 2)
        if t <= inst_time:
            x_pos = int((5 / (countx / 250)) * Vx * t)
            y_pos = 542 - int((5 / (county / 110)) * (Vy * t - (0.5 * grav * (t ** 2))))
        # if (t+0.5) >= "inst_time":
        #     if sound_counter == 1:
        #         Landing.play()
        #         sound_counter += 1
        t += (1 / 60) # this is done as the function is run 60 times a second, therefore after 1 second of running the
                      # time will eb one second.
        #
        # if sound_counter == 0:
        #     Shooting.play()
        #     sound_counter+=1

        pygame.display.update()
        clock.tick(60)


simulation_intro()
pygame.quit()
quit()