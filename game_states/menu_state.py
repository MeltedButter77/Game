import pygame
import pygame_gui
from game_states.states import BaseState
from game_states.states import StateTransition

# TODO:
# Add layered menus:
# -> Child menus currently have to be duplicated if accessed from a different parent menu to preserve proper back navigation


class MenuState(BaseState):
    def __init__(self, context):
        super().__init__(context)

        self.ui_manager = context["ui_manager"]
        self.active_menu = "main"

        # Main menu panel
        self.ui_panels = {
            "main": pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((440, 160), (400, 400)),
                manager=self.ui_manager
            ),
            "settings": pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((440, 160), (400, 400)),
                manager=self.ui_manager
            ),
            "pause": pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((440, 160), (400, 400)),
                manager=self.ui_manager
            ),
            "pause_settings": pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((440, 160), (400, 400)),
                manager=self.ui_manager
            ),
        }

        self.main_buttons = {
            "play": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 20), (200, 40)),
                text='Play',
                manager=self.ui_manager,
                container=self.ui_panels["main"]
            ),
            "editor": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 80), (200, 40)),
                text='Editor',
                manager=self.ui_manager,
                container=self.ui_panels["main"]
            ),
            "settings": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 140), (200, 40)),
                text='Settings',
                manager=self.ui_manager,
                container=self.ui_panels["main"]
            ),
            "quit": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 320), (200, 40)),
                text='Quit',
                manager=self.ui_manager,
                container=self.ui_panels["main"]
            ),
        }

        self.settings_buttons = {
            "fullscreen": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 80), (200, 40)),
                text='Fullscreen (wip)',
                manager=self.ui_manager,
                container=self.ui_panels["settings"]
            ),
            "windowed": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 140), (200, 40)),
                text='Windowed',
                manager=self.ui_manager,
                container=self.ui_panels["settings"]
            ),
            "back": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 260), (200, 40)),
                text='Back',
                manager=self.ui_manager,
                container=self.ui_panels["settings"]
            ),
        }

        self.pause_buttons = {
            "resume": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 20), (200, 40)),
                text='Resume',
                manager=self.ui_manager,
                container=self.ui_panels["pause"]
            ),
            "save": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 80), (200, 40)),
                text='Save',
                manager=self.ui_manager,
                container=self.ui_panels["pause"]
            ),
            "settings": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 140), (200, 40)),
                text='Settings',
                manager=self.ui_manager,
                container=self.ui_panels["pause"]
            ),
            "main_menu": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 260), (200, 40)),
                text='Main Menu',
                manager=self.ui_manager,
                container=self.ui_panels["pause"]
            ),
            "quit": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 320), (200, 40)),
                text='Quit',
                manager=self.ui_manager,
                container=self.ui_panels["pause"]
            ),
        }

        self.pause_settings_buttons = {
            "fullscreen": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 80), (200, 40)),
                text='Fullscreen (wip)',
                manager=self.ui_manager,
                container=self.ui_panels["pause_settings"]
            ),
            "windowed": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 140), (200, 40)),
                text='Windowed',
                manager=self.ui_manager,
                container=self.ui_panels["pause_settings"]
            ),
            "back": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((100, 260), (200, 40)),
                text='Back',
                manager=self.ui_manager,
                container=self.ui_panels["pause_settings"]
            ),
        }

        self.switch_menu(self.active_menu)

    def switch_menu(self, menu_name):
        self.active_menu = menu_name
        for panel in self.ui_panels.values():
            panel.hide()

        self.ui_panels[menu_name].show()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.next_transition = StateTransition("quit")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_transition = StateTransition("pop")  # Assuming ESC resumes game via pop

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                # Main menu buttons
                if event.ui_element == self.main_buttons["play"]:
                    self.next_transition = StateTransition("switch", "play")
                elif event.ui_element == self.main_buttons["editor"]:
                    self.next_transition = StateTransition("switch", "editor")
                elif event.ui_element == self.main_buttons["settings"]:
                    self.next_transition = StateTransition("push", "menu", {"submenu": "settings"})
                elif event.ui_element == self.main_buttons["quit"]:
                    self.next_transition = StateTransition("quit")

                # Settings menu buttons
                elif event.ui_element == self.settings_buttons["back"]:
                    self.next_transition = StateTransition("pop")
                elif event.ui_element == self.settings_buttons["fullscreen"]:
                    self.next_transition = StateTransition("setting_change", data="fullscreen")
                elif event.ui_element == self.settings_buttons["windowed"]:
                    self.next_transition = StateTransition("setting_change", data="windowed")

                # Pause menu buttons
                elif event.ui_element == self.pause_buttons["resume"]:
                    self.next_transition = StateTransition("pop")
                elif event.ui_element == self.pause_buttons["save"]:
                    self.next_transition = StateTransition("call", "save_level")
                elif event.ui_element == self.pause_buttons["main_menu"]:
                    self.next_transition = StateTransition("pop_all_push", "menu", {"submenu": "main"})
                elif event.ui_element == self.pause_buttons["settings"]:
                    self.next_transition = StateTransition("push", "menu", {"submenu": "pause_settings"})
                elif event.ui_element == self.pause_buttons["quit"]:
                    self.next_transition = StateTransition("quit")

                # Pause settings menu buttons
                elif event.ui_element == self.pause_settings_buttons["back"]:
                    self.next_transition = StateTransition("pop")
                elif event.ui_element == self.pause_settings_buttons["fullscreen"]:
                    self.context["screen"] = pygame.display.set_mode(self.context["game_size"], pygame.FULLSCREEN)
                elif event.ui_element == self.pause_settings_buttons["windowed"]:
                    self.context["screen"] = pygame.display.set_mode(self.context["game_size"],
                                                                     pygame.SCALED | pygame.RESIZABLE)

            self.ui_manager.process_events(event)

    def update(self, time_delta):
        self.ui_manager.update(time_delta)

    def render(self, screen):
        self.ui_manager.draw_ui(screen)
