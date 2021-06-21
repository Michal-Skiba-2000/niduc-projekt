import csv
import hamming_codec
import random
from reedsolo import RSCodec

from ImageToBits import ImageBitParser

TRIPLE = "triple"
HAMMING = "hamming"
SALOMON = "salomon"
SALOMON_DEPTH = 4
MULTIPLIER = 5


class Channel:
    def __init__(self, s, r, noise_rate):
        self.sender = s
        self.receiver = r
        self.noise_rate = noise_rate

    def communicate(self):
        for packet in self.sender.get_encoded_msg():
            packet = self._noise(packet)
            self.receiver.receive_packet(packet)

    def _noise(self, packet):
        new_packet = []

        for bit in packet:
            rand_int = random.randint(1, 100000)
            limit = 100000*self.noise_rate
            if rand_int <= limit:
                # print('rand_int: {}, limit: {}, noise_rate: {}'.format(rand_int, limit, self.noise_rate))
                if bit == 0:
                    new_packet.append(1)
                elif bit == 1:
                    new_packet.append(0)
                else:
                    raise
            else:
                new_packet.append(bit)

        return new_packet


class Sender:
    def __init__(self, msg, encode_method, bits_per_packet):
        self.msg = msg
        self.encode_method = encode_method
        self.bits_per_packet = bits_per_packet
        self.counter = 0
        self.rsc = RSCodec(SALOMON_DEPTH)

    def get_encoded_msg(self):
        while len(self.msg) >= (self.counter+1) * self.bits_per_packet:
            if self.encode_method == TRIPLE:
                yield self._get_triple_packet()
            elif self.encode_method == HAMMING:
                yield self._get_hamming_packet()
            elif self.encode_method == SALOMON:
                yield self._get_salomon_packet()
            else:
                raise

    def _get_triple_packet(self):
        packet_start = self.counter * self.bits_per_packet
        packet_end = (self.counter+1) * self.bits_per_packet
        packet = self.msg[packet_start:packet_end]
        encoded_packet = []

        for bit in packet:
            for i in range(MULTIPLIER):
                encoded_packet.append(bit)

        self.counter += 1
        return encoded_packet

    def _get_hamming_packet(self):
        packet_start = self.counter * self.bits_per_packet
        packet_end = (self.counter + 1) * self.bits_per_packet
        packet = self.msg[packet_start:packet_end]
        number = ImageBitParser.bit_array_to_number(packet)
        encoded_packet = [int(bit) for bit in hamming_codec.encode(number, self.bits_per_packet)]
        self.counter += 1
        return encoded_packet

    def _get_salomon_packet(self):
        packet_start = self.counter * self.bits_per_packet
        packet_end = (self.counter + 1) * self.bits_per_packet
        packet = self.msg[packet_start:packet_end]
        encoded_value = self.rsc.encode(packet)
        for number in encoded_value[self.bits_per_packet:]:
            packet += ImageBitParser.number_to_bit_array(number, 8)
        self.counter += 1
        return packet


class Receiver:
    def __init__(self, decode_method, bits_per_packet):
        self.msg = []
        self.decode_method = decode_method
        self.bits_per_packet = bits_per_packet
        self.rsc = RSCodec(SALOMON_DEPTH)

    def receive_packet(self, packet):
        if self.decode_method == TRIPLE:
            self._decode_triple_packet(packet)
        elif self.decode_method == HAMMING:
            self._decode_hamming_packet(packet)
        elif self.decode_method == SALOMON:
            self._decode_salomon_packet(packet)

    def _decode_triple_packet(self, packet):
        for i in range(0, len(packet), MULTIPLIER):
            zero = 0
            one = 0
            for j in range(3):
                if packet[i+j] == 0:
                    zero += 1
                elif packet[i+j] == 1:
                    one += 1
                else:
                    raise

            if zero > one:
                self.msg.append(0)
            else:
                self.msg.append(1)

    def _decode_hamming_packet(self, packet):
        number = ImageBitParser.bit_array_to_number(packet)
        decoded_packet = [int(bit) for bit in hamming_codec.decode(number, len(packet))]
        self.msg += decoded_packet

    def _decode_salomon_packet(self, packet):
        decoded_packet = [bit for bit in packet[:self.bits_per_packet]]
        packet = packet[self.bits_per_packet:]

        for i in range(0, len(packet), 8):
            bit_array = [packet[i], packet[i+1], packet[i+2], packet[i+3],
                         packet[i+4], packet[i+5], packet[i+6], packet[i+7]]
            number = ImageBitParser.bit_array_to_number(bit_array)
            decoded_packet.append(number)

        try:
            decoded_packet = self.rsc.decode(bytearray(decoded_packet))
        except Exception:
            decoded_packet = [decoded_packet[:self.bits_per_packet]]

        decoded_packet = [bit for bit in decoded_packet[0]]
        self.msg += decoded_packet


def compare_two_arrays(csw_writer, decode_method, bits, i, arr1, arr2):
    if len(arr1) != len(arr2):
        raise

    counter = 0
    for j in range(len(arr1)):
        if arr1[j] != arr2[j]:
            counter += 1

    csw_writer.writerow([decode_method, bits, i, counter/len(arr1)*100])



def foo():
    with open('data.csv', mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Metoda dekodowania', 'Ilosc bitow w pakiecie', 'Prawdobodopienstwo zmiany bitu(%)', 'Zmiana wiadomosci(%)'])
        for decode_method in [TRIPLE, HAMMING, SALOMON]:
            for bits in [4, 8]:
                for i in [0, 1, 3, 5, 10, 20, 30, 40, 50]:
                    image_bit_array = ImageBitParser.parse_img_to_bit_array('input.jpg')
                    size = image_bit_array[:32]
                    image_bit_array = image_bit_array[32:]
                    sender = Sender(image_bit_array, decode_method, bits)
                    receiver = Receiver(decode_method, bits)
                    channel = Channel(sender, receiver, i/100)
                    channel.communicate()
                    ImageBitParser.save_image_from_bit_array('out_{}_{}.jpg'.format(decode_method, i), size+receiver.msg)
                    compare_two_arrays(csv_writer, decode_method, bits, i, sender.msg, receiver.msg)
                    print('Ended communication for {} method, with {}% of changing single bit, with {} bits per packet.'.format(decode_method, i, bits))


if __name__ == '__main__':
    foo()
