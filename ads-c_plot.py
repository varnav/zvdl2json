import plotly.express as px
import pandas as pd

# Get homedir
from pathlib import Path
homedir = str(Path.home())

df = pd.read_csv(homedir + 'positions.csv')

fig = px.scatter_geo(df,lat='lat',lon='lon')
fig.update_layout(title = 'World map', title_x=0.5)
fig.show()