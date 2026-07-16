import tkinter as tk
from tkinter import ttk

# Definições de tipos da API do Windows para o ctypes
WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

def buscar_emulador_dinamico():
    """
    Percorre todas as janelas abertas no Windows para encontrar
    um emulador ativo e retorna o PID (Process ID) dele.
    """
    palavras_chave = ["bluestacks", "ldplayer", "memu", "nox", "smartgaga", "gameloop", "mumu"]
    resultado = {"pid": None, "nome_janela": None}

    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                titulo_janela = buff.value.lower()
                
                # Verifica se o título da janela contém alguma das palavras-chave
                for palavra in palavras_chave:
                    if palavra in titulo_janela:
                        pid = ctypes.c_ulong()
                        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                        resultado["pid"] = pid.value
                        resultado["nome_janela"] = buff.value
                        return False  # Para a busca ao encontrar a primeira correspondência
        return True

    # Enumera as janelas chamando a função para cada uma
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(foreach_window), 0)
    
    return resultado["pid"], resultado["nome_janela"]


MODULE_NAME = "GameAssembly.dll"

# Offsets e constantes originais informados por você
LOCAL_ROOT = 0x0
LOCAL_PELVIS = 0x2
LOCAL_NECK = 0x5
LOCAL_HEAD = 0x8
OFFSET_LOCAL_PLAYER = 0xABFF3C0
OFFSET_PLAYER_MODEL = 0x1A8
OFFSET_BONE_MATRIX = 0x2C
OFFSET_ESP_COLOR = 0x12345E
OFFSET_ESP_SIZE = 0x12345F
OFFSET_COMBAT_FOV = 0x12345B
OFFSET_COMBAT_AIMBOT = LOCAL_HEAD
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
        self.esp_color = 0xFFFFFF
        self.esp_size = 1
        self.combat_fov = 0
        self.combat_aimbot = False
        self.combat_smooth = 0

    def attach_process(self):
        print("[*] Procurando emulador ativo...")
        
        # Correção da busca: chama a nova busca dinâmica de janelas
        process_id, nome_janela = buscar_emulador_dinamico()
        
        if not process_id:
            raise Exception("Processo do Free Fire (Emulador) nao encontrado. Certifique-se de que o jogo está aberto.")

        print(f"[+] Emulador encontrado! Janela: '{nome_janela}' | PID: {process_id}")
        self.process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, process_id)
        if not self.process_handle:
            raise Exception("Falha ao abrir processo (Execute como Administrador).")

        print("[*] Buscando endereço base da GameAssembly.dll...")
        self.module_base = self.get_module_base_address(process_id, MODULE_NAME)
        if not self.module_base:
            print("[-] ALERTA: 'GameAssembly.dll' nao foi encontrada ainda. O emulador pode estar carregando.")
        else:
            print(f"[+] GameAssembly.dll encontrada no endereço: {hex(self.module_base)}")

    def get_module_base_address(self, process_id, module_name):
        hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, process_id)
        if not hProcess:
            return None

        modules = (ctypes.c_void_p * 1024)()
        cbNeeded = ctypes.c_ulong()
        
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
        buffer = ctypes.c_size_t()
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
        # Alinhamento e indentação corrigidos com 8 espaços internos
        self.esp_enabled = not self.esp_enabled
        state = 1 if self.esp_enabled else 0
        print(f"[*] Definindo estado do ESP para: {state}")
        self.write_memory(self.module_base + LOCAL_ROOT, state)
        self.write_memory(self.module_base + LOCAL_PELVIS, state)
        self.write_memory(self.module_base + LOCAL_NECK, state)
        self.write_memory(self.module_base + LOCAL_HEAD, state)

    def set_esp_color(self, color):
        if not self.module_base:
            return
        self.esp_color = color
        self.write_memory(self.module_base + OFFSET_ESP_COLOR, color)

    def set_esp_size(self, size):
        if not self.module_base:
            return
        self.esp_size = size
        self.write_memory(self.module_base + OFFSET_ESP_SIZE, size)

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
                    self.read_memory(self.module_base + LOCAL_ROOT)
                    self.read_memory(self.module_base + LOCAL_PELVIS)
                    self.read_memory(self.module_base + LOCAL_NECK)
                    self.read_memory(self.module_base + LOCAL_HEAD)
                    self.read_memory(self.module_base + OFFSET_ESP_COLOR)
                    self.read_memory(self.module_base + OFFSET_ESP_SIZE)
                if self.combat_aimbot:
                    self.read_memory(self.module_base + OFFSET_COMBAT_AIMBOT)

class ConfigPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurações do Free Fire OB54")
        self.root.geometry("400x300")

        # Cria os widgets do painel de configurações
        self.esp_enabled = tk.BooleanVar()
        self.esp_enabled.set(False)
        self.esp_enabled_checkbutton = ttk.Checkbutton(root, text="ESP Ativado", variable=self.esp_enabled)
        self.esp_enabled_checkbutton.pack(pady=10)

        self.esp_color_label = ttk.Label(root, text="Cor do ESP:")
        self.esp_color_label.pack(pady=5)
        self.esp_color_entry = ttk.Entry(root)
        self.esp_color_entry.pack(pady=5)

        self.esp_size_label = ttk.Label(root, text="Tamanho do ESP:")
        self.esp_size_label.pack(pady=5)
        self.esp_size_entry = ttk.Entry(root)
        self.esp_size_entry.pack(pady=5)

        self.combat_fov_label = ttk.Label(root, text="FOV do Combate:")
        self.combat_fov_label.pack(pady=5)
        self.combat_fov_entry = ttk.Entry(root)
        self.combat_fov_entry.pack(pady=5)

        self.combat_aimbot_enabled = tk.BooleanVar()
        self.combat_aimbot_enabled.set(False)
        self.combat_aimbot_enabled_checkbutton = ttk.Checkbutton(root, text="Aimbot Ativado", variable=self.combat_aimbot_enabled)
        self.combat_aimbot_enabled_checkbutton.pack(pady=10)

        self.combat_smooth_label = ttk.Label(root, text="Suavização do Aimbot:")
        self.combat_smooth_label.pack(pady=5)
        self.combat_smooth_entry = ttk.Entry(root)
        self.combat_smooth_entry.pack(pady=5)

        # Botão para salvar as configurações
        self.save_button = ttk.Button(root, text="Salvar Configurações", command=self.save_config)
        self.save_button.pack(pady=10)

    def save_config(self):
        # Salva as configurações do painel
        print(f"ESP Ativado: {self.esp_enabled.get()}")
        print(f"Cor do ESP: {self.esp_color_entry.get()}")
        print(f"Tamanho do ESP: {self.esp_size_entry.get()}")
        print(f"FOV do Combate: {self.combat_fov_entry.get()}")
        print(f"Aimbot Ativado: {self.combat_aimbot_enabled.get()}")
        print(f"Suavização do Aimbot: {self.combat_smooth_entry.get()}")

if __name__ == "__main__":
    root = tk.Tk()
    panel = ConfigPanel(root)
    root.mainloop()
