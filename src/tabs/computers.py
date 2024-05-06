from typing import TYPE_CHECKING, Callable

import flet as ft
from app_settings import settings
from wakeonlan import send_magic_packet

if TYPE_CHECKING:
    from main import WoLApp


class Computer(ft.Column):
    def __init__(
        self,
        name: str,
        mac_address: str,
        status_change: Callable[..., None],
        delete: Callable[["Computer"], None],
    ):
        super().__init__()
        self.name = name
        self.mac_address = mac_address
        self.status_change = status_change
        self.delete = delete

    def build(self):  # type: ignore
        self.display_name = ft.Text(value=self.name)
        self.display_mac_address = ft.Text(value=self.mac_address)
        self.edit_name = ft.TextField(expand=1)
        self.edit_mac_address = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_name,
                self.display_mac_address,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.PLAY_ARROW,
                            tooltip="Run",
                            on_click=self.run_clicked,
                        ),
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                self.edit_mac_address,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls=[self.display_view, self.edit_view])

    def run_clicked(self, e: ft.ControlEvent):
        send_magic_packet(self.mac_address)

    def edit_clicked(self, e: ft.ControlEvent):
        self.edit_name.value = self.display_name.value
        self.edit_mac_address.value = self.display_mac_address.value
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e: ft.ControlEvent):
        self.display_name.value = self.edit_name.value
        self.display_mac_address.value = self.edit_mac_address.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def delete_clicked(self, e: ft.ControlEvent):
        self.delete(self)


class ComputersGroup(ft.Column):
    def __init__(
        self,
        app: "WoLApp",
    ):
        super().__init__()
        self.app = app
        self.base_info_text = "computer(s) added"

    def build(self):  # type: ignore
        self.new_name = ft.TextField(
            hint_text="Enter the name of the computer",
            on_submit=self.add_clicked,
            expand=True,
        )
        self.new_mac = ft.TextField(
            hint_text="Enter the MAC address of the computer",
            on_submit=self.add_clicked,
            expand=True,
        )
        self.computers = ft.Column()

        self.info_field = ft.Text()

        self.computers_tab = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.new_name,
                        self.new_mac,
                        ft.FloatingActionButton(
                            icon=ft.icons.ADD, on_click=self.add_clicked
                        ),
                    ],
                ),
                self.computers,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        self.info_field,
                    ],
                ),
            ],
            visible=True,
        )

        for key, val in settings.get_list("Computers").items():
            self.add_computer(key, val)

        self.info_field.value = f"{len(self.computers.controls)} {self.base_info_text}"

        return self.computers_tab

    def add_clicked(self, e: ft.ControlEvent):
        if self.new_name.value and self.new_mac.value:
            self.add_computer(
                self.new_name.value,
                self.new_mac.value,
            )
            self.new_name.value = ""
            self.new_mac.value = ""
            self.new_name.focus()
            self.update_info()

    def add_computer(self, name: str, mac_address: str):
        computer = Computer(
            name,
            mac_address,
            self.status_change,
            self.delete,
        )
        self.computers.controls.append(computer)
        settings.set(
            "Computers",
            name,
            mac_address,
        )

    def delete(self, computer: Computer):
        settings.remove("Computers", computer.name)
        self.computers.controls.remove(computer)
        self.update_info()

    def status_change(self):
        self.update_info()

    def update_info(self):
        self.info_field.value = f"{len(self.computers.controls)} {self.base_info_text}"
        self.update()
        super().update()
