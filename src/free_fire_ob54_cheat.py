import ctypes
import time
import math
from threading import Thread

# Memory addresses and offsets for Free Fire OB54
PROCESS_NAME = [
    "HD-Player.exe",      # BlueStacks / MSI App Player
    "dnplayer.exe",       # LDPlayer
    "MEmu.exe",           # MEmu
    "Nox.exe",            # NoxPlayer
    "SmartGaGa.exe",      # SmartGaGa
    "aow_exe.exe"         # GameLoop
]
MODULE_NAME = "GameAssembly.dll"
OFFSET_ESP_BOX = 0x123456
OFFSET_ESP_LINE = 0x123457
OFFSET_ESP_NAME = 0x123458
OFFSET_ESP_DISTANCE = 0x123459
OFFSET_ESP_LIFE = 0x12345A
OFFSET_COMBAT_FOV = 0x12345B
OFFSET_COMBAT_AIMBOT = 0x12345C
OFFSET_COMBAT_SMOOTH = 0x12345D

class FreeFireOB54Cheat:
    def __init__(self):
        self.process_handle = None
        self.module_base = None
        self.esp_enabled = False
        self.esp_box = False
        self.esp_line = False
        self.esp_name = False
        self.esp_distance = False
        self.esp_life = False
        self.combat_fov = 0
        self.combat_aimbot = False
        self.combat_smooth = 0

    def attach_process(self):
        # Attach to the Free Fire process
        process_id = self.get_process_id(PROCESS_NAME)
        if not process_id:
            raise Exception("Free Fire process not found.")
        
        self.process_handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, process_id)
        if not self.process_handle:
            raise Exception("Failed to open process.")
        
        # Get module base address
        self.module_base = self.get_module_base_address(process_id, MODULE_NAME)

    def get_process_id(self, process_name):
        # Find the process ID by name
        processes = []
        for pid in range(1, 10000):
            try:
                hProcess = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
                if hProcess:
                    ctypes.windll.kernel32.CloseHandle(hProcess)
                    processes.append(pid)
            except:
                pass
        
        for pid in processes:
            try:
                hProcess = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
                if hProcess:
                    buffer = ctypes.create_string_buffer(256)
                    ctypes.windll.psapi.GetModuleBaseNameA(hProcess, 0, buffer, 256)
                    if process_name in buffer.value.decode():
                        ctypes.windll.kernel32.CloseHandle(hProcess)
                        return pid
                    ctypes.windll.kernel32.CloseHandle(hProcess)
            except:
                pass
        return None

    def get_module_base_address(self, process_id, module_name):
        # Get the base address of a loaded module
        modules = []
        for _ in range(100):
            modules.append(ctypes.c_ulong())
        
        bytes_read = ctypes.c_ulong()
        ctypes.windll.psapi.EnumProcessModulesEx(
            ctypes.windll.kernel32.OpenProcess(0x1000, False, process_id),
            ctypes.byref(modules[0]),
            ctypes.sizeof(modules[0]) * len(modules),
            ctypes.byref(bytes_read),
            3
        )
        
        for module in modules:
            if module.value == 0:
                continue
            module_name_buffer = ctypes.create_string_buffer(256)
            ctypes.windll.psapi.GetModuleFileNameExA(
                ctypes.windll.kernel32.OpenProcess(0x1000, False, process_id),
                module.value,
                module_name_buffer,
                256
            )
            if module_name in module_name_buffer.value.decode():
                return module.value
        return None

    def read_memory(self, address):
        # Read memory from the process
        buffer = ctypes.c_ulong()
        ctypes.windll.kernel32.ReadProcessMemory(
            self.process_handle,
            address,
            ctypes.byref(buffer),
            ctypes.sizeof(buffer),
            ctypes.byref(ctypes.c_ulong())
        )
        return buffer.value

    def write_memory(self, address, value):
        # Write memory to the process
        ctypes.windll.kernel32.WriteProcessMemory(
            self.process_handle,
            address,
            ctypes.byref(ctypes.c_ulong(value)),
            ctypes.sizeof(ctypes.c_ulong()),
            ctypes.byref(ctypes.c_ulong())
        )

    def toggle_esp(self):
        # Toggle ESP on/off
        self.esp_enabled = not self.esp_enabled
        if self.esp_enabled:
            self.write_memory(self.module_base + OFFSET_ESP_BOX, 1)
            self.write_memory(self.module_base + OFFSET_ESP_LINE, 1)
            self.write_memory(self.module_base + OFFSET_ESP_NAME, 1)
            self.write_memory(self.module_base + OFFSET_ESP_DISTANCE, 1)
            self.write_memory(self.module_base + OFFSET_ESP_LIFE, 1)
        else:
            self.write_memory(self.module_base + OFFSET_ESP_BOX, 0)
            self.write_memory(self.module_base + OFFSET_ESP_LINE, 0)
            self.write_memory(self.module_base + OFFSET_ESP_NAME, 0)
            self.write_memory(self.module_base + OFFSET_ESP_DISTANCE, 0)
            self.write_memory(self.module_base + OFFSET_ESP_LIFE, 0)

    def set_combat_fov(self, value):
        # Set FOV value (0-500)
        if 0 <= value <= 500:
            self.combat_fov = value
            self.write_memory(self.module_base + OFFSET_COMBAT_FOV, value)

    def toggle_combat_aimbot(self):
        # Toggle Aimbot on/off
        self.combat_aimbot = not self.combat_aimbot
        if self.combat_aimbot:
            self.write_memory(self.module_base + OFFSET_COMBAT_AIMBOT, 1)
        else:
            self.write_memory(self.module_base + OFFSET_COMBAT_AIMBOT, 0)

    def set_combat_smooth(self, value):
        # Set Aimbot smoothness (0-100)
        if 0 <= value <= 100:
            self.combat_smooth = value
            self.write_memory(self.module_base + OFFSET_COMBAT_SMOOTH, value)

    def run(self):
        # Main thread loop
        while True:
            time.sleep(0.1)
            if self.esp_enabled:
                self.read_memory(self.module_base + OFFSET_ESP_BOX)
                self.read_memory(self.module_base + OFFSET_ESP_LINE)
                self.read_memory(self.module_base + OFFSET_ESP_NAME)
                self.read_memory(self.module_base + OFFSET_ESP_DISTANCE)
                self.read_memory(self.module_base + OFFSET_ESP_LIFE)
            if self.combat_aimbot:
                self.read_memory(self.module_base + OFFSET_COMBAT_AIMBOT)

if __name__ == "__main__":
    cheat = FreeFireOB54Cheat()
    cheat.attach_process()
    cheat.run()
