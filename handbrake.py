import time


import yaml

from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
environ["PYTHONWARNINGS"] = "ignore"
import pygame


class Handbrake:
    joysticks = None

    @staticmethod
    def get_joysticks():
        if not pygame.get_init():
            pygame.init()
        if not pygame.joystick.get_init():
            pygame.joystick.init()
        if not Handbrake.joysticks:
            Handbrake.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        return Handbrake.joysticks

    def __init__(self, config):
        self.joystick = None
        self.joystick_guid = config["guid"]
        self.joystick_index = config["index"]
        self.joystick_type = config["type"]
        self.joystick_num = config["number"]
        self.joystick_min = float(config.get("min", 0))
        self.joystick_max = float(config.get("max", 1))
        joysticks = self.get_joysticks()
        joysticks = [j for j in joysticks if j.get_guid() == self.joystick_guid]
        joystick = joysticks[self.joystick_index]
        joystick.init()
        self.joystick = joystick

    def close(self):
        self.joystick.quit()

    def get_pressed(self):
        pygame.event.pump()
        if self.joystick_type == "axis":
            value = self.joystick.get_axis(self.joystick_num)
            threshold = (self.joystick_max - self.joystick_min) * 0.7 + self.joystick_min
            if self.joystick_max > threshold:
                pressed = value > threshold
            else:
                pressed = value < threshold
            return pressed
        elif self.joystick_type == "button":
            value = self.joystick.get_button(self.joystick_num)
            return value
        else:
            return False

    @staticmethod
    def get_all_inputs(joysticks):
        options = []
        joystick_indices = {}

        for joystick in joysticks:
            pygame.event.pump()
            if joystick.get_guid() not in joystick_indices:
                joystick_indices[joystick.get_guid()] = -1
            joystick_indices[joystick.get_guid()] += 1

            for axis in range(joystick.get_numaxes()):
                value = joystick.get_axis(axis)
                options.append({
                    "guid": joystick.get_guid(),
                    "index": joystick_indices[joystick.get_guid()],
                    "type": "axis",
                    "number": axis,
                    "value": value
                })
            for button in range(joystick.get_numbuttons()):
                value = joystick.get_button(button)
                options.append({
                    "guid": joystick.get_guid(),
                    "index": joystick_indices[joystick.get_guid()],
                    "type": "button",
                    "number": button,
                    "value": value
                })
        return options


if __name__ == "__main__":
    print("This script will help you generate the handbrake configuration:\n")
    joysticks = Handbrake.get_joysticks()
    for joystick in joysticks:
        joystick.init()

    input("Fully let go off the handbrake and press ENTER")
    dummy = Handbrake.get_all_inputs(joysticks)
    input("Fully engage the handbrake and press ENTER")
    state_max = Handbrake.get_all_inputs(joysticks)
    input("Fully let go off the handbrake and press ENTER")
    state_min = Handbrake.get_all_inputs(joysticks)
    options_max = [x for x in state_max if x not in state_min]
    options_min = [x for x in state_min if x not in state_max]

    if len(options_max) > 1:
        input("More than one button/axis was pressed, please try again.")
    elif len(options_max) == 0:
        input("No button/axis was pressed, please try again.")
    else:
        p_max = options_max[0]
        p_min = options_min[0]

        p_max["max"] = p_max["value"]
        p_max["min"] = p_min["value"]
        del p_max["value"]
        print("\nPlease add the following to your config.yml:\n")
        print(yaml.dump({"handbrake": p_max}))
        input()

