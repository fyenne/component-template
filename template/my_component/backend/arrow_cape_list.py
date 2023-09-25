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
from pages_component.get_vessel_speed import get_speed_of_vessels
# %%
sys.path.append("D:\\samo\\bunge_freight_dashboard_ext\\pages_component\\")



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


def plot_general_count(cd1,cd2, renames = 'open_ships'):
    
    plt = go.Figure()
    
    plt.add_trace(go.Bar(
          x = cd2[renames]
        , y = cd2['count']
        , text= cd2['count']
        , textposition='outside' 
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
            height = 375,
            hovermode = 'x unified',
            title = renames,
            title_x = .5,
            title_y = .12,
            yaxis=dict(
                range=[0, max(cd1['count'].append(cd2['count']))*1.2]
            )
        )
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
        margin=dict(l=5, r=5, t=50, b=90),
        height = 375,
        width = width_,
        hovermode = 'x unified',
        title = title_,
        title_x = .55,
        title_y = .1,
        
    ) 
    plt.update_xaxes({"title":None})
    return plt

def table_decorater_(df, mode = 1):

    from pages_component.cape_summ_table import color_negative_red,color_columns
    df['order_key'] = pd.to_datetime(df['order_key'], errors='ignore')
    df = convert_floats_to_int(df)
    
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

# %%
# if __name__ == '__main__':
def main_cape_():
    import pages_component.cape_summ_table as cape_summ_table
    from button_send_email import button_send_email
    
    cm = sns.light_palette("green", as_cmap=True)
    st.markdown("""
        <center> <span style="font-size:30pt; font-family: impact; color: blue; text-shadow: 4px 4px grey; padding: 20px; letter-spacing: 10px;"> 
        <mark> CAPES' LIST </mark> </span> </center></ br> 
        """, unsafe_allow_html=True)
    df = get_df(2)
    df_atl_summary = get_df_atl_summarized(df)
    df_pac_summary = get_df_pac_summarized(df)
    russianships = cape_summ_table.get_russian_vessels(df['imo'].unique().tolist())
    df = df.merge(russianships, how = 'left', left_on = 'imo', right_on = 'shipno')
    # ---------------------------------------------------------------------------- #
    #                                     atlan                                    #
    # ---------------------------------------------------------------------------- #
    
    tab1, tab2,  = st.tabs([
        " ✅ Atlantic open ships",
        " ✅ COGH open ships ", 
        # "✅ data"
        ])
    with tab1: # atlantic open ships
        
        col2,col3= st.columns([3, 1])
        with col2:
            cd1,cd2,chart_data = cape_summ_table.plot_data_prepare_(df_atl_summary)
            summ_table = cape_summ_table.summ_table_(df_atl_summary, chart_data)
            summ_table_present = summ_table[
                [
                    'open_period', 
                    summ_table.columns[1],
                    summ_table.columns[2],
                    'diff', 'gone_cnt',  'new_cnt', 'roll_cnt', 'likely_fixed',
                    'scrubber', 'non_scrubbed', 'drafty', 'not_drafty',
                    'over_15yo', 'under_15yo', 'isopen_med', 'isopen_nwe', 'order_key',
                    # 'new', 'roll1',
                    # 'gone', # 'roll2'
                ]
            ]
            summ_table_present.rename({'new_cnt': 'new', 'roll_cnt': 'roll', 'gone_cnt':'gone'}, inplace = True, axis = 1)

            st.table(
                table_decorater_(summ_table_present,1)
            )
            st.write("last refresh: ", df['last_modified_time'].max())
        file_time_stamp = chart_data['file_time_stamp'].max()
        chart_data = chart_data[chart_data["file_time_stamp"]==file_time_stamp]    

        with col3:
            i = ["non_scrubbed", "scrubber"]
            plt = plot_summ_count(i,chart_data, color_pair_controller=-1)
            st.plotly_chart(plt, use_container_width=True) 

        col1, col2, col3, col4 = st.columns([3,1,1,1])
        col_list = [col2,col3,col4]
        # col5,col6 = st.columns(2)
        with col1:
            plt = plot_general_count(cd1,cd2)
            st.plotly_chart(plt, use_container_width=True)
            df_operator_summarized = get_df_operator_summarized(df)
            st.plotly_chart(px.bar(df_operator_summarized, x = 'operator', y = 'occurence'))
        # with col6:
        #     st.write(chart_data)
        m = 0
        for i in [
            ["not_drafty","drafty"],
            ["under_15yo","over_15yo"], 
            ['isopen_med','isopen_nwe']
            ]:
                plt = plot_summ_count(i,chart_data,color_pair_controller = m)
                with col_list[m]:
                    st.plotly_chart(plt, use_container_width=True)
                    m+=1
    # * tables
        st.write('Currente Atlantic Open Ships')
        ca = cape_summ_table.present_df_(df, cd1)
        df_open_time_min, df_open_time_max  = pd.to_datetime(
            df['early_open'].min()
            ), pd.to_datetime(df['late_open'].max()) + timedelta(days=60) 
        try:
            col1,col2, col3, _ = st.columns([2,2,2,6])
            with col1:
                start_date,end_date = st.date_input(
                    "date range ",
                    (df_open_time_min, df_open_time_max),
                    df_open_time_min, df_open_time_max
                    )
            with col2:
                st.write('reset filter button')
                reset_date_sele = st.button('\n reset')
                if reset_date_sele:
                    start_date,end_date=df_open_time_min, df_open_time_max
        except:
            start_date,end_date=df_open_time_min, df_open_time_max
        


        check_interval = pd.Interval(pd.to_datetime(start_date)- timedelta(days=1),pd.to_datetime(end_date) + timedelta(days=1))
        ca['overlap'] = ca.apply(lambda row: pd.Interval(
                row['early_open'], 
                row['late_open']
            ).overlaps(check_interval), axis=1)
        ca = ca[ca['overlap']].drop(['overlap'], axis = 1) 
        len_ = 300 if len(ca)*45 < 300 else len(ca)*45
        
        #@ drop unessagry part
        #       table[role="grid"] thead th[role="columnheader"] {
        # st.markdown("""
        #         <style>
        #         .glideDataEditor.wzg2m5k{
        #         font-size: 22px;
        #         background-color: red;
        #         padding: 1rem;
        #         }
        #         </style>
        #         """, unsafe_allow_html=True)
        edited_df = st.data_editor(
            ca.drop(['early_open', 'late_open', 'early_second_eta', 'late_second_eta'], axis = 1), #.drop(['early_open', 'late_open'], axis = 1), 
            column_config={
                "scrubber":   st.column_config.CheckboxColumn(
                    label="scrubber",
                    disabled=True,
                ),
                "isopen_nwe": st.column_config.CheckboxColumn(
                    disabled=True
                ),
                "isopen_med": st.column_config.CheckboxColumn(
                    disabled=True
                ),
                "Name": {'header_style': 'font-weight: bold; font-size: 20px;'},

            },
            hide_index=True, 
            use_container_width=True,
            key = 'edited_df_plot1',
            height = len_
            )#
        # edited_cell_list_imo = edited_df[edited_df['likely_fixed']]['imo'].astype(str).tolist()
        edited_cell_list_imo = edited_df[['likely_fixed','imo', 'Name']].astype(str)
        # for update_sqlserver_on_fixed_vessels
        if len(edited_df[edited_df['likely_fixed']]) != len(ca[ca['likely_fixed']]):
            modeupdate_sqlserver_on_fixed_vessels = 2
        else:
            modeupdate_sqlserver_on_fixed_vessels = 1
        st.write(modeupdate_sqlserver_on_fixed_vessels)
        col1,col2,_ = st.columns([1,1,4])
        with col1:
            button_of_selected_likely_fixed = st.button('apply the change', key = 'button_of_selected_likely_fixed1')
        with col2:
            @st.cache_data
            def write_and_download1(ca):
                return edited_df.to_csv(index = None).encode('utf-8')
            write_and_download_data = write_and_download1(ca)
            st.download_button(
                    label = 'download the data', 
                    key = 'button_of_download1',
                    data = write_and_download_data,
                    file_name='cape_list_atlantic.csv',
                    mime = 'text/csv'
                )
        
        if (button_of_selected_likely_fixed):
            cape_summ_table.update_sqlserver_on_fixed_vessels(
                st.session_state.likely_fixed_list, 
                file_time_stamp,
                modeupdate_sqlserver_on_fixed_vessels
                )
            st.success('refreshing the page to apply the change', icon=None)
            st.experimental_rerun() 
         
        
        st.write('Ships New From Last')
        cape_summ_table.ship_present_df_with_aspects(df,summ_table, mode='new')
        
        df_likely_fixed = df[list(ca.columns) + ['file_time_stamp', 'sheet_name']]
        df_likely_fixed = df_likely_fixed[
            (df_likely_fixed['file_time_stamp'] == f'{file_time_stamp}')
            &
            (df_likely_fixed['likely_fixed'] == 1)
            ]
            #
        st.write('Ships Likely Fixed')
        
        st.data_editor(
            df_likely_fixed[df_likely_fixed['sheet_name'] != 'Ballaster list'][list(ca.columns)].drop(['early_open', 'late_open',], axis = 1)#[list(ca2.columns)]
            , hide_index=True
            , use_container_width=True
            , column_config={
                "likely_fixed": st.column_config.CheckboxColumn(
                    disabled=True
                )
            }
            )
        
        st.write('Ships roll From Last')
        cape_summ_table.ship_present_df_with_aspects(df,summ_table, mode='roll')

    
        st.write('Ships Gone From Last')
        cape_summ_table.ship_present_df_with_aspects(df,summ_table, mode='gone')
        button_send_email(mode = 'N.Atlantic' , edited_df=edited_df)
    
        st.write('---')
 
    # ---------------------------------------------------------------------------- #
    #                                     plot2                                    #
    # ---------------------------------------------------------------------------- #
    with tab2:
        # st.write("###")
        col2,col3 = st.columns([3,1])
        with col2:

            cd1,cd2,chart_data = cape_summ_table.plot_data_prepare_(df_pac_summary, 'ETA_Tub')
            summ_table = cape_summ_table.summ_table_(df_pac_summary, chart_data)
            summ_table_present = summ_table[
                [
                    'open_period', 
                    summ_table.columns[1],
                    summ_table.columns[2],
                    'diff', 'gone_cnt', 'new_cnt', 'roll_cnt',   'likely_fixed',
                    'scrubber', 'non_scrubbed', 'drafty', 'not_drafty',
                    'over_15yo', 'under_15yo', 'order_key'
                    # 'new', 'roll1',
                ]
            ]
            summ_table_present.rename({'new_cnt': 'new', 'roll_cnt': 'roll', 'gone_cnt':'gone'}, inplace = True, axis = 1)
            # summ_table_present.to_csv('./datadown/summ_table_present_0731.csv', index = None)
            
            st.table(
                table_decorater_(summ_table_present)
                )
            st.write("last refresh: ", df['last_modified_time'].max())
            
        chart_data = chart_data[chart_data["file_time_stamp"]==max(chart_data["file_time_stamp"])]
        
        with col3:
            i = ["non_scrubbed", "scrubber"]
            plt = plot_summ_count(i,chart_data, 'ETA_Tub',color_pair_controller=-1)
            st.plotly_chart(plt, use_container_width=True)
        col1, col2, col3 = st.columns([2,1,1])
        col_list = [col2,col3]

        with col1:
            plt = plot_general_count(cd1,cd2,'ETA_Tub')
            st.plotly_chart(plt, use_container_width=True)
            df_operator_summarized = get_df_operator_summarized(df, 'Ballaster list')
            st.plotly_chart(px.bar(df_operator_summarized, x = 'operator', y = 'occurence'))
        m = 0
        for i in [["not_drafty",
                        "drafty"],
                        ["under_15yo",
                        "over_15yo"]]:
                plt = plot_summ_count(i,chart_data,'ETA_Tub',color_pair_controller = m)
                with col_list[m]:
                    st.plotly_chart(plt, use_container_width=True)
                    m+=1
        
        st.write('Currente COGH Open Ships')
        ca_2 = cape_summ_table.present_df_(df, cd1, 'Ballaster list')
        try:
            col1,col2, col3, _ = st.columns([2,2,2,6])

            with col1:
                start_date,end_date = st.date_input(
                    "date range ",
                    (df_open_time_min, df_open_time_max),
                    df_open_time_min, df_open_time_max,
                    key = "date range 2"
                    )
            with col2:
                st.write('reset date filter')
                reset_date_sele = st.button('reset')
                if reset_date_sele:
                    start_date,end_date=df_open_time_min, df_open_time_max
        except Exception as e:
            st.write(e)
            start_date,end_date=df_open_time_min, df_open_time_max
        # check_interval = pd.Interval(pd.to_datetime(start_date),pd.to_datetime(end_date))
        check_interval = pd.Interval(
            pd.to_datetime(start_date)- timedelta(days=1),
            pd.to_datetime(end_date) + timedelta(days=1)
            )
        # st.write(ca_2)
        ca_2['overlap'] = ca_2.apply(lambda row: pd.Interval(
            row['early_second_eta'], row['late_second_eta']
            ).overlaps(check_interval), axis=1)
        ca_2 = ca_2[ca_2['overlap']].drop(['overlap'], axis = 1) #@ d
        len_ = 300 if len(ca_2)*45 < 300 else len(ca_2)*45
        edited_df_2 = st.data_editor(
            ca_2.drop(['early_open', 'late_open', 'early_second_eta', 'late_second_eta'], axis = 1), 
            # num_rows="dynamic",
            column_config={
                "scrubber": st.column_config.CheckboxColumn(
                    label = "*scrubber*",
                    disabled=True
                )
            },
            hide_index=True, 
            use_container_width=True,
            key = 'edited_df_plot2',
            height=len_
            )#
        # edited_cell_list_imo_2 =  edited_df_2[edited_df_2['likely_fixed']]['imo'].astype(str).tolist()
        edited_cell_list_imo_2 = edited_df_2[['likely_fixed','imo', 'Name']].astype(str)
        if len(edited_df_2[edited_df_2['likely_fixed']]) != len(ca_2[ca_2['likely_fixed']]):
            modeupdate_sqlserver_on_fixed_vessels = 2
        else:
            modeupdate_sqlserver_on_fixed_vessels = 1
        st.write(modeupdate_sqlserver_on_fixed_vessels)
        col1,col2,_ = st.columns([1,1,4])
        with col1:
            button_of_selected_likely_fixed = st.button('apply the change', key = 'button_of_selected_likely_fixed2')
        with col2:
            @st.cache_data
            def write_and_download1(ca_2):
                return edited_df_2.to_csv(index =None).encode('utf-8')
            write_and_download_data = write_and_download1(ca_2) 
            st.download_button(
                    label = 'download the data', 
                    key = 'button_of_download2',
                    data = write_and_download_data,
                    file_name='cape_list_cogh.csv',
                    mime = 'text/csv'
                )

        if (button_of_selected_likely_fixed):
            cape_summ_table.update_sqlserver_on_fixed_vessels(
                st.session_state.likely_fixed_list, 
                file_time_stamp,
                modeupdate_sqlserver_on_fixed_vessels
                )
            st.success('refreshing the page to apply the change', icon=None)
            st.experimental_rerun()

        
        st.write('Ships New From Last')
        cape_summ_table.ship_present_df_with_aspects(df,summ_table, sheetname='Ballaster list', mode='new')

        st.write('Ships Likely Fixed')
        st.data_editor(
            df_likely_fixed[df_likely_fixed['sheet_name'] == 'Ballaster list'].drop(['early_open', 'late_open', 'sheet_name', 'file_time_stamp'], axis = 1)#[list(ca2.columns)]
            , hide_index=True
            , use_container_width=True
            , key = 'Ships likely_fixed_table'
            , column_config={
                "likely_fixed": st.column_config.CheckboxColumn(
                    disabled=True
                )
            }

            )
        
        st.write('Ships Roll From Last')
        cape_summ_table.ship_present_df_with_aspects(df,summ_table, sheetname='Ballaster list', mode='roll')

        
        st.write('Ships Gone From Last')
        cape_summ_table.ship_present_df_with_aspects(df,summ_table, sheetname='Ballaster list', mode='gone')
        button_send_email(mode = 'COGH', edited_df=ca_2)

        st.write('---')

        
        st.session_state.likely_fixed_list = pd.concat(
                [edited_cell_list_imo , edited_cell_list_imo_2]
            )
        # st.session_state.likely_fixed_list.to_clipboard()
        # st.write(st.session_state.likely_fixed_list)