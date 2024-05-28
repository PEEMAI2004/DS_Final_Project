import random
import struct

# Define the size of the array
SIZE = 10000

# Generate n unique random numbers
numbers = random.sample(range(1, SIZE * 2), SIZE)

# Convert numbers to bytes
data = struct.pack('{}i'.format(SIZE), *numbers)

# Write the bytes to a binary file
with open('numbers.bin', 'wb') as file:
    file.write(data)
