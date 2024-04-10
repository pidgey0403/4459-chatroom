import curses
import threading

def draw_chat(stdscr, chat_client):
    k = 0
    input_text = ""
    max_input_length = 200  # Adjust the maximum length of the input text as needed

    threading.Thread(target=chat_client.receive_message,
                     args=(stdscr,), daemon=True).start()

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
        stdscr.refresh()
        height, width = stdscr.getmaxyx()

        if k == 10 and input_text != "":  # Handle Enter key press
            stdscr.clear()  # Clear the screen
            threading.Thread(target=chat_client.send_message,
                             args=(input_text,), daemon=True).start()
            stdscr.refresh()
            input_text = ""  # Clear the input text
        elif k == 127:  # Handle backspace key press
            input_text = input_text[:-1]  # Remove the last character
            # Clear the character on the screen
            stdscr.addch(height - 2, len("Enter your message: ") +
                         len(input_text), ' ')
        # Handle printable ASCII characters
        elif 32 <= k < 127 and len(input_text) < max_input_length:
            input_text += chr(k)

        # Declaration of strings
        title = f"Welcome {chat_client.username}, to Super Secret Chat!"[
            :width - 1]
        subtitle = "Written for CS4459B"[:width - 1]
        statusbarstr = "Press 'q' to exit"

        # Render title and subtitle
        stdscr.addstr(0, (width - len(title)) // 2, title)
        stdscr.addstr(1, (width - len(subtitle)) // 2, subtitle)

        # Render message
        message = "Enter your message: {}".format(input_text)[:width - 1]
        message_y = height - len(input_text.split('\n')) - 1
        stdscr.addstr(message_y, 0, message)

        # Render cursor next to the message prompt
        stdscr.move(message_y, len("Enter your message: ") + len(input_text))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height - 1, 0, statusbarstr)
        stdscr.addstr(height - 1, len(statusbarstr), " " *
                      (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()