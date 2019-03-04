class Message():

    def __init__(self, header="", body=""):
        self.header = header
        self.body = body

    @staticmethod
    def from_encoded(encoded):
        message = Message()
        decoded = encoded.decode()
        header, body = decoded.split("::::")
        message.header = header
        message.body = body

    def encode(self):
        data = self.header + "::::" + self.body
        return data.encode()