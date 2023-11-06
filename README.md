# Elech-Tools

Python Utilities for Electrochemical Measurements in My Laboratory.

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

## Utils

### Search

The Search class finds the nearest value in an array or data structure to a specified target value. It's a valuable tool for tasks involving proximity search in various data structures, such as lists, NumPy arrays, pandas Series, or DataFrames, streamlining the process of locating the closest data point.

#### Usage

```python
import pandas as pd
from elech_tools.utils.search import Search

# Sample series
series = pd.Series([1.1, 2.2, 3.3, 4.4, 5.5])

# Using the Search class to find the nearest value in the DataFrame
search_obj = Search(series)
nearest_index = search_obj.get_nearest_index(3.2)

print("Nearest Index:", nearest_index)# 2 (index=[0,1,*2*,3,4])
print("Nearest Value:", series.at[nearest_index])# 3.3
```

If the array is not sorted, you can call Search().sort() to ensure accurate results.

```python
import pandas as pd
from elech_tools.utils.search import Search

# Disordered sample series
series = pd.Series([4.4, 1.1, 5.5, 3.3, 2.2])

search_obj = Search(series)
# To get accurate results, call `sort()` method to Search object.
search_obj.sort()
nearest_index = search_obj.get_nearest_index(3.2)

print("Nearest Index:", nearest_index)# 3 (index=[0,1,2,*3*,4])
print("Nearest Value:", series.at[nearest_index])# 3.3
```



## Contribution

### Pre-commit

This project utilizes `pre-commit` for code formatting. To get started, please install `pre-commit` locally and register it with the project.

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
