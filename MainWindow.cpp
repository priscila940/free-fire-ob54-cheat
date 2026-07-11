#include "MainWindow.h"
#include <CommCtrl.h>
#include <tchar.h>

#define IDC_ESP_BOX 1001
#define IDC_ESP_LINE 1002
#define IDC_ESP_NAME 1003
#define IDC_ESP_DISTANCE 1004
#define IDC_ESP_LIFE 1005
#define IDC_COMBAT_FOV 1010
#define IDC_COMBAT_AIMBOT 1011
#define IDC_COMBAT_SMOOTH 1012

namespace FreeFireOB54Cheat {
    MainWindow::MainWindow() : visible(false) {
        WNDCLASSEX wcex = {};
        wcex.cbSize = sizeof(WNDCLASSEX);
        wcex.lpfnWndProc = WndProc;
        wcex.hInstance = GetModuleHandle(NULL);
        wcex.lpszClassName = _T("FreeFireOB54CheatPanel");
        RegisterClassEx(&wcex);

        hwnd = CreateWindow(_T("FreeFireOB54CheatPanel"), _T("Free Fire OB54 Cheat"),
                          WS_OVERLAPPEDWINDOW | WS_VISIBLE, CW_USEDEFAULT, CW_USEDEFAULT,
                          300, 250, NULL, NULL, GetModuleHandle(NULL), this);
    }

    MainWindow::~MainWindow() {
        DestroyWindow(hwnd);
    }

    void MainWindow::Show() {
        ShowWindow(hwnd, SW_SHOW);
        UpdateWindow(hwnd);
        visible = true;
    }

    void MainWindow::Hide() {
        ShowWindow(hwnd, SW_HIDE);
        visible = false;
    }

    LRESULT CALLBACK MainWindow::WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
        MainWindow* self = (MainWindow*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
        if (!self && msg != WM_CREATE) return DefWindowProc(hwnd, msg, wParam, lParam);

        switch (msg) {
        case WM_CREATE:
            self = ((CREATESTRUCT*)lParam)->lpCreateParams;
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)self);
            return 0;
        case WM_COMMAND:
            self->OnCommand(wParam & 0xFFFF);
            return 0;
        case WM_HSCROLL:
            self->OnCommand(GetDlgCtrlID((HWND)lParam));
            return 0;
        case WM_TIMER:
            self->OnTimer(wParam);
            return 0;
        case WM_PAINT:
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            self->OnPaint(hdc);
            EndPaint(hwnd, &ps);
            return 0;
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
        }
        return DefWindowProc(hwnd, msg, wParam, lParam);
    }

    void MainWindow::OnPaint(HDC hdc) {
        RECT rect;
        GetClientRect(hwnd, &rect);

        FillRect(hdc, &rect, (HBRUSH)(COLOR_WINDOW+1));

        // Draw controls
        TextOut(hdc, 10, 10, _T("ESP Settings:"), 11);
        CheckDlgButton(hwnd, IDC_ESP_BOX, BST_CHECKED);
        CheckDlgButton(hwnd, IDC_ESP_LINE, BST_CHECKED);
        CheckDlgButton(hwnd, IDC_ESP_NAME, BST_CHECKED);
        CheckDlgButton(hwnd, IDC_ESP_DISTANCE, BST_CHECKED);
        CheckDlgButton(hwnd, IDC_ESP_LIFE, BST_CHECKED);

        TextOut(hdc, 10, 100, _T("Combat Settings:"), 14);
        CheckDlgButton(hwnd, IDC_COMBAT_AIMBOT, BST_CHECKED);
        SendDlgItemMessage(hwnd, IDC_COMBAT_FOV, TBM_SETRANGE, TRUE, MAKELONG(0, 500));
        SendDlgItemMessage(hwnd, IDC_COMBAT_FOV, TBM_SETPOS, TRUE, 250);
        SendDlgItemMessage(hwnd, IDC_COMBAT_SMOOTH, TBM_SETRANGE, TRUE, MAKELONG(0, 100));
        SendDlgItemMessage(hwnd, IDC_COMBAT_SMOOTH, TBM_SETPOS, TRUE, 50);
    }

    void MainWindow::OnCommand(int id) {
        switch (id) {
        case IDC_ESP_BOX:
        case IDC_ESP_LINE:
        case IDC_ESP_NAME:
        case IDC_ESP_DISTANCE:
        case IDC_ESP_LIFE:
            // Handle ESP checkboxes
            break;
        case IDC_COMBAT_AIMBOT:
            // Handle Aimbot checkbox
            break;
        case IDC_COMBAT_FOV:
            // Handle FOV slider
            break;
        case IDC_COMBAT_SMOOTH:
            // Handle Smoothness slider
            break;
        }
    }

    void MainWindow::OnTimer(WPARAM timerId) {
        // Timer handler
    }
}
