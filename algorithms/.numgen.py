import random
import struct

# Generate 1000 unique random numbers
numbers = random.sample(range(1, 2000), 1000)

# Convert numbers to bytes
data = struct.pack('1000i', *numbers)

# Write the bytes to a binary file
with open('numbers.bin', 'wb') as file:
    file.write(data)
