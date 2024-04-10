import grpc
from concurrent import futures
import time
import chat_pb2
import chat_pb2_grpc
from pymongo import MongoClient


# Define the chat service


class ChatService(chat_pb2_grpc.ChatServiceServicer):
    chatroom_id = 0
    
    def __init__(self):
        self.messages = []
        self.mongo_client = MongoClient('localhost', 27017)
        self.db = self.mongo_client.chat_db

    def ChatStream(self, request_iterator, context):
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.messages) > lastindex:
                n = self.messages[lastindex]
                lastindex += 1
                yield n
        
        # chat_history = self.get_chat_history()
        # while True:
        #     # Check if there are any new messages
        #     while len(chat_history) > lastindex:
        #         n = self.chat_history[lastindex]
        #         lastindex += 1
        #         yield n
                
                

    def SendMessage(self, request, context):
        self.messages.append(request)
        
        self.save_history(request)
        
        print(f"{request.username}: {request.message}")
        return chat_pb2.MessageResponse(username=request.username, message=request.message)

    def save_history(self, request):
        # Create a document to insert into MongoDB
        message_doc = {
            'message': request.message,
            'user': request.username,
        }
        
        # Insert the document into the chat collection
        self.db.messages.insert_one(message_doc)
        
    def get_chat_history(self):
        # Retrieve chat history from MongoDB
        chat_history = self.db.messages.find()

        # Convert MongoDB documents to message objects
        message_list = [chat_pb2.MessageResponse(
            username=message['user'],
            message=message['message'],
        ) for message in chat_history]

        return message_list

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
