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
from sqlalchemy import create_engine 
import re
import calendar
warnings.filterwarnings('ignore')
from samoyan_pack.cred import cred_samo
# df = pd.DataFrame(cred_samo('fetch_all',"101").sql_process())
import plotly.graph_objects as go
import plotly.express as px
# sys.path.append("D:\\samo\\bunge_freight_dashboard_ext\\pages_component\\")

 

import pandas as pd


def get_speed_of_vessels(imo_ls: list, engine):
    imo_ls = ','.join(imo_ls)
    # engine = create_engine("mssql+pyodbc://research:research@GEN-NT-SQL11\MATLAB:56094/BrokerData?driver=SQL+Server+Native+Client+10.0")    
    query = f"""
            SELECT   [ShipID]
            ,[MMSI]
            ,[ShipName]
            ,[Latitude]
            ,[Longitude]
            ,[Speed]
            ,[MovementdateTime]
            FROM [VTPositionDB].[dbo].[VTvesselposition_last]
            where [ShipID] in ({imo_ls})
        """
    df = pd.read_sql(query, engine) 
    return df

def categorize_date(date):
    day = date.day
    if 1 <= day <= 10:
        return 'cat01-10'
    elif 11 <= day <= 20:
        return 'cat11-20'
    else:   
        return f'cat21-{date.daysinmonth}'

def get_df(remove_likely_fixed = 1):
    global llfixed
    if remove_likely_fixed == 1 :
        remove_likely_fixed = "where likely_fixed != 1"
    else:
        remove_likely_fixed = ''
    engine = create_engine("mssql+pyodbc://research:research@GEN-NT-SQL11\MATLAB:56094/BrokerData?driver=SQL+Server+Native+Client+10.0")
    df = pd.read_sql(f"select * from ods_arrow_cape_list_dtl_wi {remove_likely_fixed}", engine)
    df['early_open_cats_day'] = df['early_open'].apply(categorize_date)
    df['late_open_cats_day' ] = df['late_open'] .apply(categorize_date)
    df['early_open_cats_mon'] = df['early_open'].dt.strftime('%m')
    df['late_open_cats_mon' ] = df['late_open'] .dt.strftime('%m')

    df['scrubber']   = np.where(df['scrubber'].str.lower().str.strip() == 'fitted', True, False)
    df['non_scrubbed'] = -df['scrubber']
    df['drafty']     = np.where(df['draught']  >= 17.8, True, False)
    df['not_drafty'] = -df['drafty']
    df['over_15yo' ] = np.where(df['age']  >= 15, True, False)
    df['under_15yo'] = -df['over_15yo']
    df['isopen_med'] = df.Open.isin(["GIB"
        ,"ALGECIRAS"
        ,"HADERA"
        ,"ARZEW"
        ,"PORT SAID"
        ,"GIJON"
        ,"GIBRALTAR"
        ,"TARANTO"
        ,"CONT"
        ,"CONTINENT"
        ,"MISURATA"])
    df['isopen_nwe'] = -df['isopen_med']
    df['imo'] = df['imo'].astype(str)
    df['likely_fixed'].fillna(False, inplace=True)
    df['ETA Gibraltar'] = df['early_first_eta'] - timedelta(days = 16)

    df['second_ETA'] = df['second_ETA'].str.replace('\d+\:\d+\:.+', '')
    df['first_ETA'] = df['first_ETA'].str.replace('\d+\:\d+\:.+', '')
    df['Open Date'] = df['Open Date'].str.replace('\d+\:\d+\:.+', '')
    df['ETA Gibraltar'] = df['ETA Gibraltar'].astype(str).str.replace('\d+\:\d+\:.+', '')

    df['draught'] = df['draught'].round(2)
    df.sort_values('file_time_stamp', ascending=False, inplace=True)
    diff_table_1maxtime_stamp, diff_table_2maxtime_stamp  = df.sort_values('file_time_stamp', ascending = False)['file_time_stamp'].unique()[:2]
    df = df[df['file_time_stamp'] >= diff_table_2maxtime_stamp]
    try:
        df_get_speed_of_vessels = get_speed_of_vessels(df['imo'].tolist(), engine = engine)
        df_get_speed_of_vessels['ShipID'] = df_get_speed_of_vessels['ShipID'].astype(str)
        df = df.merge(df_get_speed_of_vessels, left_on ='imo' ,  right_on = 'ShipID', how = 'left')
    except Exception as e:
        st.write(str(e))
        pass
    # df.to_clipboard()
    return df

# %%

def convert_floats_to_int(df):
    # Get columns of type float
    float_cols = df.select_dtypes(include=['float']).columns  
    for col in float_cols:
        # Convert to int
        df[col] = df[col].astype(int)
        
    return df
def get_df_operator_summarized(df, mode = 'Atlantic List'):
    """
    take get_df() raw data as input.
    """
    df = df[(df['sheet_name'] == mode) & (df['file_time_stamp'] == df['file_time_stamp'].max())] 
    df['current_operator'] = df['current_operator'].astype(str).str.split('/').fillna('')
    ls = []
    for j in df['current_operator']:
        if len(j) > 1:
            ls += [i.strip() for i in j ]
        else:
            ls += j
    
    df = pd.DataFrame(pd.Series(ls).value_counts()).reset_index()
    df.columns = ['operator', 'occurence']
    return df


def get_df_atl_summarized(df):
    """
    take get_df() raw data as input.
    """
    df_atl = df[df['sheet_name'] == 'Atlantic List']
    
    df_atl_summary = df_atl.groupby([
        'file_time_stamp',
        'early_open_cats_day',
        # 'late_open_cats_day',
        'early_open_cats_mon',
        # 'late_open_cats_mon',
                ], as_index=False).agg(
        {
            'imo': ('nunique', set),
            'scrubber':'sum', 	# Summarize the scrubber's state.  Not all scrubbers are "Fitted" or "Not Fitted"
            'non_scrubbed':'sum', 	# Summarize the scrubber's state.  Not all scrubber's are "
            'drafty':'sum', 	
            'not_drafty':'sum',  
            'over_15yo': 'sum', 		# 
            'under_15yo': 'sum', 	
            'isopen_med':'sum', 		  
            'isopen_nwe':'sum',
            'likely_fixed':'sum',
        }

        ).sort_values(['file_time_stamp', 'early_open_cats_mon', 'early_open_cats_day'], ascending=[False, True, True])
    df_atl_summary.columns =  df_atl_summary.columns.get_level_values(0)
    df_atl_summary.columns = ['file_time_stamp', 'early_open_cats_day', 'early_open_cats_mon',
        'imo', 'imo_set', 'scrubber', 'non_scrubbed', 'drafty', 'not_drafty',
        'over_15yo', 'under_15yo', 'isopen_med', 'isopen_nwe','likely_fixed']
    
    df_atl_summary['change'] = df_atl_summary.groupby(
        ['early_open_cats_day', 'early_open_cats_mon'], as_index=False
        )['imo'].diff(-1).fillna(0)
    df_atl_summary.rename({"imo":"count"}, axis = 1 ,inplace=True)
    
    df_atl_summary['early_open_cats_day'] = df_atl_summary['early_open_cats_day'].str.replace('cat', '')
    df_atl_summary['early_open_cats_mon'] = df_atl_summary['early_open_cats_mon'].apply(lambda x: calendar.month_name[int(x)])
    df_atl_summary['order_key'] = pd.to_datetime(
            df_atl_summary['file_time_stamp'].astype(str).str.slice(0,4) + '-' +  df_atl_summary.iloc[:,2] + '-' + df_atl_summary.iloc[:,1].str.slice(0,2)
            )
    df_atl_summary['imo_set'] = df_atl_summary['imo_set'].apply(lambda x : ','.join(x))
    df_atl_summary['open_period'] = df_atl_summary['file_time_stamp'].dt.year.astype(str) + ' ' + df_atl_summary['early_open_cats_mon'] + ' ' + df_atl_summary['early_open_cats_day']
    df_atl_summary['count'] = df_atl_summary['count'] - df_atl_summary['likely_fixed'] 
    return df_atl_summary

# %%
def get_df_pac_summarized(df):
    df_pac = df[df['sheet_name'] == 'Ballaster list']

    filler = df_pac[['first_dest', 'first_ETA', 'early_first_eta', 'late_first_eta']] 
    filler.columns = ['second_dest', 'second_ETA', 'early_second_eta', 'late_second_eta']
    df_pac[[
        'second_dest', 'second_ETA', 'early_second_eta', 'late_second_eta'
        ]] = df_pac[['second_dest', 'second_ETA', 'early_second_eta', 'late_second_eta']].fillna(
        filler
    )
    df_pac['early_eta_brz_cats_day'] = df_pac['early_second_eta'].apply(categorize_date)
    df_pac['late_eta_brz_cats_day' ] = df_pac['late_second_eta'] .apply(categorize_date)
    df_pac['early_eta_brz_cats_mon'] = df_pac['early_second_eta'].dt.strftime('%m')
    df_pac['late_eta_brz_cats_mon' ] = df_pac['late_second_eta'] .dt.strftime('%m')
    df_pac = df_pac[~((df_pac['likely_fixed'] == 1) & (df_pac['file_time_stamp'] < max(df_pac['file_time_stamp'])))]
    df_pac_summary = df_pac.groupby([
        'file_time_stamp',
        'early_eta_brz_cats_day',
        'early_eta_brz_cats_mon',
                ], as_index=False).agg(
        {
            'imo': ('nunique', set),
            'scrubber':'sum', 	# Summarize the scrubber's state.  Not all scrubbers are "Fitted" or "Not Fitted"
            'non_scrubbed':'sum', 	# Summarize the scrubber's state.  Not all scrubber's are "
            'drafty':'sum', 	
            'not_drafty':'sum',  
            'over_15yo': 'sum', 		# 
            'under_15yo': 'sum',  # 
            'likely_fixed':'sum',
        }

        ).sort_values(['file_time_stamp','early_eta_brz_cats_mon', 'early_eta_brz_cats_day', ], ascending=[False, True, True])
    df_pac_summary.columns =  df_pac_summary.columns.get_level_values(0)
    df_pac_summary.columns = ['file_time_stamp', 'early_eta_brz_cats_day', 'early_eta_brz_cats_mon',
        'imo', 'imo_set', 'scrubber', 'non_scrubbed', 'drafty', 'not_drafty',
        'over_15yo', 'under_15yo','likely_fixed']
    df_pac_summary['change'] = df_pac_summary.groupby(
        ['early_eta_brz_cats_day', 'early_eta_brz_cats_mon'], as_index=False
        )['imo'].diff(-1).fillna(0)
    df_pac_summary.rename({"imo":"count"}, axis = 1 ,inplace=True)
    # make nested df columns to a list
    df_pac_summary['early_eta_brz_cats_day'] = df_pac_summary['early_eta_brz_cats_day'].str.replace('cat', '')
    df_pac_summary['early_eta_brz_cats_mon'] = df_pac_summary['early_eta_brz_cats_mon'].apply(lambda x: calendar.month_name[int(x)])
    df_pac_summary['order_key'] = pd.to_datetime(
        df_pac_summary['file_time_stamp'].astype(str).str.slice(0,4) + '-' +  df_pac_summary.iloc[:,2] + '-' + df_pac_summary.iloc[:,1].str.slice(0,2)
        )
    
    df_pac_summary['imo_set'] = df_pac_summary['imo_set'].apply(lambda x : ','.join(x))
    df_pac_summary['open_period'] = df_pac_summary['file_time_stamp'].dt.year.astype(str) + ' ' + df_pac_summary['early_eta_brz_cats_mon'] + ' ' + df_pac_summary['early_eta_brz_cats_day']
    df_pac_summary['count'] = df_pac_summary['count'] - df_pac_summary['likely_fixed'] 
    
    return df_pac_summary




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