import asyncio
import aiohttp
import time
import csv
import statistics
import matplotlib.pyplot as plt

NUM_MACHINES = 2

TARGET_URL = "http://164.90.240.114/work"
RPS_LEVELS = [1, 10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
TEST_DURATION = 30
TIMEOUT = 15

async def send_request(latencies):
    start = time.perf_counter()
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(TARGET_URL):
                latencies.append(time.perf_counter() - start)
        except Exception:
            pass

async def run_test(rps):
    latencies = []
    interval = 1.0 / rps
    end_time = time.time() + TEST_DURATION
    expected_requests = rps * TEST_DURATION  # TOTAL requests we TRIED to send

    tasks = []
    while time.time() < end_time:
        tasks.append(asyncio.create_task(send_request(latencies)))
        await asyncio.sleep(interval)
    await asyncio.gather(*tasks)

    if latencies:
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 5 else max(latencies)
        # FIXED: success_rate = successful / expected_requests
        success_rate = (len(latencies) / expected_requests) * 100
        throughput = len(latencies) / TEST_DURATION  # ACTUAL req/s achieved
    else:
        avg_latency = float('inf')
        p95_latency = float('inf')
        success_rate = 0.0
        throughput = 0.0

    return avg_latency, p95_latency, success_rate, len(latencies), throughput

async def main():
    base_latency = None
    x_vals = []
    speedups = []
    results = []
    max_throughput = 0

    print(f"Testing with {NUM_MACHINES} active machines (NEW CONNECTIONS PER REQUEST)")

    for rps in RPS_LEVELS:
        print(f"Testing @ {rps:>4} RPS...", end=" ")
        result = await run_test(rps)
        avg_latency, p95_latency, success_rate, success_count, throughput = result
        results.append(result)
        max_throughput = max(max_throughput, throughput)
        
        if base_latency is None or base_latency == 0:
            base_latency = max(1.0, avg_latency)
            speedup = 1.0
        else:
            speedup = base_latency / avg_latency if avg_latency > 0 else float('inf')

        x_vals.append(rps)
        speedups.append(speedup)
        
        status = "EXCELLENT"
        if speedup < 0.8:
            status = "DEGRADING" 
        if success_rate < 90:
            status = "SATURATED"
        if avg_latency > 10:
            status = "QUEUEING"
            
        print(f"Avg: {avg_latency:6.2f}s P95: {p95_latency:6.2f}s "
              f"Success: {success_rate:5.1f}% Throughput: {throughput:5.1f}r/s {status}")
        
        if rps >= 10:
            print(f"   SATURATION POINT: ~{throughput:5.1f} req/s capacity "
                  f"({success_rate:4.1f}% of {rps} target)")

    print("-" * 70)
    print(f"🎯 MAX THROUGHPUT: {max_throughput:.1f} req/s across {NUM_MACHINES} machines")
    
    # CSV
    with open(f"speedup_{NUM_MACHINES}machines.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rps", "speedup", "avg_latency", "p95_latency", "success_rate", "throughput"])
        for i, rps in enumerate(RPS_LEVELS):
            avg_latency, p95_latency, success_rate, _, throughput = results[i]
            writer.writerow([rps, speedups[i], avg_latency, p95_latency, success_rate, throughput])
    print(f"Saved speedup_{NUM_MACHINES}machines.csv")

    # Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    line1 = ax1.plot(x_vals, speedups, marker="o", color="blue", linewidth=2, label="Speedup")
    ax1.set_xlabel("Target RPS")
    ax1.set_ylabel("Speedup (higher = better)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, alpha=0.3)
    
    # Add throughput as second Y axis
    ax2 = ax1.twinx()
    throughputs = [r[4] for r in results]
    line2 = ax2.plot(x_vals, throughputs, marker="s", color="green", linewidth=2, label="Throughput")
    ax2.set_ylabel("Achieved RPS", color="green")
    ax2.tick_params(axis="y", labelcolor="green")
    
    plt.suptitle("Cluster Load Test: Speedup + Throughput", fontsize=14)
    plt.title(f"{NUM_MACHINES} Machines - New TCP Connections Per Request", fontsize=12)
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right")
    
    plt.tight_layout()
    plt.savefig(f"speedup_{NUM_MACHINES}machines.png", dpi=300, bbox_inches='tight')
    print(f"Saved speedup_{NUM_MACHINES}machines.png")
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())

