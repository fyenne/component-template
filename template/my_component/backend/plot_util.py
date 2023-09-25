# plot_util
# %%
import altair as alt
import streamlit as st
import seaborn as sns
import pandas as pd
from datetime import datetime,timedelta
import sys
import inspect
import os
import dateutil.parser as dparser
import numpy as np
import warnings
from loguru import logger
from tqdm import tqdm
import sqlalchemy
from sqlalchemy import create_engine 
import re
import calendar
warnings.filterwarnings('ignore')
from samoyan_pack.cred import cred_samo
# df = pd.DataFrame(cred_samo('fetch_all',"101").sql_process())

import plotly.graph_objects as go
import plotly.express as px
from backend.cape_summ_table import color_negative_red,color_columns
import backend.backend_util as backend_util

cwd = os.getcwd()
if re.findall('component-template$', cwd) == []:
    path_prefix = './backend'
else:
    path_prefix = ''
sys.path.append(path_prefix)

def convert_floats_to_int(df):
    # Get columns of type float
    float_cols = df.select_dtypes(include=['float']).columns  
    for col in float_cols:
        # Convert to int
        df[col] = df[col].astype(int)
        
    return df
def plot_general_count(cd1,cd2, renames = 'open_ships'):
    
    plt = go.Figure()
    
    plt.add_trace(go.Bar(
          x = cd2[renames]
        , y = cd2['count']
        , text= cd2['count']
        , textposition='outside' 
        , textfont_size = 25
        , name = "file date of " + cd2['file_time_stamp'].iloc[0]
        , marker=dict(
            color='#F9ABAB'
        )
           ))
    plt.add_trace(go.Bar(
          x = cd1[renames]
        , y = cd1['count']
        , text= cd1['count']
        , textposition='outside' 
        , textfont_size = 25
        , name = "file date of " + cd1['file_time_stamp'].iloc[0]
        , marker=dict(color = '#FF5444')
           )
           )
    plt.update_layout( 
        barmode='group' ,
            showlegend = True,
            legend_orientation = 'h',
            legend_y = +1.20,
            legend_x = -.01,
            margin=dict(l=40, r=0, t=50, b=90), 
            legend_font_size = 17,
            height = 375,
            hovermode = 'x unified',
            title = renames,
            title_x = .5,
            title_y = .12,
            yaxis=dict(
                range=[0, max(cd1['count'].append(cd2['count']))*1.2]
            )
        )
    plt.update_xaxes({
        'tickfont_size': 15

    })
    plt.update_yaxes({
        'tickfont_size': 15
    })
    
    return plt

def plot_summ_count(i, chart_data, renames = 'open_ships', color_pair_controller = 0):
    """
    i is a pair of columns name.
    chart data is data.
    renames are passed to x as x-axis;.
    """
    if renames == 'open_ships':
        width_ = 245
    else:
        width_ = 300
    color_pair = [
        ['#154734','#90ee90'], 
        ['#D3D2D2','#A9A9A9'], 
        ['#795548','#C3B091'], 
        ['#3F51B5','#2196F3']]
    plt = go.Figure()

    plt.add_trace(
        go.Bar(
            x=chart_data[renames],
            y=chart_data[i[0]],
            opacity=0.75,
            marker=dict(
                color=[color_pair[color_pair_controller][0]] * len(chart_data)
            ),
            name=i[0],
            text=chart_data[i[0]],
            textposition="auto",
            textfont_size = 25
        )
    )

    plt.add_trace(
        go.Bar(
            x=chart_data[renames],
            y=chart_data[i[1]],
            marker=dict(
                color=[color_pair[color_pair_controller][1]] * len(chart_data)
            ),
            name=i[1],
            text=chart_data[i[1]],
            textposition="auto",
            textfont_size = 25

        )
    )
    title_ = i[1]
    if i[1] == 'over_15yo':
        title_ = 'age'
    plt.update_layout(
        barmode="stack",
        showlegend = True,
        legend_orientation = 'h',
        legend_y = +1.20,
        legend_x = -.01,
        legend_title = None,
        legend_font_size = 17,
        margin=dict(l=5, r=5, t=50, b=90),
        height = 375,
        width = width_,
        hovermode = 'x unified',
        title = title_,
        title_x = .55,
        title_y = .1,
        
    ) 
    plt.update_xaxes({
        "title":None,
        'tickfont_size': 15
        })
    plt.update_yaxes({
        'tickfont_size': 15
    })
    return plt

def operator_plot(df):
    df_operator_summarized = backend_util.get_df_operator_summarized(df)
    plt = px.bar(df_operator_summarized, x = 'operator', y = 'occurence')
    plt.update_layout(
        title = 'operator count',
        title_xanchor="center",
        title_yanchor="top",
        barmode="stack",
        margin=dict(l=5, r=5, t=50, b=90),
        height = 375,
        hovermode = 'x unified',
        title_x = .55,
        title_y = .1,
    ) 
    plt.update_xaxes({
        "title":None,
        'tickfont_size': 15
        })
    plt.update_yaxes({
        'tickfont_size': 15
    })
    return plt
def table_decorater_(df, mode = 1):

    df['order_key'] = pd.to_datetime(df['order_key'], errors='ignore')
    df =  convert_floats_to_int(df)
    
    th_props = [
        ('font-size', '18px'),
        ('text-align', 'center'),
        ('font-weight', 'bold'),
        ('color', '#6d6d6d'),
        ('background-color', '#f7ffff')
        ]
                                
    td_props = [
        ('font-size', '17px')
    ]
                                    
    styles = [
        dict(selector="th", props=th_props),
        dict(selector="td", props=td_props),
        dict(selector="tbody tr th", props=[("display", "none")]),
        dict(selector="thead tr th.blank", props=[("display", "none")]),
        # dict(selector="thead tr th[id='diff']", props=[("background-color", "green")])

    ]
    
    df = df.sort_values('order_key', ascending = True).drop('order_key', axis = 1)\
        .style.set_properties(
        **{'text-align': 'left', }
        )\
            .set_table_styles(styles)\
                .apply(lambda x: [color_columns(val, x.name) for val in x])\
                    .applymap(
                        color_negative_red,
                        subset=pd.IndexSlice[
                            :, [
                                'diff',# 'new', 'roll', 'gone',
                                # 'scrubber', 'non_scrubbed', 'drafty',
                                # 'not_drafty','over_15yo','under_15yo',
                                ]
                        ]
    )
    return df



def open_period_to_orderkey(x):
    return pd.to_datetime(re.findall("(^\d+)", x)[0] + ' ' + re.findall("([a-zA-Z]+)", x)[0] + ' ' + re.findall("(?<=\w\s)\d+", x)[0])

def convert_floats_to_int(df):
    # Get columns of type float
    float_cols = df.select_dtypes(include=['float']).columns  
    for col in float_cols:
        # Convert to int
        df[col] = df[col].astype(int)
        
    return df

def is_overlap(x, start_date2, end_date2):
    start_date1 = x['early_open']
    end_date1   = x['late_open' ]
    latest_start = max(start_date1, start_date2)
    earliest_end = min(end_date1, end_date2)
    
    if latest_start <= earliest_end:
        return True
    else:
        return False
