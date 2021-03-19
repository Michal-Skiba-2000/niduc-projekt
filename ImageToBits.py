from PIL import Image

image = Image.open("buchal.jpg")
#image.show()

def pixel_to_array(pixel):
    bin_arr = bin(pixel)[2:]
    return_arr = []

    for bit in bin_arr:
        return_arr.append(bit)

    num = 8 - len(return_arr)

    for i in range(0, num):
        return_arr.insert(0, 0)

    return(return_arr)

for y in range(image.height):
    for x in range(image.width):
        pixels = image.getpixel((x,y))
        print(pixels)
        for pixel in pixels:
            print(pixel_to_array(pixel))