# /// script
# dependencies = [
#  "pygame-ce",
#  "pygame-gui",
#  "python-i18n",
# ]
# ///

import asyncio
import sys
import pygame
import pygame._sdl2.controller
import pygame_gui
from game_states.editor_state import EditorState
from game_states.menu_state import MenuState
from game_states.game_state import GameState
from game_classes.input_handler import InputHandler

WIDTH, HEIGHT = 1280, 720  # Use 320x180 or multiples


class GameApp:
    def __init__(self):
        pygame.init()
        pygame._sdl2.controller.init()
        self.clock = pygame.time.Clock()
        if sys.platform in ('emscripten','wasi'):
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)

        self.game_context = {
            "ui_manager": pygame_gui.UIManager((WIDTH, HEIGHT)),
            "screen_size": (WIDTH, HEIGHT),
            "input_handlers": [],
            "grid_size": 16
        }
        self.state_instances = {
            "menu": MenuState(self.game_context),
            "game": GameState(self.game_context),
            "editor": EditorState(self.game_context),
        }
        self.state_stack = [self.state_instances["menu"]]
        self.running = True

        # Load input handlers, no inputs can be added after
        self.load_input_handlers()

    def load_input_handlers(self):
        self.game_context["input_handlers"] = []
        for joystick in [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]:
            print(f"Joystick {joystick.get_instance_id()}: {joystick.get_name()}")

            has_handler = False
            # Check if joystick has a handler, if not add it
            for handler in self.game_context["input_handlers"]:
                if handler.joystick:
                    if joystick.get_instance_id() == handler.joystick.get_instance_id():
                        has_handler = True
            if not has_handler:
                self.game_context["input_handlers"].append(InputHandler(joystick))

        self.game_context["input_handlers"].append(InputHandler("keyboard_1"))
        self.game_context["input_handlers"].append(InputHandler("keyboard_2"))

        # Log input handlers
        print("Total input handlers:", len(self.game_context["input_handlers"]))
        for handler in self.game_context["input_handlers"]:
            if not isinstance(handler.joystick, str):
                print(handler.joystick.get_name())
            else:
                print(handler.joystick)
        print(self.game_context["input_handlers"])

    async def run(self):
        while self.running:
            self._handle_events()
            self._handle_state_transitions()
            self._update()
            self._render()
            await asyncio.sleep(0)  # Yield to web

        pygame.quit()

    def _handle_events(self):
        events = pygame.event.get()
        self.state_stack[-1].handle_events(events)

    def _handle_state_transitions(self):
        current_state = self.state_stack[-1]
        transitions = getattr(current_state, "next_transitions", None)

        if not transitions:
            return

        for transition in transitions:
            if not transition:
                continue

            # Run custom actions from transition.data
            if transition.data:
                if transition.target:
                    state = self.state_instances[transition.target]
                else:
                    state = self.state_stack[-1]

                # Custom actions depending on transition.data
                if "submenu" in transition.data and hasattr(state, "switch_menu"):
                    state.switch_menu(transition.data["submenu"])
                if "level_select_data" in transition.data and hasattr(state, "load_level"):
                    data = transition.data.get("level_select_data")
                    state.load_level(data["players"], data["world"], data["level"])

            if transition.type == "quit":
                self.running = False

            elif transition.type == "switch":
                state = self.state_instances[transition.target]
                self.state_stack[-1] = state

            elif transition.type == "push":
                state = self.state_instances[transition.target]
                self.state_stack.append(state)  # Add the new state to front of stack

            elif transition.type == "setting_change":
                if "fullscreen" in transition.data:
                    self.screen = pygame.display.set_mode(self.game_context["game_size"], pygame.FULLSCREEN)
                if "windowed" in transition.data:
                    self.screen = pygame.display.set_mode(self.game_context["game_size"], pygame.SCALED | pygame.RESIZABLE)

            elif transition.type == "pop":
                # Pops the top-most state
                if len(self.state_stack) > 1:
                    self.state_stack.pop()

            elif transition.type == "clear":
                # Removes all states
                self.state_stack.clear()

            # Call a method on the 2nd-top-most state. Can be used in menus to run a method when a button is pressed. Used for Save and Load buttons
            elif transition.type == "call":
                method = getattr(self.state_stack[-2], transition.target)
                if callable(method):
                    method(**transition.data)

        # Always reset transition
        self.state_stack[-1].next_transitions = None

    def _update(self):
        caption = f"{int(self.clock.get_fps()):02d} FPS"
        pygame.display.set_caption(caption)
        time_delta = self.clock.tick(60) / 1000.0
        self.state_stack[-1].update(time_delta)

    def _render(self):
        self.screen.fill("hot pink")  # This is the background behind every state, this should not be seen.

        for state in self.state_stack:
            state.render(self.screen)

        pygame.display.flip()


app = GameApp()
asyncio.run(app.run())
