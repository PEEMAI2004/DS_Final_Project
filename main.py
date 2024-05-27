import os
import subprocess
import time
import csv
import resource

SUBFOLDER = 'algorithms'
RESULT_FOLDER = 'result'
CSV_FILENAME_PREFIX = 'result'
CSV_FILENAME_EXTENSION = '.csv'

def get_memory_usage():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

def compile_and_time(filepath, filename):
    output_path = os.path.join(SUBFOLDER, f'{filename}.out')
    compile_command = ['gcc', filepath, '-o', output_path]
    
    # Measure compilation time and memory usage
    compile_start_time = time.time_ns()
    compile_start_mem = get_memory_usage()
    compile_result = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    compile_end_time = time.time_ns()
    compile_end_mem = get_memory_usage()
    
    compile_time_taken = compile_end_time - compile_start_time  # Time in nanoseconds
    compile_mem_used = compile_end_mem - compile_start_mem      # Memory in kilobytes
    
    if compile_result.returncode != 0:
        print(f'Failed to compile {filename}.')
        print(compile_result.stderr.decode())
        return (filename, compile_time_taken, compile_mem_used, None, None, None)
    
    # Get compiled file size
    compiled_file_size = os.path.getsize(output_path)  # Size in bytes
    
    print(f'Compiled {filename} in {compile_time_taken} ns. Memory used: {compile_mem_used} KB. Compiled file size: {compiled_file_size} bytes.')

    # Measure runtime and memory usage
    run_command = [output_path]
    run_start_time = time.time_ns()
    run_start_mem = get_memory_usage()
    run_result = subprocess.run(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    run_end_time = time.time_ns()
    run_end_mem = get_memory_usage()
    
    run_time_taken = run_end_time - run_start_time  # Time in nanoseconds
    run_mem_used = run_end_mem - run_start_mem      # Memory in kilobytes
    
    if run_result.returncode == 0:
        print(f'Ran {filename} in {run_time_taken} ns. Memory used: {run_mem_used} KB.')
    else:
        print(f'Failed to run {filename}.')
        print(run_result.stderr.decode())
    
    return (filename, compile_time_taken, compile_mem_used, compiled_file_size, run_time_taken, run_mem_used)

def delete_out_files():
    try:
        files = os.listdir(SUBFOLDER)
        for filename in files:
            if filename.endswith('.out'):
                filepath = os.path.join(SUBFOLDER, filename)
                os.remove(filepath)
    except OSError as e:
        print(f'Error deleting .out files: {e}')

def main():
    try:
        files = os.listdir(SUBFOLDER)
    except OSError as e:
        print(f'Error opening directory: {e}')
        return

    compilation_and_runtime_times = []

    for filename in files:
        if filename.endswith('.c'):
            filepath = os.path.join(SUBFOLDER, filename)
            result = compile_and_time(filepath, filename)
            compilation_and_runtime_times.append(result)
    
    # Ensure the result folder exists
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    
    # Find the next available CSV filename
    i = 1
    while True:
        csv_filename = f'{CSV_FILENAME_PREFIX}_{i}{CSV_FILENAME_EXTENSION}'
        if not os.path.exists(os.path.join(RESULT_FOLDER, csv_filename)):
            break
        i += 1
    
    csv_filepath = os.path.join(RESULT_FOLDER, csv_filename)
    
    # Write the results to the CSV file
    with open(csv_filepath, 'w', newline='') as csvfile:
        fieldnames = ['filename', 'compile_time_ns', 'compile_mem_kb', 'compiled_file_size_bytes', 'run_time_ns', 'run_mem_kb']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for filename, compile_time, compile_mem, compiled_file_size, run_time, run_mem in compilation_and_runtime_times:
            writer.writerow({'filename': filename, 'compile_time_ns': compile_time, 'compile_mem_kb': compile_mem,
                             'compiled_file_size_bytes': compiled_file_size, 'run_time_ns': run_time, 'run_mem_kb': run_mem})

    # Delete all compiled files
    delete_out_files()

if __name__ == '__main__':
    main()
