# %%
import altair as alt
import streamlit as st
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

def plot_data_prepare_(df, renames = 'open_ships'):
    ll1 = sorted(df["file_time_stamp"].unique(), reverse=True)[:2]
    chart_data = df[df["file_time_stamp"].isin(ll1)] 
    chart_data['file_time_stamp'] = chart_data['file_time_stamp'].astype(str)
    if renames == 'open_ships':
        chart_data[renames] = chart_data['early_open_cats_mon'].astype(str) + ' ' + chart_data['early_open_cats_day'].astype(str)
    else:
        chart_data['ETA_Tub'] = chart_data['early_eta_brz_cats_mon'].astype(str) + ' ' + chart_data['early_eta_brz_cats_day'].astype(str)
    
    chart_data = chart_data.sort_values(renames)
    chart_data['order_key'] = pd.to_datetime(chart_data['file_time_stamp'].str.slice(0,4) + '-' +  chart_data.iloc[:,2] + '-' + chart_data.iloc[:,1].str.slice(0,2))
    chart_data.sort_values('order_key', inplace = True)
    # # remove likely_fixed
    cd1 = chart_data[chart_data['file_time_stamp'] == max(chart_data['file_time_stamp'])]
    cd2 = chart_data[chart_data['file_time_stamp'] != max(chart_data['file_time_stamp'])]
    return cd1, cd2, chart_data
# %%
# 
def get_diff_table(df):
    try:
        diff_table = df[[
            'imo_set', 'order_key', 'file_time_stamp','early_open_cats_day','early_open_cats_mon'
            ]].drop_duplicates().sort_values(['order_key', 'file_time_stamp'], ascending=False).reset_index(drop = True)
    except:
        diff_table = df[[
            'imo_set', 'order_key', 'file_time_stamp','early_eta_brz_cats_day','early_eta_brz_cats_mon'
            ]].drop_duplicates().sort_values(['order_key', 'file_time_stamp'], ascending=False).reset_index(drop = True)
    diff_table_1maxtime_stamp, diff_table_2maxtime_stamp  = diff_table.sort_values('file_time_stamp', ascending = False)['file_time_stamp'].unique()[:2]
    diff_table = diff_table[diff_table['file_time_stamp'] >= diff_table_2maxtime_stamp]
    diff_table.reset_index(inplace = True, drop = True)
    diff_table['new']   = ''
    diff_table['roll1'] = ''
    diff_table['gone']  = ''
    diff_table['roll2'] = ''
    return diff_table
def tolist_(x):
    return x.split(',')
def get_table_done(df):
    diff_table = get_diff_table(df)
    diff_table = diff_table.sort_values('order_key', ascending = False)
    diff_table_1maxtime_stamp, diff_table_2maxtime_stamp  = diff_table.sort_values('file_time_stamp', ascending = False)['file_time_stamp'].unique()[:2]
    m1_df = diff_table.query("file_time_stamp == @diff_table_1maxtime_stamp")
    m2_df = diff_table.query("file_time_stamp == @diff_table_2maxtime_stamp")
    for ind, row in m1_df.iterrows():
        # comparable with diff file and same cate, create new 
        roll1 = []
        new1  = []
        current_order_key = row['order_key']
        if len(re.findall(',', row['imo_set'])) >= 1:
            for i in row['imo_set'].split(','):
                if diff_table.query("order_key != @current_order_key") ['imo_set'].str.contains(i).sum() ==  1: # 总表含此船数量>1, its been observed previously, so roll + 1
                    roll1 += [i]
                elif diff_table['imo_set'].str.contains(i).sum() == 1: # first appearence , so new + 1
                    new1  += [i]
        else:
            i = row['imo_set']
            if diff_table.query("order_key != @current_order_key")['imo_set'].str.contains(i).sum() ==  1: # 总表含此船数量>1, its been observed previously, so roll + 1
                roll1 += [i]
            elif diff_table['imo_set'].str.contains(i).sum() == 1: # first appearence , so new + 1
                new1  += [i]
        m1_df.loc[ind, 'roll1'] = str(roll1)
        m1_df.loc[ind, 'new'] = str(new1)
    #* for goners
    for ind, row in m2_df.iterrows():
            current_order_key = row['order_key']
            roll1 = []
            new1  = []
            if len(re.findall(',', row['imo_set'])) >= 1:
                for i in row['imo_set'].split(','):
                    if diff_table.query("order_key != @current_order_key") ['imo_set'].str.contains(i).sum() == 1: # 总表含此船数量>1, its been observed previously, so roll + 1
                        roll1 += [i]
                    elif diff_table['imo_set'].str.contains(i).sum() == 1: # first appearence , so new + 1
                        new1  += [i]
            else:
                i = row['imo_set']
                if diff_table.query("order_key != @current_order_key")['imo_set'].str.contains(i).sum() == 1: # 总表含此船数量>1, its been observed previously, so roll + 1
                    roll1 += [i]
                elif diff_table['imo_set'].str.contains(i).sum() == 1: # first appearence , so new + 1
                    new1  += [i]
            m2_df.loc[ind, 'roll2'] = str(roll1)
            m2_df.loc[ind, 'gone'] = str(new1) # should be "gone",  naming lazy
            m1_df.loc[m1_df[m1_df['order_key'] == row['order_key']].index, 'gone'] = str(new1)

    diff_table = pd.concat([m1_df,m2_df], axis = 0)
    m1_df = diff_table
    try:
        m1_df['open_period'] = m1_df['file_time_stamp'].dt.year.astype(str) + ' ' + m1_df['early_open_cats_mon'] + ' ' + m1_df['early_open_cats_day']
    except:
        m1_df['open_period'] = m1_df['file_time_stamp'].dt.year.astype(str) + ' ' + m1_df['early_eta_brz_cats_mon'] + ' ' + m1_df['early_eta_brz_cats_day']    

    
    return m1_df

def funct_(x):
    try:
        return len(re.findall('(\d+)', str(x)))
    except:
        return None
    
def summ_table_(df , chart_data):
    summ_table = get_table_done(df)
    # st.write(summ_table)
    try:
        summ_table_cnt = chart_data.pivot_table(
            values=[
                'count' 
            ]
            , index = 'open_ships', columns=['file_time_stamp']).reset_index().fillna(0)
    except:
        summ_table_cnt = chart_data.pivot_table(
            values=[
                'count' 
            ]
            , index = 'ETA_Tub', columns=['file_time_stamp']).reset_index().fillna(0)
        
    summ_table_cnt.columns = ['open_period'] + summ_table_cnt.columns.levels[1:][0].tolist()[0:2] 
    summ_table_cnt['open_period'] = list(summ_table_cnt.columns.str.findall('(\d+)'))[2][0] + ' ' + summ_table_cnt['open_period']
    summ_table_cnt['diff'] =  summ_table_cnt.iloc[:,2] - summ_table_cnt.iloc[:,1] 
    summ_table = summ_table_cnt.merge( summ_table[[
            'new','roll1','gone','roll2', 'open_period', 'imo_set' ,
        ]]
        , on = 'open_period', how = 'left')
    summ_table[['new','roll1','gone','roll2',]]=summ_table[['new','roll1','gone','roll2',]].apply(lambda x: x.replace(0, "[\'\']").replace("[]", "[\'\']"))    
    summ_table[['new_cnt','roll_cnt','gone_cnt','roll2_cnt',]] = summ_table.iloc[:,4:8].applymap(funct_)
    summ_table['roll_cnt'] = summ_table['roll_cnt'] - summ_table['roll2_cnt']
    try:
        summ_table = summ_table.merge(chart_data[chart_data['file_time_stamp'] == max(chart_data['file_time_stamp'])][[
            'open_period', 'scrubber', 'non_scrubbed', 'drafty', 'not_drafty',
            'over_15yo', 'under_15yo', 'isopen_med', 'isopen_nwe', 'order_key', 'likely_fixed']], 
            on = 'open_period', how = 'left')
        summ_table = summ_table[
            [
                'open_period', 
                summ_table.columns[1],
                summ_table.columns[2],
                'diff', 'new_cnt', 'roll_cnt', 'gone_cnt',  
                'scrubber', 'non_scrubbed', 'drafty', 'not_drafty',
                'over_15yo', 'under_15yo', 'isopen_med', 'isopen_nwe', 
                'new', 'roll1',
                'gone', 'order_key', 'likely_fixed'
            ]
        ]
    except:
        summ_table = summ_table.merge(chart_data[chart_data['file_time_stamp'] == max(chart_data['file_time_stamp'])][[
            'open_period', 'scrubber', 'non_scrubbed', 'drafty', 'not_drafty',
            'over_15yo', 'under_15yo','order_key','likely_fixed'
            ]], 
            on = 'open_period', how = 'left') 
        summ_table = summ_table[
            [
                'open_period', 
                summ_table.columns[1],
                summ_table.columns[2],
                'diff', 'new_cnt', 'roll_cnt', 'gone_cnt',  
                'scrubber', 'non_scrubbed', 'drafty', 'not_drafty',
                'over_15yo', 'under_15yo', 
                'new', 'roll1',
                'gone', 'order_key' ,'likely_fixed',
            ]
        ]
    summ_table[[ summ_table.columns[1],
                summ_table.columns[2],
                'diff', ]] = summ_table[[ 
                    summ_table.columns[1],
                    summ_table.columns[2],
                    'diff', ]].astype(int) 
    summ_table['order_key'] = summ_table['open_period'].apply(open_period_to_orderkey)
    # alter real number to subtract likely_fixed ones.
    t = summ_table.groupby(['open_period'])[['gone_cnt', 'new_cnt', 'roll_cnt']].sum()
    summ_table.drop_duplicates(subset = ['open_period'], inplace = True)
    summ_table.drop(['gone_cnt', 'new_cnt', 'roll_cnt'], inplace = True, axis = 1)
    summ_table = summ_table.merge(t, on = ['open_period'], how = 'inner')
    summ_table['gone_cnt'] = -summ_table['gone_cnt']/2
    # summ_table[summ_table.columns[2]] = (summ_table[summ_table.columns[2]] - summ_table['likely_fixed'])
    # summ_table.to_csv('./datadown/summ_table_0731.csv', index = None)
    return summ_table.fillna(0)

def open_period_to_orderkey(x):
    return pd.to_datetime(re.findall("(^\d+)", x)[0] + ' ' + re.findall("([a-zA-Z]+)", x)[0] + ' ' + re.findall("(?<=\w\s)\d+", x)[0])

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    if val < 0:
        color = '#fca5a5'  
    elif val>0 :
        color = '#afeaa1' 
    else :
        color = '#ffffff' 
        pass
    return f'background-color: {color}'


def color_columns(val, column):
    try:
        colors_ = [
            '#90ee9087','#15473487', 
            '#A9A9A987','#D3D2D287', 
            '#C3B09187','#79554887', 
            '#2196F387','#3F51B587',
        ]
        columns_ = [
            'drafty',
            'not_drafty',
            'over_15yo',
            'under_15yo',
            'isopen_med',
            'isopen_nwe',
            'scrubber',
            'non_scrubbed',
        ]
        
        dict_ = dict(zip(columns_, colors_)) 
        return 'background-color: ' + dict_[column]
    except:
        return ''
    


def present_df_(df, imo_lst_table, sheetname = 'Atlantic List', mode = 'gone', get_russian_vessels=''):
    """ 
    imo_lst_table: cd1 or summ_table
    sheetname = 'Ballaster list'
    sheetname = 'Atlantic List'
    * this is to create a table of ship gone./ new ./ roll
    """
    try:
        imo_ls_cd1 = imo_lst_table['imo_set'].apply(lambda x: re.findall('(\d+)', x)).sum() 
    except:
        if mode == 'gone':
            imo_ls_cd1 = imo_lst_table['gone'].apply(lambda x: re.findall('(\d{2,})', str(x))).sum()  
        if mode == 'new' :
            imo_ls_cd1 = imo_lst_table['new' ].apply(lambda x: re.findall('(\d{2,})', str(x))).sum()  
        if mode == 'roll':
            imo_ls_cd1 = imo_lst_table['roll1'].apply(lambda x: re.findall('(\d{2,})', str(x))).sum()  
    present_df = df[
        (
            df['file_time_stamp'].isin((df['file_time_stamp'].unique()[0:2]))
        ) & (
            df['imo'].isin(imo_ls_cd1)
        ) & (
            df['sheet_name'].isin([sheetname])
        )
        ].drop_duplicates(subset=['imo']).sort_values(['early_open'], ascending = True)
    if sheetname == 'Ballaster list': # COGH
        present_df.sort_values(['early_second_eta'], ascending = True, inplace = True)
        df = present_df[['likely_fixed', 'imo', 'Name', 'dwt', 'draught', 'scrubber', 
            'age', 'Open',
            'Open Date', 'second_ETA', 'Speed', #'ETA Tubarao',  # 'early_open', 'late_open','file_time_stamp','sheet_name' 
            'current_operator','ais_destination_now', 'russia_port', 'Notes',
            'early_open', 'late_open', 'early_second_eta', 'late_second_eta',]]
        df.rename({'second_ETA' : 'ETA_Tubarao'}, axis = 1, inplace = True) 
    else: 
        df = present_df[['likely_fixed', 'imo', 'Name', 'dwt', 'draught', 'scrubber', 
            'age', 'isopen_med', 'isopen_nwe', 'Open', 
            'Open Date','ETA Gibraltar', 'Speed','current_operator', 'ais_destination_now', 'russia_port','Notes', 
            'early_open', 'late_open', 
            'early_second_eta', 'late_second_eta',]]
    df['russia_port'] = df['russia_port'].fillna(False).astype(bool)
    return df

def ship_present_df_with_aspects(df,summ_table,sheetname = 'Atlantic List', mode='new'):
    ca2 = present_df_(df,summ_table,sheetname, mode)
    # try:
    #     ca2 = ca2.drop(['early_open', 'late_open'], axis = 1), 
    # except:
    #     pass
    if sheetname == 'Atlantic List': 
        st.data_editor(
            ca2.drop(['early_open', 'late_open'], axis = 1).style.set_properties(
                **{'text-align': 'left', 'text-color': 'green'}
                ).applymap(
                        color_negative_red,
                        subset=pd.IndexSlice[
                            :, [
                                'age',# 'new', 'roll', 'gone',
                                # 'scrubber', 'non_scrubbed', 'drafty',
                                # 'not_drafty','over_15yo','under_15yo',
                                ]
                        ]
                        ), 
            hide_index=True, 
            column_config={
                "likely_fixed": st.column_config.CheckboxColumn(
                    disabled=True
                ),
                "scrubber": st.column_config.CheckboxColumn(
                    disabled=True
                ),
                "isopen_nwe": st.column_config.CheckboxColumn(
                    disabled=True
                ),
                "isopen_med": st.column_config.CheckboxColumn(
                    disabled=True
                )
                
            },
            use_container_width=True,

            )
    else:
        st.data_editor(
            ca2.drop(['early_open', 'late_open'], axis = 1), 
            hide_index=True, 
            column_config={
                "likely_fixed": st.column_config.CheckboxColumn(
                    disabled=True
                ),
                "scrubber": st.column_config.CheckboxColumn(
                    disabled=True
                )
            },
            use_container_width=True,
            height=len(ca2)*44 + 40

            ) 

def update_sqlserver_on_fixed_vessels(edited_cell_list_imo , file_time_stamp, mode=2):
    """
    get the df of modified imo and name and iffixed 
    very stupid to write this strategy to update the selected col values,
    """
    engine = create_engine("mssql+pyodbc://research:research@GEN-NT-SQL11\MATLAB:56094/BrokerData?driver=SQL+Server+Native+Client+10.0")    
    if mode != 2:    
        query = """
            SELECT   [imo]
                ,upper([name])  as Name
            FROM [BrokerData].[dbo].[ods_arrow_cape_list_dtl_wi] 
            group by  [imo]
                ,[name] 
        """
        df = pd.read_sql(query, engine) 
        df['Name'] = df['Name'].str.replace('\s+$', '')
        df = df.merge(edited_cell_list_imo, on = 'Name', how = 'right')
        df = pd.concat([df.where(df['imo_x'] != df['imo_y']).dropna(), df[df['imo_x'].isna()]])
        for _, row in df.iterrows():
            new_imo = str(row['imo_y'])
            thename = str(row['Name'])
            # print(new_imo)
            query = f"""
                        UPDATE [BrokerData].[dbo].[ods_arrow_cape_list_dtl_wi] 
                        SET imo = '{new_imo}'
                        WHERE name = '{thename}'
                        """
            with engine.connect() as con:
                con.execute(query)

    elif mode == 2:
        edited_cell_list_imo.reset_index(drop = True, inplace = True)
        # edited_cell_list_imo['likely_fixed'] = edited_cell_list_imo['likely_fixed'].astype(bool)
        edited_cell_list_imo_fixed_list = edited_cell_list_imo[edited_cell_list_imo['likely_fixed'] == 'True']['imo'].astype(str).tolist()
        edited_cell_list_imo_fixed_list = '\',\''.join(edited_cell_list_imo_fixed_list)
        query = f"""
                UPDATE [BrokerData].[dbo].[ods_arrow_cape_list_dtl_wi] 
                SET likely_fixed = 
                case 
                    when (imo in ('{edited_cell_list_imo_fixed_list}', '99999999') and file_time_stamp = '{file_time_stamp} 00:00:00') 
                        then 
                        1
                    else 
                        0
                end
                """
        with engine.connect() as con:
            con.execute(query)
    return 1 

@st.cache_data(ttl=86400)
def get_russian_vessels(imo_list):
    """
    push a list  into this function to see if the vessels been to the russian port.
    return a list of imo that are in the russian port.
    """
    imo_list = "','".join(imo_list)
    engine = create_engine("mssql+pyodbc://research:research@GEN-NT-SQL11\MATLAB:56094/BrokerData?driver=SQL+Server+Native+Client+10.0")
    sql = f"""
        SELECT shipno
            FROM brokerData.dbo.dim_berthreport_ships_to_ru_wi;
        """
    df = pd.read_sql(sql, engine)
    df['russia_port'] = True
    df = df[['shipno', 'russia_port']].astype(str).drop_duplicates()
    return df