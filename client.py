import curses
import grpc
import chat_pb2
import chat_pb2_grpc
from google.protobuf.empty_pb2 import Empty


class ChatClient:
    def __init__(self, username):
        # initialize the grpc client
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.username = username

    def send_message(self, message):
        # send a MessageRequest to the chat server
        self.stub.SendMessage(chat_pb2.MessageRequest(
            username=self.username, message=message))

    def receive_message(self, stdscr):
        curses.curs_set(0)  # Curses UI - set the cursor to invisible

        messages = []  # Store received messages
        for message in self.stub.ChatStream(Empty()):
            messages.append(f"{message.username}: {message.message}")

            # display received messages in the UI between title and status bar
            max_display_lines = curses.LINES - 4
            display_start_y = 2  # start displaying messages below title and subtitle

            # calculate starting index based on messages count and screen size
            start_index = max(0, len(messages) - max_display_lines)
            for i, msg_index in enumerate(range(start_index, len(messages))):
                stdscr.move(display_start_y + i, 0)
                stdscr.clrtoeol()  # Clear the current line
                stdscr.addstr(display_start_y + i, 0, messages[msg_index])

            # Curses UI - refresh the screen
            stdscr.refresh()
