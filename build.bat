@echo off
setlocal enabledelayedexpansion

:: Compile resources
windres resource.rc -o resource.res

:: Compile C++ files
g++ -Wall -O2 -mwindows -I. -c MainWindow.cpp -o MainWindow.obj
g++ -Wall -O2 -mwindows -I. -c main.cpp -o main.obj

:: Link
g++ -Wall -O2 -mwindows MainWindow.obj main.obj resource.res -o free_fire_ob54_cheat_panel.exe -lcomctl32

:: Clean up
del *.obj *.res

echo Build completed successfully!
