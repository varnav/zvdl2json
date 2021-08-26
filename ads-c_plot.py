#!/usr/bin/env python3
import os

import plotly.express as px
import pandas as pd
import os

# Get homedir
from pathlib import Path

homedir = str(Path.home())

df = pd.read_csv(homedir + os.sep + 'positions.csv', names=['lat', 'lon', 'alt'])

fig = px.scatter_geo(df, lat='lat', lon='lon')
fig.update_layout(title='World map', title_x=0.5)
fig.show()
