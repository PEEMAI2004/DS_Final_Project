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

def convert_to_command(input_list):
    return ' '.join(input_list)

# Helper functions
def measure_time_memory(command):
    command = convert_to_command(command)
    print(f"Running command: {command}")
    
    # Redirect stdout and stderr to os.devnull
    with open(os.devnull, 'w') as devnull:
        # Start the command
        start_time = time.time()
        process = subprocess.Popen(command, shell=True, stdout=devnull, stderr=devnull)
        
        # Get process info
        process_info = psutil.Process(process.pid)
        
        # Monitor RAM usage
        peak_ram_usage = 0
        try:
            while process.poll() is None:
                current_ram_usage = process_info.memory_info().rss / 1024  # in kB
                if current_ram_usage > peak_ram_usage:
                    peak_ram_usage = current_ram_usage
                time.sleep(0.1)  # Sleep a bit before checking again
        except psutil.NoSuchProcess:
            pass  # The process finished before we could check again
        
        # Calculate the total run time
        end_time = time.time()
        run_time = (end_time - start_time) * 1000000  # in microseconds
    
    return run_time, peak_ram_usage, process.returncode

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
    compile_time, compile_memory, compile_returncode = measure_time_memory(compile_command)

    # Check if the compiled file was created
    if compile_returncode != 0:
        print(f"\033[91mFailed to compile {base_name}: \033[0m")
        result = [base_name, c_file_size, 0, compile_time, compile_memory, 0, 0, 'Compilation Failed', SIZE]
        with data_lock:
            data.append(result)
        return

    print(f"\033[92mCompiled {base_name}\033[0m")

    # Measure the size of the compiled file
    compiled_file_size = os.path.getsize(compiled_file)

    # Run the compiled file
    run_command = [compiled_file]
    run_time, run_memory, run_returncode = measure_time_memory(run_command)

    if run_returncode != 0:
        print(f"\033[91mFailed to run {base_name}: \033[0m")
        result = [base_name, c_file_size, compiled_file_size, compile_time, compile_memory, run_time, run_memory, 'Runtime Failed', SIZE]
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
