import pygame
import pygame_gui
from game_states.states import BaseState, StateTransition


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
            "pause": {
                "resume": self._add_button("Resume", (100, 20)),
                "save": self._add_button("Save", (100, 80)),
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
                "1": self._add_button("Solo", (100, 80)),
                "2": self._add_button("2 Players", (100, 140)),
                "3": self._add_button("3 Players", (100, 200)),
                "4": self._add_button("4 Players", (100, 260))
            },
            "world_select": {
                "1": self._add_button("World 1", (100, 80)),
                "2": self._add_button("World 2", (100, 140)),
                "3": self._add_button("World 3", (100, 200))
            },
            "level_select": {
                "1": self._add_button("Level 1", (100, 80)),
                "2": self._add_button("Level 2", (100, 140)),
                "3": self._add_button("Level 3", (100, 200))
            },
        }

    def _add_button(self, text, pos):
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pos, (200, 40)),
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
                self.next_transitions = [StateTransition("pop")]
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                self._handle_button_event(event.ui_element)

            self.ui_manager.process_events(event)

    def _handle_button_event(self, element):
        current_menu = self.menu_stack[-1] if self.menu_stack else None
        if current_menu == "main":
            if element == self.all_buttons["main"]["play"]:
                self.push_menu("player_count_select")
            elif element == self.all_buttons["main"]["editor"]:
                self.next_transitions = [StateTransition("switch", "editor")]
            elif element == self.all_buttons["main"]["settings"]:
                self.push_menu("settings")
            elif element == self.all_buttons["main"]["quit"]:
                self.next_transitions = [StateTransition("quit")]

        elif current_menu == "pause":
            if element == self.all_buttons["pause"]["resume"]:
                self.next_transitions = [StateTransition("pop")]
            elif element == self.all_buttons["pause"]["save"]:
                self.next_transitions = [StateTransition("call", "save_level")]
            elif element == self.all_buttons["pause"]["settings"]:
                self.push_menu("settings")
            elif element == self.all_buttons["pause"]["main_menu"]:
                self.next_transitions = [StateTransition("clear"), StateTransition("push", "menu", {"submenu": "main"})]
            elif element == self.all_buttons["pause"]["quit"]:
                self.next_transitions = [StateTransition("quit")]

        elif current_menu == "settings":
            if element == self.all_buttons["settings"]["fullscreen"]:
                self.next_transitions = [StateTransition("setting_change", data="fullscreen")]
            elif element == self.all_buttons["settings"]["windowed"]:
                self.next_transitions = [StateTransition("setting_change", data="windowed")]
            elif element == self.all_buttons["settings"]["back"]:
                self.pop_menu()

        if current_menu == "player_count_select":
            for i in range(1, 5):
                if element == self.all_buttons["player_count_select"][str(i)]:
                    self.level_select_data["players"] = i
                    self.push_menu("world_select")
                    break

        elif current_menu == "world_select":
            for i in range(1, 4):
                if element == self.all_buttons["world_select"][str(i)]:
                    self.level_select_data["world"] = i
                    self.push_menu("level_select")
                    break

        elif current_menu == "level_select":
            for i in range(1, 4):
                if element == self.all_buttons["level_select"][str(i)]:
                    self.level_select_data["level"] = i
                    self.next_transitions = [StateTransition("push", "play", {"level_select_data": self.level_select_data})]
                    self.menu_stack.clear()
                    break
        print(self.menu_stack)

    def update(self, time_delta):
        self.ui_manager.update(time_delta)

    def render(self, screen):
        self.ui_manager.draw_ui(screen)
