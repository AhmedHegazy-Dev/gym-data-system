import sys
import os

from services.gym import Gym
from gui.app import GymApp


def main():
    gym_service = Gym(name="Instant Fitness Gym")
    app = GymApp(gym=gym_service)
    app.mainloop()


if __name__ == "__main__":
    main()
