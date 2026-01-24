import pandas as pd
import matplotlib.pyplot as plt
import glob

# Load all CSV files
all_data = []
for csv in glob.glob("machines_*.csv"):
    df = pd.read_csv(csv)
    all_data.append(df)

df = pd.concat(all_data, ignore_index=True)

# Calculate speedup vs 1-machine baseline
baseline = df[df['machines'] == 1].set_index('target_rps')['throughput']
df['speedup'] = df.apply(lambda row: row['throughput'] / baseline.get(row['target_rps'], 1.0), axis=1)

# Plot
plt.figure(figsize=(12, 7))
for machines in [1, 2, 3]:
    data = df[df['machines'] == machines]
    plt.plot(data['target_rps'], data['speedup'], 
             marker='o', linewidth=3, label=f'{machines} Machine(s)',
             markersize=8)

plt.xlabel('Target RPS', fontsize=12)
plt.ylabel('Speedup (vs 1 Machine)', fontsize=12)
plt.title('HAProxy Load Balancing Scaling', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('haproxy_scaling.png', dpi=300, bbox_inches='tight')
plt.show()

print("Max speedup: 3 machines = %.1fx" % df[df['machines']==3]['speedup'].max())

