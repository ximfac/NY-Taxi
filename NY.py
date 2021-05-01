import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, time, timedelta
import plotly.graph_objects as go
import pydeck as pdk

st.title('NY Taxi project')

colss = st.beta_columns(2)

data = pd.read_csv('june_preds.csv', index_col=0, parse_dates=True)
dates=np.unique(data.index.strftime('%Y-%m-%d'))
regions=pd.read_csv('regions.csv', sep=';')
regions.index=regions.region
regions.drop(['region'], axis=1, inplace=True)
with colss[0]:
    zone=st.sidebar.selectbox('Зона', np.unique(data.zone.values))
with colss[1]:
    date=st.sidebar.selectbox('Дата', dates)
    
reg=regions[regions.index==zone]

reg['avg_trips']=data[['y']][data.zone==zone].loc[f'{date}'].mean()[0]
reg['preds']=data[['preds']][data.zone==zone].loc[f'{date}'].mean()[0]

st.subheader(f'Координаты {zone} зоны и среднее количество поездок в час {date}')    
st.write(reg)


reg['lon']=(reg.iloc[:,0]+reg.iloc[:,1])/2
reg['lat']=(reg.iloc[:,2]+reg.iloc[:,3])/2

reg3=reg[['lon', 'lat']]

long=reg3.lon
lat=reg3.lat

st.subheader('Расположение зоны на карте')

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v11",
    initial_view_state={
        "latitude": long,
        "longitude": lat,
        "zoom": 12,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=reg3,
            get_position=["lon", "lat"],
            radius=300,
            elevation_scale=4,
            elevation_range=[0, 2000],
            pickable=False,
            extruded=True,
        ),
    ]
))
 

st.subheader(f'Поездки из зоны {zone}')
DF=pd.DataFrame(data=data[['y', 'preds']][data.zone==zone].loc[f'{date}'].values,
                index=data[['y']][data.zone==zone].loc[f'{date}'].index.strftime('%F %H:%M'),
                columns=['True', 'Preds'])
st.write(DF)
    
fig = go.Figure()
fig.add_trace(go.Scatter(x=DF.index,
                         y=DF.iloc[:,0],
                         name='True',
                         line={'color':'blue'}))
fig.add_trace(go.Scatter(x=DF.index,
                         y=DF.iloc[:,1],
                name='Predictions',
                line={'color':'green'}))

fig.update_layout(title=f'<b>Количество поездок в час из зоны {zone} True vs Preds</b><br>',
                          yaxis_title='trips/h',
                          width=800,
                          autosize=True)
cols2=st.beta_columns(1)
with cols2[0]:
    st.plotly_chart(fig)
    
time=st.sidebar.slider('Время', value=0, min_value=0, max_value=23)

f_date=date+f' {time}:00'
st.title('Поездки такси'+\
         f' {date} в {time}:00')

data2 = pd.read_csv('Taxi.4.csv', index_col=0, parse_dates=True)

reg2=regions.copy()
reg2.index=reg2.index.astype('str')
reg2=reg2.loc[data2.columns.values]
reg2['m']=data2.loc[f'{f_date}']

l=[]
for i, S in reg2.iterrows():
    if S.m!=0:
        l.extend([i]*int(S.m))
        

new=pd.DataFrame(columns=['lat', 'lon', 'm'], index=reg2.index)

new.lon=(reg2.iloc[:,0]+reg2.iloc[:,1])/2
new.lat=(reg2.iloc[:,2]+reg2.iloc[:,3])/2
new.m=reg2['m'].values

l=[]
for i, S in new.iterrows():
    if S.m!=0:
        l.extend([i]*int(S.m))
        
new2=new.loc[l][['lat', 'lon']]
        
st.subheader('--')
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v11",
    initial_view_state={
        "latitude": 40.78,
        "longitude": -73.9,
        "zoom": 9.8,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=new2,
            get_position=["lon", "lat"],
            radius=300,
            elevation_scale=4,
            elevation_range=[0, 2000],
            pickable=False,
            extruded=True,
        ),
    ]
))
