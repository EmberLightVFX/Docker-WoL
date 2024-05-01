import flet as ft
from app_settings import settings


class SettingsGroup(ft.Column):
    def __init__(
        self,
    ):
        super().__init__()

    def build(self):  # type: ignore
        self.settings_tab = ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text("IP Range"),
                        ft.TextField(
                            settings.ip_range,
                            on_change=self.ip_range_change,
                            expand=True,
                        ),
                    ]
                ),
            ],
        )
        return self.settings_tab

    def ip_range_change(self, e: ft.ControlEvent):
        settings.ip_range = e.control.value
