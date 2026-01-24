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
    """NEW TCP connection PER REQUEST - forces HAProxy round-robin"""
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

    tasks = []
    while time.time() < end_time:
        tasks.append(asyncio.create_task(send_request(latencies)))
        await asyncio.sleep(interval)
    await asyncio.gather(*tasks)

    if latencies:
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 5 else max(latencies)
        success_rate = len(latencies) / TEST_DURATION * interval * 100
    else:
        avg_latency = float('inf')
        p95_latency = float('inf')
        success_rate = 0.0

    return avg_latency, p95_latency, success_rate, len(latencies)

async def main():
    base_latency = None
    x_vals = []
    speedups = []
    results = []

    print(f"Testing with {NUM_MACHINES} active machines (NEW CONNECTIONS PER REQUEST)")

    for rps in RPS_LEVELS:
        print(f"Testing @ {rps:>4} RPS...", end=" ")
        result = await run_test(rps)
        avg_latency, p95_latency, success_rate, success_count = result
        results.append(result)
        
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
        if speedup < 0.5 or success_rate < 50:
            status = "SATURATED"
        if avg_latency > 10:
            status = "QUEUEING"
            
        print(f"Avg: {avg_latency:6.2f}s P95: {p95_latency:6.2f}s "
              f"Success: {success_rate:6.1f}% Speedup: {speedup:6.2f} {status}")
        
        if rps >= 10:
            print(f"   PREDICTION: Cluster capacity ~{success_count / TEST_DURATION:5.1f} req/s "
                  f"({(success_count / TEST_DURATION / rps * 100):4.1f}% of target)")

    print("-" * 60)
    print(f"FINAL CAPACITY: {NUM_MACHINES} machines = ~{success_count / TEST_DURATION:.1f} req/s total")
    
    # CSV
    with open(f"speedup_{NUM_MACHINES}machines.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rps", "speedup", "avg_latency", "p95_latency", "success_rate"])
        for i, rps in enumerate(RPS_LEVELS):
            avg_latency, p95_latency, success_rate, _ = results[i]
            writer.writerow([rps, speedups[i], avg_latency, p95_latency, success_rate])
    print(f"Saved speedup_{NUM_MACHINES}machines.csv")

    # Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    line1 = ax1.plot(x_vals, speedups, marker="o", color="blue", linewidth=2, label="Speedup")
    ax1.set_xlabel("RPS")
    ax1.set_ylabel("Speedup (higher = better)", color="blue", fontsize=12)
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, alpha=0.3)
    
    max_capacity = 10.0 * NUM_MACHINES  # Adjust based on your single machine capacity
    ax1.axvline(x=max_capacity, color="red", linestyle="--", alpha=0.7, 
                label=f"Capacity Limit ({max_capacity:.0f} req/s)")
    
    plt.suptitle("Amdahl's Law: Speedup Degradation Under Load (5s Processing)", fontsize=14)
    plt.title(f"{NUM_MACHINES} Active Machines - NEW TCP Connections Per Request", fontsize=12, pad=10)
    ax1.legend(loc="upper right")
    
    plt.tight_layout()
    plt.savefig(f"speedup_{NUM_MACHINES}machines.png", dpi=300, bbox_inches='tight')
    print(f"Saved speedup_{NUM_MACHINES}machines.png")
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())

