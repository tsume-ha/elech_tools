from tkinter import filedialog

import matplotlib.pyplot as plt

from elech_tools import GCDAnalyser, get_GCDData, ordinal

plt.rcParams["font.size"] = 18
plt.rcParams["font.family"] = "Arial"
plt.rcParams["xtick.direction"] = "in"
plt.rcParams["xtick.major.size"] = 5
plt.rcParams["xtick.minor.size"] = 5
plt.rcParams["ytick.direction"] = "in"
plt.rcParams["ytick.major.size"] = 5
plt.rcParams["ytick.minor.size"] = 5
plt.tight_layout()
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

path = filedialog.askopenfilename()
data = get_GCDData(file_path=path)
analyser = GCDAnalyser(data)

fig, ax = plt.subplots()
for i in range(2):
    ax = analyser.plot_charge_discharge(
        ax=ax, cycle=i + 1, mode="Charge", label=f"{ordinal(i + 1)}", color=colors[i]
    )
    ax = analyser.plot_charge_discharge(
        ax=ax, cycle=i + 1, mode="Discharge", color=colors[i]
    )
fig.legend()
fig.tight_layout()

fig.savefig("test.png")
