import ctypes
import time
import math
from threading import Thread

# Nomes dos processos dos emuladores populares
PROCESS_NAMES = [
    "HD-Player.exe",      # BlueStacks / MSI App Player
    "dnplayer.exe",       # LDPlayer
    "MEmu.exe",           # MEmu
    "Nox.exe",            # NoxPlayer
    "SmartGaGa.exe",      # SmartGaGa
    "aow_exe.exe"         # GameLoop
]

MODULE_NAME = "GameAssembly.dll"

# Atenção: Substitua os offsets temporários abaixo pelos offsets reais da OB54!
OFFSET_ESP_BOX = 0x123456
OFFSET_ESP_LINE = 0x123457
OFFSET_ESP_NAME = 0x123458
OFFSET_ESP_DISTANCE = 0x123459
OFFSET_ESP_LIFE = 0x12345A
OFFSET_COMBAT_FOV = 0x12345B
OFFSET_COMBAT_AIMBOT = 0x12345C
OFFSET_COMBAT_SMOOTH = 0x12345D

# Constantes de Acesso do Windows
PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

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
        print("[*] Procurando emulador ativo...")
        process_id = self.get_process_id(PROCESS_NAMES)
        if not process_id:
            raise Exception("Processo do Free Fire (Emulador) nao encontrado. Certifique-se de que o jogo está aberto.")

        print(f"[+] Emulador encontrado! PID: {process_id}")
        self.process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, process_id)
        if not self.process_handle:
            raise Exception("Falha ao abrir processo (Execute como Administrador).")

        print("[*] Buscando endereço base da GameAssembly.dll...")
        self.module_base = self.get_module_base_address(process_id, MODULE_NAME)
        if not self.module_base:
            # Avisa, mas não impede a execução para que você possa depurar
            print("[-] ALERTA: 'GameAssembly.dll' nao foi encontrada ainda. O emulador pode estar carregando.")
        else:
            print(f"[+] GameAssembly.dll encontrada no endereço: {hex(self.module_base)}")

    def get_process_id(self, process_list):
        # Enumera os processos usando o Windows API de forma segura
        arr = (ctypes.c_ulong * 1024)()
        cbNeeded = ctypes.c_ulong()
        
        if not ctypes.windll.psapi.EnumProcesses(ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(cbNeeded)):
            return None
            
        number_of_processes = int(cbNeeded.value / ctypes.sizeof(ctypes.c_ulong()))
        
        for i in range(number_of_processes):
            pid = arr[i]
            if pid == 0:
                continue
                
            # Abre um handle temporário apenas para ler o nome do processo
            hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
            if hProcess:
                buffer = ctypes.create_string_buffer(256)
                ctypes.windll.psapi.GetModuleBaseNameA(hProcess, 0, buffer, 256)
                process_name_decoded = buffer.value.decode('utf-8', errors='ignore')
                ctypes.windll.kernel32.CloseHandle(hProcess) # Evita vazamento de memória
                
                # Compara o nome de forma case-insensitive contra a lista permitida
                for target_name in process_list:
                    if target_name.lower() in process_name_decoded.lower():
                        return pid
        return None

    def get_module_base_address(self, process_id, module_name):
        hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, process_id)
        if not hProcess:
            return None

        modules = (ctypes.c_void_p * 1024)()
        cbNeeded = ctypes.c_ulong()
        
        # LIST_MODULES_ALL = 0x03 (Garante compatibilidade com emuladores de 32 bits e 64 bits)
        if ctypes.windll.psapi.EnumProcessModulesEx(hProcess, ctypes.byref(modules), ctypes.sizeof(modules), ctypes.byref(cbNeeded), 0x03):
            number_of_modules = int(cbNeeded.value / ctypes.sizeof(ctypes.c_void_p))
            
            for i in range(number_of_modules):
                module_addr = modules[i]
                if not module_addr:
                    continue
                buffer = ctypes.create_string_buffer(256)
                ctypes.windll.psapi.GetModuleFileNameExA(hProcess, module_addr, buffer, 256)
                decoded_path = buffer.value.decode('utf-8', errors='ignore')
                
                if module_name.lower() in decoded_path.lower():
                    ctypes.windll.kernel32.CloseHandle(hProcess)
                    return module_addr
                    
        ctypes.windll.kernel32.CloseHandle(hProcess)
        return None

    def read_memory(self, address):
        if not self.process_handle:
            return 0
        buffer = ctypes.c_size_t() # Usando c_size_t evita bugs de 64 bits
        bytes_read = ctypes.c_size_t()
        ctypes.windll.kernel32.ReadProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            ctypes.byref(buffer),
            ctypes.sizeof(buffer),
            ctypes.byref(bytes_read)
        )
        return buffer.value

    def write_memory(self, address, value):
        if not self.process_handle:
            return
        buffer = ctypes.c_size_t(value)
        bytes_written = ctypes.c_size_t()
        ctypes.windll.kernel32.WriteProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            ctypes.byref(buffer),
            ctypes.sizeof(buffer),
            ctypes.byref(bytes_written)
        )

    def toggle_esp(self):
        if not self.module_base:
            return
        self.esp_enabled = not self.esp_enabled
        state = 1 if self.esp_enabled else 0
        print(f"[*] Definindo estado do ESP para: {state}")
        self.write_memory(self.module_base + OFFSET_ESP_BOX, state)
        self.write_memory(self.module_base + OFFSET_ESP_LINE, state)
        self.write_memory(self.module_base + OFFSET_ESP_NAME, state)
        self.write_memory(self.module_base + OFFSET_ESP_DISTANCE, state)
        self.write_memory(self.module_base + OFFSET_ESP_LIFE, state)

    def set_combat_fov(self, value):
        if not self.module_base:
            return
        if 0 <= value <= 500:
            self.combat_fov = value
            self.write_memory(self.module_base + OFFSET_COMBAT_FOV, value)

    def toggle_combat_aimbot(self):
        if not self.module_base:
            return
        self.combat_aimbot = not self.combat_aimbot
        state = 1 if self.combat_aimbot else 0
        print(f"[*] Definindo estado do Aimbot para: {state}")
        self.write_memory(self.module_base + OFFSET_COMBAT_AIMBOT, state)

    def set_combat_smooth(self, value):
        if not self.module_base:
            return
        if 0 <= value <= 100:
            self.combat_smooth = value
            self.write_memory(self.module_base + OFFSET_COMBAT_SMOOTH, value)

    def run(self):
        print("[+] Script rodando. Aguardando comandos ou alteracoes de estado...")
        while True:
            time.sleep(0.5)
            if self.process_handle and self.module_base:
                if self.esp_enabled:
                    self.read_memory(self.module_base + OFFSET_ESP_BOX)
                if self.combat_aimbot:
                    self.read_memory(self.module_base + OFFSET_COMBAT_AIMBOT)

if __name__ == "__main__":
    try:
        cheat = FreeFireOB54Cheat()
        cheat.attach_process()
        cheat.run()
    except Exception as e:
        print(f"\n[ERRO CRITICO]: {e}")
        input("\nPressione ENTER para fechar...") # Mantém o prompt aberto para você ler o erro
