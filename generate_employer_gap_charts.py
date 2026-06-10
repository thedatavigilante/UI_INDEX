import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from pathlib import Path

output_dir = Path("figures")
output_dir.mkdir(exist_ok=True)

with open("data/political/employer_contribution_gap.json") as f:
    gaps = json.load(f)

states = [g["state"] for g in gaps]
per_emp = [g["per_employee_gap"] for g in gaps]
aggregate = [g["aggregate_gap"] / 1e6 for g in gaps]  # millions
pct = [g["wage_base_as_pct_of_avg"] * 100 for g in gaps]
expected = [g["expected_wage_base"] for g in gaps]
statutory = [g["statutory_wage_base"] for g in gaps]

# Figure 05: Per-employee gap
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#e74c3c', '#e67e22', '#f1c40f']
bars = ax.bar(states, per_emp, color=colors, edgecolor='black')
ax.set_ylabel('Per-Employee Underpayment ($/year)')
ax.set_title('SUI Employer Contribution Gap: Per-Employee Loss (2026)')
ax.axhline(y=0, color='black', linewidth=0.5)
for bar, val in zip(bars, per_emp):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'${val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.text(0.98, 0.98, f'Total DMV: ${sum(g["aggregate_gap"] for g in gaps)/1e6:.1f}M/year',
        transform=ax.transAxes, ha='right', va='top', fontsize=10,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
plt.tight_layout()
plt.savefig(output_dir / "05_employer_per_employee_gap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved figures/05_employer_per_employee_gap.png")

# Figure 06: Aggregate gap
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(states, aggregate, color=colors, edgecolor='black')
ax.set_ylabel('Annual Trust Fund Shortfall ($ Millions)')
ax.set_title('SUI Trust Fund Shortfall by State (2026)')
for bar, val in zip(bars, aggregate):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f'${val:.1f}M', ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.text(0.98, 0.98, f'Total: ${sum(aggregate):.1f}M/year',
        transform=ax.transAxes, ha='right', va='top', fontsize=11, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
plt.tight_layout()
plt.savefig(output_dir / "06_employer_aggregate_gap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved figures/06_employer_aggregate_gap.png")

# Figure 07: Statutory vs Expected wage base
fig, ax = plt.subplots(figsize=(9, 5))
x = range(len(states))
width = 0.35
bars1 = ax.bar([i - width/2 for i in x], statutory, width, label='Statutory Base', color='#3498db', edgecolor='black')
bars2 = ax.bar([i + width/2 for i in x], expected, width, label='Expected (2010 Ratio)', color='#e74c3c', edgecolor='black')
ax.set_ylabel('Taxable Wage Base ($)')
ax.set_title('SUI Taxable Wage Base: Statutory vs Expected (2026)')
ax.set_xticks(x)
ax.set_xticklabels(states)
ax.legend()
for bar, val in zip(bars1, statutory):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
            f'${val:,.0f}', ha='center', va='bottom', fontsize=9)
for bar, val in zip(bars2, expected):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
            f'${val:,.0f}', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig(output_dir / "07_statutory_vs_expected_wage_base.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved figures/07_statutory_vs_expected_wage_base.png")

print(f"\n✅ Generated 3 employer contribution gap charts")
