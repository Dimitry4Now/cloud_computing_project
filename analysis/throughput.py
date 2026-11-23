import asyncio
import aiohttp
import time
import csv
import matplotlib.pyplot as plt

# =====================
# Configuration
# =====================
TARGET_URL = "http://164.90.240.114/work"

RPS_LEVELS = [1, 10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
INSTANCES = 3              # change manually when scaling backends
TEST_DURATION = 30         # seconds per RPS
TIMEOUT = 15                # request timeout (seconds)

X_AXIS_MODE = "rps"        # "rps" or "instances"

# =====================
# Request logic
# =====================
async def send_request(session, results):
    try:
        async with session.get(TARGET_URL, timeout=TIMEOUT) as response:
            results.append(response.status == 200)
    except Exception:
        results.append(False)

async def run_test(rps):
    results = []
    start_time = time.time()  # Track actual start
    interval = 1.0 / rps
    end_time = time.time() + TEST_DURATION
    sent_count = 0

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        while time.time() < end_time:
            tasks.append(asyncio.create_task(send_request(session, results)))
            sent_count += 1
            await asyncio.sleep(interval)
        await asyncio.gather(*tasks)

    actual_duration = time.time() - start_time
    total = len(results)
    success = sum(results)

    # Corrected metrics
    observed_throughput = total / actual_duration  # Requests sent per second
    success_throughput = success / actual_duration  # Successful req/s (server capacity)
    failure_rate = 1 - (success / total) if total > 0 else 0

    return observed_throughput, success_throughput, failure_rate, sent_count, actual_duration

# =====================
# Main experiment
# =====================
async def main():
    x_vals = []
    throughputs = []
    failure_rates = []

    # Run all tests first
    for rps in RPS_LEVELS:
        print(f"Running throughput test @ {rps} RPS")
        obs_tp, success_tp, failure_rate, sent, duration = await run_test(rps)

        x_value = rps if X_AXIS_MODE == "rps" else INSTANCES
        x_vals.append(x_value)
        throughputs.append(success_tp)  # Plot server capacity
        failure_rates.append(failure_rate)

        print(f"  Sent: {sent} req in {duration:.1f}s")
        print(f"  Observed throughput: {obs_tp:.2f} req/s")
        print(f"  Success throughput: {success_tp:.2f} req/s")
        print(f"  Failure rate: {failure_rate:.4f}")

    # =====================
    # Save CSV (after all tests)
    # =====================
    with open("throughput_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x_value", "throughput_req_per_sec", "failure_rate"])
        writer.writerows(zip(x_vals, throughputs, failure_rates))

    print("Saved throughput_results.csv")

    # =====================
    # Plot (dual Y-axis)
    # =====================
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Throughput (left axis)
    ax1.plot(x_vals, throughputs, marker="o", color="blue", linewidth=2, markersize=6, label="Success Throughput")
    ax1.set_xlabel("Target RPS" if X_AXIS_MODE == "rps" else "Number of Instances")
    ax1.set_ylabel("Success Throughput (req/s)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, alpha=0.3)

    # Failure rate (right axis)
    ax2 = ax1.twinx()
    ax2.plot(x_vals, failure_rates, marker="x", color="red", linewidth=2, markersize=8, label="Failure Rate")
    ax2.set_ylabel("Failure Rate", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Title & legend
    plt.title("Server Throughput Capacity and Failure Rate vs Target Load", fontsize=14, pad=20)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.savefig("throughput_failure_combined.png", dpi=300, bbox_inches='tight')
    plt.show()
    print("Saved throughput_failure_combined.png")

# =====================
# Entry point
# =====================
if __name__ == "__main__":
    asyncio.run(main())

