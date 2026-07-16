import ctypes
import time
import threading
import dearpygui.dearpygui as dpg

# Variáveis globais de controle
MENU_ABERTO = True
TECLA_MENU = 0x2D  # Tecla INSERT por padrão (Virtual Key Code)
STREAM_MODE = False

# Constantes do Windows para o Stream Mode
HWND_TOPMOST = -1
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WDA_NONE = 0x00000000
WDA_EXCLUDE = 0x00000003

def aplicar_stream_mode(estado):
    """
    Ativa ou desativa a ocultação da janela em programas de gravação (OBS/Discord).
    """
    global STREAM_MODE
    STREAM_MODE = estado
    # Obtém o identificador (HWND) da janela do Dear PyGui
    hwnd = ctypes.windll.user32.FindWindowW(None, "Painel de Configurações")
    if hwnd:
        if STREAM_MODE:
            # Exclui a janela de capturas de tela e gravação
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDE)
            print("[*] Stream Mode: ATIVADO (Invisível no OBS)")
        else:
            # Volta ao estado normal (visível para todos)
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_NONE)
            print("[*] Stream Mode: DESATIVADO")

def monitorar_teclado():
    """
    Roda em segundo plano monitorando a tecla configurada para abrir/fechar o menu.
    """
    global MENU_ABERTO, TECLA_MENU
    while True:
        # GetAsyncKeyState detecta se a tecla está pressionada no Windows globalmente
        if ctypes.windll.user32.GetAsyncKeyState(TECLA_MENU) & 1:
            MENU_ABERTO = not MENU_ABERTO
            if MENU_ABERTO:
                dpg.show_item("janela_principal")
            else:
                dpg.hide_item("janela_principal")
        time.sleep(0.1)

# Inicializa o Dear PyGui
dpg.create_context()

# Configuração visual do Menu
with dpg.window(label="Painel de Controle", width=450, height=350, no_collapse=True, tag="janela_principal"):
    
    # Barra de abas
    with dpg.tab_bar():
        
        # ABA 1: COMBATE
        with dpg.tab(label="Combate"):
            dpg.add_text("Configurações de Combate")
            dpg.add_checkbox(label="Ativar Aimbot", default_value=False)
            dpg.add_slider_float(label="Aimbot FOV", default_value=50.0, min_value=0.0, max_value=180.0)
            dpg.add_slider_int(label="Suavização (Smooth)", default_value=5, min_value=1, max_value=20)
            
        # ABA 2: ESP
        with dpg.tab(label="ESP"):
            dpg.add_text("Configurações de Visualização (ESP)")
            dpg.add_checkbox(label="Ativar ESP", default_value=False)
            dpg.add_checkbox(label="Desenhar Box (Caixa)", default_value=False)
            dpg.add_checkbox(label="Desenhar Linhas (Lines)", default_value=False)
            dpg.add_color_edit(label="Cor do ESP", default_value=[255, 255, 255, 255])

        # ABA 3: CONFIGURAÇÕES (Teclas e Stream Mode)
        with dpg.tab(label="Configurações"):
            dpg.add_text("Ajustes do Painel")
            
            # Atalho de teclado
            dpg.add_combo(
                label="Tecla para Abrir/Fechar", 
                items=["INSERT", "F9", "HOME", "DELETE"], 
                default_value="INSERT",
                callback=lambda sender, app_data: atualizar_tecla_atalho(app_data)
            )
            
            dpg.add_separator()
            
            # Chave Liga/Desliga do Stream Mode
            dpg.add_checkbox(
                label="Ativar Stream Mode (Ocultar no OBS)", 
                default_value=False,
                callback=lambda sender, app_data: aplicar_stream_mode(app_data)
            )

def atualizar_tecla_atalho(nome_tecla):
    """
    Atualiza o código da tecla com base na escolha do usuário no Combo Box.
    """
    global TECLA_MENU
    mapeamento = {
        "INSERT": 0x2D,
        "F9": 0x78,
        "HOME": 0x24,
        "DELETE": 0x2E
    }
    TECLA_MENU = mapeamento.get(nome_tecla, 0x2D)
    print(f"[*] Tecla de atalho alterada para: {nome_tecla}")

# Configura o tamanho da janela do aplicativo e exibe
dpg.create_viewport(title="Painel de Configurações", width=480, height=380, decorated=True)
dpg.setup_dearpygui()
dpg.show_viewport()

# Inicia a thread que ouve as teclas em segundo plano
thread_teclado = threading.Thread(target=monitorar_teclado, daemon=True)
thread_teclado.start()

# Loop principal de renderização da interface
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()
