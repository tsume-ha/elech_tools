# Elech-Tools

Python tools for electrochemical measurements in my lab.

## Install

```bash
pip install git+https://github.com/tsume-ha/elech_tools.git
```

## Analysis Mode

### Galvanostatic charge / discharge

#### Usage

```Python
import matplotlib.pyplot as plt
from elech_tools import GCDAnalyser, get_GCDData, ordinal

path = "path/to/the/file"
data = get_GCDData(file_path=path)
analyser = GCDAnalyser(data)

fig, ax = plt.subplots()
ax = analyser.plot_charge_discharge(ax=ax, cycle=1, mode="Discharge")
fig.show()
```

## Contribution

### Pre-commit

This project uses pre-commit for code formatting.
Please install `pre-commit` locally and register it.

For mac
```bash
brew install pre-commit
pre-commit install
```

For local python
```bash
pip install pre-commit
pre-commit install
```
