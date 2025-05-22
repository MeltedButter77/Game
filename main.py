import asyncio
import pygame
import pygame_gui

from game_states.editor_state import EditorState
from game_states.menu_state import MenuState
from game_states.play_state import PlayState

WIDTH, HEIGHT = 1280, 720  # Use 320x180 or multiples


class StateTransition:
    def __init__(self, type_, target=None, data=None):
        self.type = type_          # e.g., "push", "pop", "switch", "quit"
        self.target = target       # e.g., "editor", "menu"
        self.data = data or {}     # Optional extra info


class GameApp:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)

        self.game_context = {
            "ui_manager": pygame_gui.UIManager((WIDTH, HEIGHT)),
            "game_size": (WIDTH, HEIGHT),
            "grid_size": 10
        }
        self.state_instances = {
            "menu": MenuState(self.game_context),
            "play": PlayState(self.game_context),
            "editor": EditorState(self.game_context),
        }
        self.state_stack = [self.state_instances["menu"]]
        self.running = True

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
        transition = getattr(current_state, "next_transition", None)

        if not transition:
            return

        if transition.type == "quit":
            self.running = False

        elif transition.type == "switch":
            self.state_stack[-1] = self.state_instances[transition.target]

        elif transition.type == "push":
            state = self.state_instances[transition.target]
            if "submenu" in transition.data and hasattr(state, "switch_menu"):
                state.switch_menu(transition.data["submenu"])
            self.state_stack.append(state)  # Add the new state to front of stack

        elif transition.type == "pop_all_push":
            self.state_stack.clear()
            state = self.state_instances[transition.target]
            if "submenu" in transition.data and hasattr(state, "switch_menu"):
                state.switch_menu(transition.data["submenu"])
            self.state_stack.append(state)  # Add the new state to front of stack

        elif transition.type == "setting_change":
            if "fullscreen" in transition.data:
                self.screen = pygame.display.set_mode(self.game_context["game_size"], pygame.FULLSCREEN)
            if "windowed" in transition.data:
                self.screen = pygame.display.set_mode(self.game_context["game_size"], pygame.SCALED | pygame.RESIZABLE)

        elif transition.type == "pop":
            self.state_stack.pop()

        # Call a method on the current state. Can be used in menus to run a method when a button is pressed. Used for Save and Load buttons
        elif transition.type == "call":
            method = getattr(self.state_stack[0], transition.target)
            if callable(method):
                method(**transition.data)

        # Always reset transition
        self.state_stack[-1].next_transition = None

    def _update(self):
        time_delta = self.clock.tick(60) / 1000.0
        self.state_stack[-1].update(time_delta)

    def _render(self):
        self.screen.fill((0, 0, 0))

        for state in self.state_stack:
            state.render(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    app = GameApp()
    asyncio.run(app.run())
