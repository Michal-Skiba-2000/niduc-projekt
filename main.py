from PIL import Image

image = Image.open("buchal.jpg")
image.show()

for y in range(image.height):
    for x in range(image.width):
        print(image.getpixel((x,y)))

#an_int = 15
#a_bytes = str(bin(an_int))[2:]
#print(a_bytes)
import random

class Channel():

    def __init__(self, s, r, noise_rate = 0.1):
        self.sender = s;
        self.receiver = r
        self.noise_rate = noise_rate

    def communicate(self):
        msg = self.sender.get_encoded_msg()
        msg = self._noise(msg)
        self.receiver.receive_msg(msg)

    def _noise(self, msg):

        new_msg = []

        for bit in msg:
            rand_int = random.randint(1, 100001)
            if rand_int <= 100001*self.noise_rate:
                if bit == 0:
                    new_msg.append(1)
                else:
                    new_msg.append(0)
            else:
                new_msg.append(bit)

        print("Noised message:   " + str(new_msg))

        return new_msg


class Sender():

    def __init__(self, encode_method):
        msg = []
        for i in range(8):
            msg.append(random.randint(0, 1))

        self.msg = msg
        self.encode_method = encode_method

    def get_encoded_msg(self):

        msg = None
        if self.encode_method == "triple": msg = self._triple_msg()

        return msg

    def _triple_msg(self):
        encoded_msg = []

        for bit in self.msg:
            for i in range(3):
                encoded_msg.append(bit)

        print("Encoded message:  " + str(encoded_msg))
        return encoded_msg


    def print_msg(self):
        print("Message to send:  " + str(self.msg))


class Receiver():

    def __init__(self, decode_method):
        self.received_msg = ""
        self.decode_method = decode_method

    def receive_msg(self, msg):

        if self.decode_method == "triple": msg = self._triple_decode(msg)

        self.received_msg = msg

    def print_received_msg(self):
        print("Received message: " + str(self.received_msg))

    def _triple_decode(self, msg):

        length = len(msg)

        new_msg = []

        for i in range(0, length, 3):
            if msg[i] == msg[i+1] or msg[i] == msg[i+2]: new_msg.append(msg[i])
            elif msg[i+1] == msg[i+2]: new_msg.append(msg[i+2])

        return new_msg

coding_method = "triple"

s = Sender(coding_method)
r = Receiver(coding_method)
ch = Channel(s, r)

s.print_msg()
ch.communicate()
r.print_received_msg()