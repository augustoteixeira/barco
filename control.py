


import curses
stdscr = curses.initscr()


curses.noecho()
curses.cbreak()
stdscr.keypad(1)

stdscr.addstr(2, 30, "BARCO!!!")
stdscr.refresh()

def print 


while 1:
    c = stdscr.getch()
    if c == ord('p'):
        PrintDocument()
    elif c == ord('q'):
        break  # Exit the while()
    elif c == curses.KEY_HOME:
        x = y = 0


# terminating
curses.nocbreak(); stdscr.keypad(0); curses.echo()
curses.endwin()


