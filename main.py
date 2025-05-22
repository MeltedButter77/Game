import asyncio
import pygame
import pygame_gui

from game_states.editor_state import EditorState
from game_states.menu_state import MenuState
from game_states.play_state import PlayState

WIDTH, HEIGHT = 1280, 720  # Use 320x180 or multiples


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
        next_state = current_state.next_state

        if next_state == "quit":
            self.running = False

        elif next_state == "pause_game":
            self.state_stack.append(self.state_instances["menu"])
            self.state_instances["menu"].switch_menu("pause")
        elif next_state == "resume_game":
            self.state_stack.pop()
        elif next_state == "unload_game":
            self.state_stack.pop(0)
        elif next_state == "save_game":
            self.state_stack[0].save_level()

        elif next_state:
            self.state_stack[-1] = self.state_instances[next_state]

        # Always reset next_state
        if self.state_stack:
            self.state_stack[-1].next_state = None

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
