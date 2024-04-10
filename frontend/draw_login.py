import curses
import sys

def draw_login(stdscr):
    max_input_length = 20  # Adjust the maximum length of the input text as needed

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    height, width = stdscr.getmaxyx()
    title = "Login to Super Secret Chat"[
            :width - 1]
    stdscr.addstr(0, (width - len(title)) // 2, title)

    # Ask for username
    stdscr.addstr(2, 0, "Username: ")
    curses.echo()  # Turn on echoing to show user input
    username = stdscr.getstr(2, len(
        "Username: "), max_input_length).decode(encoding="utf-8")
    curses.noecho()  # Turn off echoing

    if username == 'q':
        sys.exit()

    # Ask for password
    stdscr.addstr(3, 0, "Password: ")
    password = stdscr.getstr(3, len(
        "Password: "), max_input_length).decode(encoding="utf-8")

    if password == 'q':
        sys.exit()

    # Cleanup
    curses.endwin()

    return username