import contextlib
import ipaddress
import os
import socket
import subprocess
import threading
from queue import Queue
from typing import TYPE_CHECKING

import flet as ft
from app_settings import settings
from getmac import get_mac_address

if TYPE_CHECKING:
    from main import WoLApp


class Scan(ft.DataRow):
    def __init__(
        self,
        name: str,
        mac_address: str,
        ip_address: str,
        app: "WoLApp",
    ):
        super().__init__()
        self.name = name
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.app = app

        self.add_button = ft.IconButton(
            icon=ft.icons.ADD,
            on_click=self.add_clicked,
        )

        self.cells = [
            ft.DataCell(ft.Text(self.name)),
            ft.DataCell(ft.Text(self.ip_address)),
            ft.DataCell(ft.Text(self.mac_address)),
            ft.DataCell(self.add_button),
        ]

    def add_clicked(self, e: ft.ControlEvent):
        self.add_button.icon = ft.icons.DONE
        self.add_button.disabled = True
        self.update()
        self.app.computers_tab.add_computer(self.name, self.mac_address)


class ScansGroup(ft.Column):
    def __init__(
        self,
        app: "WoLApp",
    ):
        super().__init__()
        self.app = app
        self.base_info_text = "computer(s) found"

        self.local_mac_address = get_mac_address()
        self.local_ip_address = str(self.get_local_ip_address())

        self.net_addr: str
        self.ip_net: ipaddress.IPv4Network | ipaddress.IPv6Network
        self.all_hosts: list[ipaddress.IPv4Address | ipaddress.IPv6Address]

        # Configure subprocess to hide the console window (for Windows)
        with contextlib.suppress(Exception):
            self.info = subprocess.STARTUPINFO()
            self.info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.info.wShowWindow = subprocess.SW_HIDE

        self.print_lock = threading.Lock()
        self.queue = Queue()

    def build(self):  # type: ignore
        self.scans: list[ft.DataRow] = []

        self.scan_button = ft.OutlinedButton(
            text="Scan",
            on_click=self.scan_clicked,
        )
        self.progressbar = ft.Row()

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Host name")),
                ft.DataColumn(ft.Text("IP")),
                ft.DataColumn(ft.Text("Mac Address")),
                ft.DataColumn(ft.Text("Add")),
            ],
            rows=self.scans,
        )

        self.info_field = ft.Text()
        self.info_field.value = f"{len(self.scans)} {self.base_info_text}"

        self.scans_tab = ft.Column(
            controls=[
                ft.Row(
                    [
                        self.scan_button,
                        self.progressbar,
                    ]
                ),
                # self.scans,
                ft.Row(controls=[self.data_table]),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[self.info_field],
                ),
            ],
            # expand=True,
        )
        return self.scans_tab

    def scan_clicked(self, e: ft.ControlEvent) -> None:
        self.net_addr = settings.ip_range
        self.ip_net = ipaddress.ip_network(self.net_addr)
        self.all_hosts: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = list(
            self.ip_net.hosts()
        )
        print(self.net_addr)

        self.scans.clear()
        self.set_progressbar(True)

        # Enqueue all host IPs for scanning
        for ip in self.all_hosts:
            self.queue.put(str(ip))

        # Start worker threads (up to 100 threads)
        threads: list[threading.Thread] = []
        for _ in range(100):
            t = threading.Thread(target=self.threader)
            t.daemon = True
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.set_progressbar(False)

    def set_progressbar(self, status: bool):
        self.progressbar.controls = [ft.ProgressRing()] if status else []
        self.scan_button.disabled = status
        self.scan_button.text = "Scanning" if status else "Scan"
        self.update_info()

    def threader(self):
        while not self.queue.empty():
            ip = self.queue.get()
            self.pingsweep(ip)
            self.queue.task_done()

    # Function to get the local IP address of the machine
    def get_local_ip_address(self):
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Connect to any remote address and get the socket's local address
            s.connect(("8.8.8.8", 80))
            local_ip_address = s.getsockname()[0]
        except Exception as e:
            print(f"Error: {e}")
            local_ip_address = None
        finally:
            s.close()

        return local_ip_address

        # Function to perform ping sweep for a given IP address

    def pingsweep(self, ip: str):
        # Define ping parameters based on operating system
        ping_params = (
            ["-n", "1", "-w", "150"] if os.name == "nt" else ["-c", "1", "-W", "1"]
        )

        ping = "ping" if os.name == "nt" else "/bin/ping"

        # Execute ping command
        output = subprocess.Popen(
            [ping] + ping_params + [ip],
            stdout=subprocess.PIPE,
            startupinfo=self.info if os.name == "nt" else None,
        ).communicate()[0]

        # Process ping output
        with self.print_lock:
            if "Reply" in output.decode("utf-8") or "icmp_seq" in output.decode(
                "utf-8"
            ):
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except socket.herror:
                    hostname = ""
                if ip == self.local_ip_address:
                    mac_address = self.local_mac_address
                else:
                    mac_address = get_mac_address(ip=ip)
                self.create_scan(hostname, str(mac_address), ip)
            elif "Destination host unreachable" in output.decode("utf-8"):
                pass
            elif "Request timed out" not in output.decode("utf-8"):
                print("UNKNOWN")

    def create_scan(
        self,
        name: str,
        mac_address: str,
        ip: str,
    ):
        self.scans.append(
            Scan(
                name,
                mac_address,
                ip,
                self.app,
            )
        )
        self.update_info()

    def update_info(self):
        self.info_field.value = f"{len(self.scans)} {self.base_info_text}"
        self.update()
        super().update()
