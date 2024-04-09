import grpc
from concurrent import futures
import time
import chat_pb2
import chat_pb2_grpc

# Define the chat service


class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.messages = []

    def ChatStream(self, request_iterator, context):
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.messages) > lastindex:
                n = self.messages[lastindex]
                lastindex += 1
                yield n

    def SendMessage(self, request, context):
        self.messages.append(request)
        print(f"{request.username}: {request.message}")
        return chat_pb2.MessageResponse(username=request.username, message=request.message)


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
