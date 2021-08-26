#!/usr/bin/env python3
import sys
import plotly.express as px
import pandas as pd
import os

# Get homedir
from pathlib import Path

hour = int(sys.argv[1])
homedir = str(Path.home())

df = pd.read_csv(homedir + os.sep + 'positions_' + str(hour) + '.csv', names=['lat', 'lon', 'alt', 'sec'])
df['min'] = df['sec'] / 60
df['time'] = str(hour) + ':' + df['min'].astype(int).astype(str).str.zfill(2)

fig = px.scatter_geo(df, lat='lat', lon='lon', hover_data=['alt', 'time'])
fig.update_layout(title='World map', title_x=0.5)
fig.show()
