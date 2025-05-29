import pygame
import pygame_gui
from game_states.state_helpers import BaseState, StateTransition


class MenuState(BaseState):
    def __init__(self, context):
        super().__init__(context)

        self.ui_manager = context["ui_manager"]
        self.menu_stack = []

        # Panels for each menu
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((440, 160), (400, 400)),
            manager=self.ui_manager
        )

        self.all_buttons = {}
        self.build_menus()
        self.push_menu("main")

        self.level_select_data = {"players": 1, "world": 1, "level": 1}

    def build_menus(self):
        self.all_buttons = {
            "main": {
                "play": self._add_button("Play", (100, 20)),
                "editor": self._add_button("Editor", (100, 80)),
                "settings": self._add_button("Settings", (100, 140)),
                "quit": self._add_button("Quit", (100, 320))
            },
            "game_pause": {
                "resume": self._add_button("Resume", (100, 20)),
                "save": self._add_button("Save", (100, 80)),
                "settings": self._add_button("Settings", (100, 140)),
                "level_select": self._add_button("Level Select", (100, 200)),
                "main_menu": self._add_button("Main Menu", (100, 260)),
                "quit": self._add_button("Quit", (100, 320))
            },
            "editor_pause": {
                "resume": self._add_button("Resume", (100, 20)),
                "save": self._add_button("Save", (100, 80), (100, 40)),
                "load": self._add_button("Load", (200, 80), (100, 40)),
                "settings": self._add_button("Settings", (100, 140)),
                "main_menu": self._add_button("Main Menu", (100, 260)),
                "quit": self._add_button("Quit", (100, 320))
            },
            "settings": {
                "fullscreen": self._add_button("Fullscreen (wip)", (100, 80)),
                "windowed": self._add_button("Windowed", (100, 140)),
                "back": self._add_button("Back", (100, 260))
            },
            "player_count_select": {
                "1": self._add_button("Solo", (100, 20)),
                "2": self._add_button("2 Players", (100, 80)),
                "3": self._add_button("3 Players", (100, 140)),
                "4": self._add_button("4 Players", (100, 200)),
                "back": self._add_button("Back", (100, 260)),
                "main_menu": self._add_button("Main Menu", (100, 320)),
            },
            "world_select": {
                "1": self._add_button("World 1", (100, 20)),
                "2": self._add_button("World 2", (100, 80)),
                "3": self._add_button("World 3", (100, 140)),
                "back": self._add_button("Back", (100, 260)),
                "main_menu": self._add_button("Main Menu", (100, 320)),
            },
            "level_select": {
                "1": self._add_button("Level 1", (100, 20)),
                "2": self._add_button("Level 2", (100, 80)),
                "3": self._add_button("Level 3", (100, 140)),
                "back": self._add_button("Back", (100, 260)),
                "main_menu": self._add_button("Main Menu", (100, 320)),
            },
        }

    def _add_button(self, text, pos, size = (200, 40)):
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pos, size),
            text=text,
            manager=self.ui_manager,
            container=self.panel
        )

    def switch_menu(self, menu_name):
        if self.menu_stack:
            self.menu_stack[-1] = menu_name
        else:
            self.menu_stack.append(menu_name)
        self._refresh_buttons()

    def push_menu(self, menu_name):
        self.menu_stack.append(menu_name)
        self._refresh_buttons()

    def pop_menu(self):
        if self.menu_stack:
            self.menu_stack.pop()
        self._refresh_buttons()

    def _refresh_buttons(self):
        # Hide all buttons
        for menu in self.all_buttons.values():
            for button in menu.values():
                button.hide()

        if self.menu_stack:
            current = self.menu_stack[-1]
            for button in self.all_buttons.get(current, {}).values():
                button.show()
        self.panel.show() if self.menu_stack else self.panel.hide()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.next_transitions = [StateTransition("quit")]
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if len(self.menu_stack) > 1:
                    self.pop_menu()
                else:
                    self.next_transitions = [StateTransition("pop")]
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if hasattr(event, "ui_element"):
                    self._handle_button_event(event.ui_element)

            self.ui_manager.process_events(event)

    def _handle_button_event(self, element):
        current_menu = self.menu_stack[-1] if self.menu_stack else None
        if current_menu == "main":
            if element == self.all_buttons[current_menu]["play"]:
                self.push_menu("player_count_select")
            elif element == self.all_buttons[current_menu]["editor"]:
                self.next_transitions = [StateTransition("switch", "editor")]
            elif element == self.all_buttons[current_menu]["settings"]:
                self.push_menu("settings")
            elif element == self.all_buttons[current_menu]["quit"]:
                self.next_transitions = [StateTransition("quit")]

        elif current_menu == "game_pause" or current_menu == "editor_pause":
            # Shared pause menu button logic
            if element == self.all_buttons[current_menu]["resume"]:
                self.next_transitions = [StateTransition("pop")]
            elif element == self.all_buttons[current_menu]["settings"]:
                self.push_menu("settings")
            elif element == self.all_buttons[current_menu]["main_menu"]:
                self.next_transitions = [StateTransition("clear"), StateTransition("push", "menu", {"submenu": "main"})]
            elif element == self.all_buttons[current_menu]["quit"]:
                self.next_transitions = [StateTransition("quit")]
            if element == self.all_buttons[current_menu]["save"]:
                self.next_transitions = [StateTransition("call", "save_level")]

            # Game-specific pause menu button logic
            if current_menu == "game_pause":
                if element == self.all_buttons[current_menu]["level_select"]:
                    self.push_menu("level_select")
                    print(self.menu_stack)

            # Editor-specific pause menu button logic
            if current_menu == "editor_pause":
                if element == self.all_buttons[current_menu]["load"]:
                    self.push_menu("player_count_select")

        elif current_menu == "settings":
            if element == self.all_buttons[current_menu]["fullscreen"]:
                self.next_transitions = [StateTransition("setting_change", data="fullscreen")]
            elif element == self.all_buttons[current_menu]["windowed"]:
                self.next_transitions = [StateTransition("setting_change", data="windowed")]
            elif element == self.all_buttons[current_menu]["back"]:
                self.pop_menu()

        if current_menu == "player_count_select":
            if element == self.all_buttons[current_menu]["back"]:
                self.pop_menu()
            elif element == self.all_buttons[current_menu]["main_menu"]:
                self.next_transitions = [StateTransition("clear"), StateTransition("push", "menu", {"submenu": "main"})]
            for i in range(1, 5):
                if element == self.all_buttons[current_menu][str(i)]:
                    self.level_select_data["players"] = i
                    self.push_menu("world_select")
                    break

        elif current_menu == "world_select":
            if element == self.all_buttons[current_menu]["back"]:
                self.pop_menu()
            elif element == self.all_buttons[current_menu]["main_menu"]:
                self.next_transitions = [StateTransition("clear"), StateTransition("push", "menu", {"submenu": "main"})]
            for i in range(1, 4):
                if element == self.all_buttons[current_menu][str(i)]:
                    self.level_select_data["world"] = i
                    self.push_menu("level_select")
                    break

        elif current_menu == "level_select":
            if element == self.all_buttons[current_menu]["back"]:
                self.pop_menu()
            elif element == self.all_buttons[current_menu]["main_menu"]:
                self.next_transitions = [StateTransition("clear"), StateTransition("push", "menu", {"submenu": "main"})]
            for i in range(1, 4):
                if element == self.all_buttons[current_menu][str(i)]:
                    self.level_select_data["level"] = i
                    # if the level is selected from the main menu or from in-game
                    if self.menu_stack[0] == "main" or self.menu_stack[0] == "game_pause":
                        self.next_transitions = [StateTransition("switch", "game", {"level_select_data": self.level_select_data})]
                    # if the level is selected from the editor
                    if self.menu_stack[0] == "editor_pause":
                        self.next_transitions = [
                            # Close the menu
                            StateTransition("pop"),
                            # Editor is already open behind the menu, no type needed. Data is passed in and will load
                            StateTransition(None, "editor", {"level_select_data": self.level_select_data})
                        ]
                    self.menu_stack.clear()
                    break

    def update(self, time_delta):
        self.ui_manager.update(time_delta)

    def render(self, screen):
        if self.menu_stack:
            # Render based on the menu, allows game_state to be seen behind the pause menu
            if self.menu_stack[0] == "main":
                # Add main menu images and fun stuff here
                screen.fill("Dark blue")
        self.ui_manager.draw_ui(screen)
