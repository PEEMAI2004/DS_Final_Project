import os
import glob
import subprocess
import time
import psutil
import csv
import random
import struct
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Constants
ALGORITHMS_DIR = 'algorithms'
RESULTS_DIR = 'results'
CSV_FILENAME_PREFIX = 'results'
CSV_FILENAME_EXTENSION = '.csv'
NUM_THREADS = 8  # Number of threads to use
MEMORY_SAMPLING_INTERVAL = 0.1  # Memory sampling interval in seconds

# Ensure the results folder exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# Find all .c files in the algorithms directory and sort them alphabetically
c_files = sorted(glob.glob(os.path.join(ALGORITHMS_DIR, '*.c')))

# Find the next available CSV filename
i = 1
while True:
    csv_filename = f'{CSV_FILENAME_PREFIX}_{i}{CSV_FILENAME_EXTENSION}'
    csv_filepath = os.path.join(RESULTS_DIR, csv_filename)
    if not os.path.exists(csv_filepath):
        break
    i += 1

# Headers for the CSV file
headers = ['Filename', 'C File Size (bytes)', 'Compiled File Size (bytes)', 
           'Compile Time (microseconds)', 'Compile Memory (bytes)', 
           'Run Time (microseconds)', 'Run Memory (bytes)', 'Status', 'Error', 'Number of Samples']

# Helper functions
def measure_time_memory(command):
    start_time = time.time()
    process = psutil.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    peak_memory = 0
    stdout, stderr = None, None

    while process.poll() is None:
        try:
            current_memory = process.memory_info().rss
            peak_memory = max(peak_memory, current_memory)
        except psutil.NoSuchProcess:
            break
        time.sleep(MEMORY_SAMPLING_INTERVAL)

    stdout, stderr = process.communicate()
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1_000_000  # Convert to microseconds
    return elapsed_time, peak_memory, process.returncode, stdout, stderr

def delete_out_files(subfolder):
    try:
        files = os.listdir(subfolder)
        for filename in files:
            if filename.endswith('.out'):
                filepath = os.path.join(subfolder, filename)
                os.remove(filepath)
    except OSError as e:
        print(f'Error deleting .out files: {e}')

# Generate numbers.bin file
def generate_numbers_bin(size):
    numbers = random.sample(range(1, size * 2), size)
    data = struct.pack('{}i'.format(size), *numbers)
    with open('numbers.bin', 'wb') as file:
        file.write(data)

# User-defined SIZE
SIZE = int(input("Enter the size of the array: "))
generate_numbers_bin(SIZE)

# Thread-safe data collection
data = []
data_lock = Lock()

def process_file(c_file):
    base_name = os.path.basename(c_file)
    compiled_file = os.path.join(ALGORITHMS_DIR, base_name.replace('.c', ''))

    print(f"Processing {base_name}...")

    # Measure the size of the .c file
    c_file_size = os.path.getsize(c_file)

    # Compile the C file
    compile_command = ['gcc', c_file, '-o', compiled_file]
    compile_time, compile_memory, compile_returncode, _, compile_error = measure_time_memory(compile_command)

    # Check if the compiled file was created
    if compile_returncode != 0:
        print(f"\033[91mFailed to compile {base_name}: {compile_error.decode()}\033[0m")
        result = [base_name, c_file_size, 0, compile_time, compile_memory, 0, 0, 'Compilation Failed', compile_error.decode(), SIZE]
        with data_lock:
            data.append(result)
        return

    print(f"\033[92mCompiled {base_name}\033[0m")

    # Measure the size of the compiled file
    compiled_file_size = os.path.getsize(compiled_file)

    # Run the compiled file
    run_command = [compiled_file]
    run_time, run_memory, run_returncode, _, run_error = measure_time_memory(run_command)

    if run_returncode != 0:
        print(f"\033[91mFailed to run {base_name}: {run_error.decode()}\033[0m")
        result = [base_name, c_file_size, compiled_file_size, compile_time, compile_memory, run_time, run_memory, 'Runtime Failed', run_error.decode(), SIZE]
    else:
        print(f"\033[92mRan {base_name}\033[0m")
        result = [base_name, c_file_size, compiled_file_size, compile_time, compile_memory, run_time, run_memory, 'Success', '', SIZE]

    # Delete the compiled file
    os.remove(compiled_file)
    print(f"\033[93mDeleted compiled file {compiled_file}\033[0m")

    # Collect the results
    with data_lock:
        data.append(result)

# Use ThreadPoolExecutor to process files in parallel
with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(process_file, c_file) for c_file in c_files]
    for future in as_completed(futures):
        future.result()  # wait for all futures to complete

# Write results to CSV
with open(csv_filepath, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(data)

print(f"Results have been written to {csv_filepath}")

# Delete .out files in the algorithms directory
delete_out_files(ALGORITHMS_DIR)
