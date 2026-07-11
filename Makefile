CC = g++
CFLAGS = -Wall -O2 -mwindows
INCLUDES = -I.
LIBS = -lcomctl32

all: free_fire_ob54_cheat_panel.exe

%.obj: %.cpp
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

free_fire_ob54_cheat_panel.exe: MainWindow.obj main.obj resource.res
	$(CC) $(CFLAGS) $(INCLUDES) $^ -o $@ $(LIBS)

clean:
	del *.obj *.exe *.res

.PHONY: all clean
