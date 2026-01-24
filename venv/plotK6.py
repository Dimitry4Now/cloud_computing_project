import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
# Path to CSV files
# Use filenames like: results_1machine.csv, results_2machines.csv, results_3machines.csv
csv_files = {
    1: "results_1machine.csv",
    2: "results_2machines.csv",
    3: "results_3machines.csv"
}

# Stage duration in seconds (must match your k6 script)
stage_duration = 30  # seconds per stage
stages = [1,10,50,100,200,300,400,500,600,700,800,900,1000]  # Requested RPS

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def process_csv(file_path):
    """Process a k6 CSV and compute throughput and average execution time per stage"""
    df = pd.read_csv(file_path)
    # Ensure http_req_duration is numeric
    df['http_req_duration'] = pd.to_numeric(df['http_req_duration'], errors='coerce')

    throughput_list = []
    exec_time_list = []

    # Split by stage duration
    total_rows = df.shape[0]
    rows_per_stage = int(total_rows / len(stages))  # approximate, k6 may vary slightly

    for i in range(len(stages)):
        start_idx = i * rows_per_stage
        end_idx = (i+1) * rows_per_stage
        stage_df = df.iloc[start_idx:end_idx]

        # Throughput = # of successful requests / stage_duration
        successful = stage_df[stage_df['status'] == 200].shape[0]
        throughput = successful / stage_duration
        throughput_list.append(throughput)

        # Average execution time in seconds
        avg_time = stage_df['http_req_duration'].mean() / 1000  # k6 stores in ms
        exec_time_list.append(avg_time)

    return throughput_list, exec_time_list

# -----------------------------
# PROCESS CSVs
# -----------------------------

results = {}
for machines, file in csv_files.items():
    if not os.path.exists(file):
        print(f"Warning: {file} not found. Skipping {machines} machines.")
        continue
    throughput, exec_time = process_csv(file)
    results[machines] = {'throughput': throughput, 'exec_time': exec_time}

# -----------------------------
# PLOTTING
# -----------------------------

# 1. Throughput vs Requested RPS
plt.figure(figsize=(10,6))
for machines, data in results.items():
    plt.plot(stages[:len(data['throughput'])], data['throughput'], marker='o', label=f'{machines} machine(s)')
plt.xlabel("Requested RPS")
plt.ylabel("Measured Throughput (RPS)")
plt.title("Throughput vs Requested RPS")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("throughput_vs_rps.png")
plt.show()

# 2. Execution Time vs Requested RPS
plt.figure(figsize=(10,6))
for machines, data in results.items():
    plt.plot(stages[:len(data['exec_time'])], data['exec_time'], marker='o', label=f'{machines} machine(s)')
plt.xlabel("Requested RPS")
plt.ylabel("Average Execution Time (s)")
plt.title("Execution Time vs Requested RPS")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("execution_time_vs_rps.png")
plt.show()

# 3. Speedup vs Number of Machines
# Compute speedup per stage relative to 1 machine
if 1 in results:
    plt.figure(figsize=(10,6))
    for machines, data in results.items():
        if machines == 1:
            continue
        speedup = [t_new / t_base for t_base, t_new in zip(results[1]['throughput'], data['throughput'])]
        plt.plot(stages[:len(speedup)], speedup, marker='o', label=f'{machines} machine(s) vs 1 machine')
    plt.xlabel("Requested RPS")
    plt.ylabel("Speedup")
    plt.title("Speedup vs Number of Machines")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("speedup_vs_rps.png")
    plt.show()
else:
    print("1-machine CSV missing. Cannot calculate speedup.")
