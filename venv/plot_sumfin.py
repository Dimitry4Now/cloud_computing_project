import matplotlib.pyplot as plt

machines = [1, 2, 3]
rps = [102, 273, 389]

W = 1000

execution_time = [W / x for x in rps]
speedup = [execution_time[0] / t for t in execution_time]

plt.figure()
plt.plot(machines, rps, marker='o')
plt.xlabel("Machines")
plt.ylabel("Throughput (req/s)")
plt.title("Throughput vs Machines")
plt.xticks(machines, [str(m) for m in machines])
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig("test_throughput.png", dpi=300, bbox_inches="tight")
plt.close()

plt.figure()
plt.plot(machines, execution_time, marker='o')
plt.xlabel("Machines")
plt.ylabel("Execution Time (s)")
plt.title("Execution Time vs Machines")
plt.xticks(machines, [str(m) for m in machines])
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig("test_exec_time.png", dpi=300, bbox_inches="tight")
plt.close()

plt.figure()
plt.plot(machines, speedup, marker='o', label="Measured")
plt.plot(machines, machines, linestyle='--', label="Ideal")
plt.xlabel("Machines")
plt.ylabel("Speedup")
plt.legend()
plt.title("Speedup vs Machines")
plt.xticks(machines, [str(m) for m in machines])
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig("test_speedup.png", dpi=300, bbox_inches="tight")
plt.close()
