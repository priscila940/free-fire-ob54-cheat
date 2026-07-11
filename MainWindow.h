#pragma once
#include <Windows.h>
#include <string>

namespace FreeFireOB54Cheat {
    class MainWindow {
    public:
        MainWindow();
        ~MainWindow();

        void Show();
        void Hide();

    private:
        HWND hwnd;
        bool visible;

        // Message handlers
        static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);
        void OnPaint(HDC hdc);
        void OnCommand(int id);
        void OnTimer(WPARAM timerId);

        // Controls
        HWND espBoxCheck;
        HWND espLineCheck;
        HWND espNameCheck;
        HWND espDistanceCheck;
        HWND espLifeCheck;
        HWND combatFovSlider;
        HWND combatAimbotCheck;
        HWND combatSmoothSlider;
    };
}
