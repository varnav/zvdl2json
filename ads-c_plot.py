#!/usr/bin/env python3
import sys
import plotly.express as px
import pandas as pd

df = pd.read_csv(sys.argv[1], names=['time', 'tail', 'lat', 'lon', 'alt'])
df['tail'] = df['tail'].str.replace('.', '', regex=False)
print(df)
fig = px.scatter_geo(df, lat='lat', lon='lon', hover_data=['tail', 'alt', 'time'], color='alt')
fig.update_geos(
    # showlakes=True, lakecolor="Blue",
    # showrivers=True, rivercolor="Blue",
    showcountries=True,
    lataxis_showgrid=True, lonaxis_showgrid=True
)
fig.update_layout(title='World map', title_x=0.5)
fig.show()
