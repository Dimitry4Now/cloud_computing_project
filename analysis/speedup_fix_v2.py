import asyncio
import aiohttp
import time
import csv
import statistics
import matplotlib.pyplot as plt

NUM_MACHINES = 1  # CHANGE THIS to match enabled machines

TARGET_URL = "http://164.90.240.114/work"
RPS_LEVELS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70]
TEST_DURATION = 30
TIMEOUT = 15

async def send_request(session, latencies):
    start = time.perf_counter()
    try:
        async with session.get(TARGET_URL) as response:
            await response.read()
            latencies.append(time.perf_counter() - start)
    except Exception:
        pass

async def run_test(rps):
    latencies = []
    interval = 1.0 / rps
    end_time = time.time() + TEST_DURATION
    
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        request_count = 0
        
        while time.time() < end_time:
            tasks.append(asyncio.create_task(send_request(session, latencies)))
            request_count += 1
            await asyncio.sleep(interval)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    # MATH CHECK:
    # attempted = request_count (how many we tried to send)
    # successful = len(latencies) (how many completed successfully)
    # success_rate = (successful / attempted) * 100
    # throughput = successful / TEST_DURATION (actual req/s achieved)
    
    if latencies:
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 5 else max(latencies)
        success_rate = (len(latencies) / request_count) * 100
        throughput = len(latencies) / TEST_DURATION
    else:
        avg_latency = float('inf')
        p95_latency = float('inf')
        success_rate = 0.0
        throughput = 0.0
    
    return avg_latency, p95_latency, success_rate, throughput

async def main():
    results = []
    baseline_throughput = None
    
    print(f"Testing {NUM_MACHINES} machine(s)\n")
    
    for rps in RPS_LEVELS:
        print(f"RPS {rps:>3}...", end=" ", flush=True)
        avg_lat, p95_lat, success, throughput = await run_test(rps)
        results.append((avg_lat, p95_lat, success, throughput))
        
        # First valid test is baseline
        if baseline_throughput is None and throughput > 0:
            baseline_throughput = throughput
        
        # SPEEDUP = current_throughput / baseline_throughput
        speedup = throughput / baseline_throughput if baseline_throughput else 1.0
        
        print(f"Throughput: {throughput:5.1f} req/s | Success: {success:5.1f}% | Speedup: {speedup:4.2f}x")
    
    # Find max throughput (saturation point)
    max_throughput = max([r[3] for r in results])
    print(f"\n🎯 Max throughput: {max_throughput:.1f} req/s")
    
    # Save CSV
    with open(f"speedup_{NUM_MACHINES}m.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rps", "throughput", "speedup", "success_rate", "avg_latency", "p95_latency"])
        for i, rps in enumerate(RPS_LEVELS):
            avg_lat, p95_lat, success, throughput = results[i]
            speedup = throughput / baseline_throughput if baseline_throughput else 1.0
            writer.writerow([rps, throughput, speedup, success, avg_lat, p95_lat])
    
    # Plot: Speedup
    speedups = [r[3] / baseline_throughput if baseline_throughput else 1.0 for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(RPS_LEVELS, speedups, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('Target RPS', fontsize=12)
    plt.ylabel('Speedup', fontsize=12)
    plt.title(f'Speedup - {NUM_MACHINES} Machine(s)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"speedup_{NUM_MACHINES}m.png", dpi=300)
    print(f"Saved speedup_{NUM_MACHINES}m.png")
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())
