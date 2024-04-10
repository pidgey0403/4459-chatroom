import curses
import client as client
from frontend.draw_login import draw_login
from frontend.draw_chat import draw_chat


def main():
    username = curses.wrapper(draw_login)  # draw the login page UI
    # create the ChatClient server
    chat_client = client.ChatClient(username=username)
    # draw the chat page UI, and pass in the ChatClient
    curses.wrapper(draw_chat, chat_client)


if __name__ == "__main__":
    main()
