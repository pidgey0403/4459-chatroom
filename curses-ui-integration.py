import curses
import grpc
import chat_pb2
import chat_pb2_grpc
import threading
from google.protobuf.empty_pb2 import Empty
import sys


class ChatClient:
    def __init__(self, username):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.username = username

    def send_message(self, message):
        self.stub.SendMessage(chat_pb2.MessageRequest(
            username=self.username, message=message))

    def receive_message(self, stdscr):
        curses.curs_set(0)

        messages = []  # Store received messages
        for message in self.stub.ChatStream(Empty()):
            messages.append(f"{message.username}: {message.message}")

            # Display received messages in the UI between title and status bar
            max_display_lines = curses.LINES - 4
            display_start_y = 2  # Start displaying messages below title and subtitle

            # Calculate starting index based on messages count and screen size
            start_index = max(0, len(messages) - max_display_lines)
            for i, msg_index in enumerate(range(start_index, len(messages))):
                stdscr.move(display_start_y + i, 0)
                stdscr.clrtoeol()  # Clear the current line
                stdscr.addstr(display_start_y + i, 0, messages[msg_index])

            # Refresh the screen
            stdscr.refresh()


def draw_chat(stdscr, chat_client):
    k = 0
    input_text = ""
    max_input_length = 200  # Adjust the maximum length of the input text as needed

    threading.Thread(target=chat_client.receive_message,
                     args=(stdscr,), daemon=True).start()

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

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


def draw_login(stdscr):
    max_input_length = 20  # Adjust the maximum length of the input text as needed

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Ask for username
    stdscr.addstr(0, 0, "Enter your username (hit 'q' to quit): ")
    curses.echo()  # Turn on echoing to show user input
    username = stdscr.getstr(0, len(
        "Enter your username (hit 'q' to quit): "), max_input_length).decode(encoding="utf-8")
    curses.noecho()  # Turn off echoing
    if username == 'q':
        sys.exit()

    # Display user input
    stdscr.clear()
    stdscr.addstr(0, 0, f"Hello, {username}!")
    stdscr.refresh()

    # Cleanup
    curses.endwin()

    return username


def main():
    username = curses.wrapper(draw_login)
    chat_client = ChatClient(username=username)
    curses.wrapper(draw_chat, chat_client)


if __name__ == "__main__":
    main()
