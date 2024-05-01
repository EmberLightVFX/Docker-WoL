import flet as ft
from tabs.computers import ComputersGroup
from tabs.scans import ScansGroup
from tabs.settings import SettingsGroup


class WoLApp(ft.Column):
    def build(self):  # type: ignore

        self.tab = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text="Computers"),
                ft.Tab(text="Scanner"),
                ft.Tab(text="Settings"),
            ],
        )

        self.computers_tab = ComputersGroup(self)
        self.scanner_tab = ScansGroup(self)
        self.scanner_tab = ScansGroup(self)
        self.scanner_tab.visible = False
        self.settings_tab = SettingsGroup()
        self.settings_tab.visible = False

        # application's root control (i.e. "view") containing all other controls
        return ft.Column(
            width=800,
            controls=[
                ft.Row(
                    [
                        ft.Text(
                            value="Wake on lan", style=ft.TextThemeStyle.HEADLINE_MEDIUM
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                self.tab,
                ft.Column(
                    spacing=25,
                    controls=[
                        self.computers_tab,
                        self.scanner_tab,
                        self.settings_tab,
                    ],
                ),
            ],
        )

    def tabs_changed(self, e: ft.ControlEvent):
        selected_index = self.tab.selected_index

        self.computers_tab.visible = selected_index == 0
        self.scanner_tab.visible = selected_index == 1
        self.settings_tab.visible = selected_index == 2

        self.update()


async def main(page: ft.Page):
    page.title = "ToDo App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    # create app control and add it to the page
    page.add(WoLApp())


ft.app(main)
