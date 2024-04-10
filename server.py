import grpc
import time

from pymongo import MongoClient
from concurrent import futures

import chat_pb2
import chat_pb2_grpc


class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        # initialize MongoDB client and database
        self.mongo_client = MongoClient('localhost', 27017)
        self.db = self.mongo_client.chat_db

    def ChatStream(self, request_iterator, context):
        lastindex = 0  # initialize to the length of chat history

        # open a continual ChatStream for every connected client
        while True:
            # Check if there are any new messages
            while len(self.get_chat_history()) > lastindex:
                message = self.get_chat_history()[lastindex]
                lastindex += 1
                yield message

    def SendMessage(self, request, context):
        # save incoming messages to the MongoDB database
        self.save_history(request)
        # simple server-side logging
        print(f"{request.username}: {request.message}")

        # return MessageResponse acknowledgment to the client
        return chat_pb2.MessageResponse(username=request.username, message=request.message)

    def save_history(self, request):
        # create a document to insert into MongoDB
        message_doc = {
            'message': request.message,
            'user': request.username,
        }

        # I\insert the document into the MongoDB 'chat' collection
        self.db.messages.insert_one(message_doc)

    def get_chat_history(self):
        # retrieve chat history from MongoDB
        chat_history = self.db.messages.find()

        # convert MongoDB documents to MessageResponse object list
        message_list = [chat_pb2.MessageResponse(
            username=message['user'],
            message=message['message'],
        ) for message in chat_history]

        return message_list


def serve():
    # initialize the grpc server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=11))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()

    print("Server started")
    try:
        while True:
            time.sleep(86400)  # keep the server running
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
