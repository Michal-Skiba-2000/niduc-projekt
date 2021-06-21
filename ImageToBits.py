from PIL import Image
from math import pow


class ImageBitParser:
    @staticmethod
    def number_to_bit_array(number, length):
        bin_arr = bin(number)[2:]
        return_arr = []

        for bit in bin_arr:
            return_arr.append(int(bit))

        num = length - len(return_arr)
        for i in range(0, num):
            return_arr.insert(0, 0)

        return return_arr

    @classmethod
    def parse_img_to_bit_array(cls, image_name):
        image = Image.open(image_name)
        bit_array = []
        bit_array += cls.number_to_bit_array(image.height, 16)
        bit_array += cls.number_to_bit_array(image.width, 16)

        for y in range(image.height):
            for x in range(image.width):
                pixels = image.getpixel((x, y))
                for pixel in pixels:
                    bit_array += cls.number_to_bit_array(pixel, 8)

        return bit_array

    @staticmethod
    def bit_array_to_number(bit_array):
        i = 0
        number = 0
        for bit in reversed(bit_array):
            number += bit * pow(2, i)
            i += 1

        return int(number)

    @classmethod
    def save_image_from_bit_array(cls, image_name, bit_array):
        height = cls.bit_array_to_number(bit_array[:16])
        bit_array = bit_array[16:]
        width = cls.bit_array_to_number(bit_array[:16])
        bit_array = bit_array[16:]
        image = Image.new('RGB', (width, height), 'red')

        i = 0

        for y in range(height):
            for x in range(width):
                pixel = []
                for j in range(3):
                    pixel.append(cls.bit_array_to_number([bit_array[0+((i+j)*8)],bit_array[1+((i+j)*8)],
                                                          bit_array[2+((i+j)*8)], bit_array[3+((i+j)*8)],
                                                          bit_array[4+((i+j)*8)], bit_array[5+((i+j)*8)],
                                                          bit_array[6+((i+j)*8)], bit_array[7+((i+j)*8)]]))

                pixel = (pixel[0], pixel[1], pixel[2])
                image.putpixel((x, y), pixel)
                i += 3

        image.save(image_name)
