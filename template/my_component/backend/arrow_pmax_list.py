from plot_modify import *

import streamlit as st 
import pandas as pd 
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import numpy as np
import warnings  
from datetime import datetime,timedelta
import sys
from original_data_downloader import run_original_data_downloader
import os
warnings.filterwarnings('ignore')



# ---------------------------------------------------------------------------- #
#                                     conn                                     #
# ---------------------------------------------------------------------------- #

 
def clear_cache():
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.clear()

# !---------------------------------------------------------------------------- #
# !                                     func                                    #
# !---------------------------------------------------------------------------- #
def get_truncated_timestamp(end=None, refresh_interval=360, 
                refresh_interval_units='minutes'):
    """
    ref: https://discuss.streamlit.io/t/clear-cache-with-a-time-interval-at-least-once-per-hour/2144/4
    A time truncated down to resolution to control caching

    Parameters:
        end (datetime.datetime):  The time to validate against

    Returns:
        datetime.datetime: a timestamp set to the nearest refresh_interval.

    If end is at or before midnight at the start of the
    current day returns **None** as we'll never want to change that
    cache anyway.

    """
    today__ = datetime.today()
    if end and end <= datetime(today__.year, today__.month, today__.day, 12, 0, 0):
        #  Fix timestamp for data not updating...
        timestamp = None
    else:
        timestamp = datetime.now()
        if refresh_interval_units == 'minutes':
            interval = int(refresh_interval)
            timestamp = timestamp.replace(
                            minute=(timestamp.minute // interval) * interval,
                            second=0, microsecond=0, )
    return timestamp

@st.cache_data(ttl=86400)
def run_manual_table_plt(mode = 1):
    """
    for the total fig, left hand.
    todo: rate need to be auto refreshed. so everthing keep like this right now.
    """ 
    # print(get_truncated_timestamp(end_date))
    
    if mode == 0:
        df_rate = pd.read_csv('./dataup/rates_tmp.csv')
    else:
        df_rate = pd.read_excel("E:\\SugarSync\\ANALYSIS FREIGHT ST\\Rates.xlsb", sheet_name='Routes', skiprows=10)
        df_rate = df_rate.dropna(axis=1, how = "all")
        df_rate = df_rate[['Capes5TC', 'Capes4TC', 'Pmax4TC', 'Pmax5TC', 'C8_03', 'C9_03','C10_03', 'C11_03', 'C8_14', 'C9_14', 'C10_14', 'C14', 'C16', 'C3',
            'C4', 'C5', 'C7',  'P1A_03', 'P2A_03', 'P3A_03',
            'P4A_03', 'P1A_82', 'P2A_82', 'P3A_82', 'P4_82', 'P5_82', 'P6_82',
            'Smax6TC', 'Smax10TC', 'S1A', 'S1B', 'S2', 'S3', 'S4', 'S4A', 'S4B',
            'S1B_58', 'S1C_58', 'S2_58', 'S3_58', 'S4A_58', 'S4B_58', 'S5_58',
            'S8_58', 'S9_58', 'S10_58', 'S11_58', 'Handy6TC', 'HS1', 'HS2', 'HS3',
            'HS4', 'HS5', 'HS6', 'C9-C4TC', 'C9/C4TC', 'C8-C4TC', 'C8/C4TC',
            'C16-C5TC', 'C9/C8', 'C10-C5TC', 'C8/C10', 'C8-C16', 'P2A-P4TC',
            'P2A/P4TC', 'P1A-P4TC', 'P1A/P4TC', 'P2A-P1A', 'P2A/P1A', 'P1A-P3A',
            'P1A/P3A', 'Cape 5TC-Pmax 5TC Spread', 'Cape 5TC/Pmax 5TC ratio',
            'C10/P3A', 'C8/P1A', 'C9/P2A', 'C3.1', 'C5.1', 
            'C5TC vs C10', 'C5TC vs C16', 'C5TC', 'datetime_fmted', 'Unnamed: 109',
            'Unnamed: 110', 'Unnamed: 111']]
        df_rate.columns = ['Capes5TC', 'Capes4TC',  'Pmax4TC', 'Pmax5TC','C8_03', 'C9_03','C10_03', 'C11_03', 'C8_14', 'C9_14', 'C10_14', 'C14', 'C16', 'C3',
            'C4', 'C5', 'C7', 'P1A_03', 'P2A_03', 'P3A_03',
            'P4A_03', 'P1A_82', 'P2A_82', 'P3A_82', 'P4_82', 'P5_82', 'P6_82',
            'Smax6TC', 'Smax10TC', 'S1A', 'S1B', 'S2', 'S3', 'S4', 'S4A', 'S4B',
            'S1B_58', 'S1C_58', 'S2_58', 'S3_58', 'S4A_58', 'S4B_58', 'S5_58',
            'S8_58', 'S9_58', 'S10_58', 'S11_58', 'Handy6TC', 'HS1', 'HS2', 'HS3',
            'HS4', 'HS5', 'HS6', 'C9-C4TC', 'C9/C4TC', 'C8-C4TC', 'C8/C4TC',
            'C16-C5TC', 'C9/C8', 'C10-C5TC', 'C8/C10', 'C8-C16', 'P2A-P4TC',
            'P2A/P4TC', 'P1A-P4TC', 'P1A/P4TC', 'P2A-P1A', 'P2A/P1A', 'P1A-P3A',
            'P1A/P3A', 'Cape 5TC-Pmax 5TC Spread', 'Cape 5TC/Pmax 5TC ratio',
            'C10/P3A', 'C8/P1A', 'C9/P2A', 'C3.1', 'C5.1', 
            'C5TC vs C10', 'C5TC vs C16', 'C5TC', 'datetime_fmted', "IO Price", "Ratio C3 vs IO" ,"Ratio C5 vs IO"]
        df_rate.to_csv('./dataup/rates_tmp.csv', index = None)
        df_rate = pd.read_csv('./dataup/rates_tmp.csv')
        #   
    df_rate = df_rate[df_rate['datetime_fmted'].str.contains('(201)|(202)').fillna(False)].drop_duplicates()
    df_rate['datetime_fmted'] = pd.to_datetime(df_rate['datetime_fmted'])
    df_rate = df_rate[df_rate['datetime_fmted'] < datetime.today()]
    time_df = pd.DataFrame(pd.date_range(df_rate['datetime_fmted'].min(), df_rate['datetime_fmted'].max(), ).to_frame()).reset_index(drop = True)
    time_df.columns = ['datetime_fmted']
    df_rate = df_rate.merge(time_df, on = "datetime_fmted", how = "right").ffill()
    df_rate = df_rate.rename({"Pmax4TC" : "P5TC", "datetime_fmted": "date"}, axis = 1)
    # st.write(df_rate)
    return df_rate 


def auto_clear_cache():
    from connect_db import connect_db 
    conn = connect_db()
    engine = conn.conn_alchemy
    sql = """
        SELECT cast(max(datetime_stamp) as varchar)
        FROM [BrokerData].[dbo].[ArrowBallasterList]
        union all 
        select v1 from tempTask.dbo.task_keys 
        where pk_column = 102
        """
    df = pd.DataFrame(engine.execute(sql).fetchall())
    df[''] = pd.to_datetime(df[''])
    if df.iloc[0,0] != df.iloc[1,0]:
        clear_cache()
        st.success('clear cache')
        # st.write('asdasd')
        v1 = str(df.iloc[0,0])
        sql_update = f"""
        update tempTask.dbo.task_keys  
        SET v1 = '{v1}'
            where pk_column = 102
        """
        engine.execute(sql_update)
        return 1 
    else:
        return 0


@st.cache_data(ttl=3600*24)
def load_online_data(end_date=datetime.today()):
    """
    * major change on df. 
    * also the st multiselector. 
    """
    get_truncated_timestamp(end_date)
    from connect_db import connect_db 
    conn = connect_db()
    engine = conn.conn_alchemy
    sql = """
        SELECT  *
        FROM [BrokerData].[dbo].[ArrowBallasterList]
        """
    df = pd.DataFrame(engine.execute(sql).fetchall())
    df = df.groupby(['Region', 'ReportDate'], as_index=False)['Name'].count()
    df.columns = ['Region', 'date','count']
    
    df_piv = df.pivot_table(columns=['Region'], index=['date',], values='count').fillna(0).reset_index()
    df_piv['date'] = pd.to_datetime(df_piv['date'])
    df_piv = pd.DataFrame({'date':pd.date_range(df['date'].min(), df['date'].max())}).merge(df_piv, how = 'left', on = 'date')
    df_piv = df_piv.ffill()
    df_piv['year'] = df_piv['date'].astype(str).str.extract('(^\d+)')
    # st.write(df_piv.head(5))
    df = pd.melt(df_piv, id_vars=['date',], value_vars=['ARAG', 'BALTIC', 'BLACK', 'EAFR', 'ECCA', 'ECCAN',
       'ECI', 'ECSA', 'EMED', 'INDIAN OCEAN', 'N. CONT', 'NCSA', 'NOPAC', 'PG',
       'RED SEA', 'SAFR', 'SEASIA', 'USEC', 'USG', 'WAFR', 'WCCA', 'WCI',
       'WCSA', 'WMED'] )
    df.columns = ['date',  'Region', 'count']
    dim_region_map_mf = pd.DataFrame(engine.execute("select * from [BrokerData].[dbo].[dim_region_map_mf]" ).fetchall())
    conn.connect_close()
    return df , dim_region_map_mf
    

def key_gen():
    global keygen
    if keygen == 0:
        keygen = 200
    else:
        keygen += 1
    return keygen

def selector_ontop():
    global list_of_select_regions_p, list_of_select_regions_ps, list_of_select_regions_s 
    df = st.session_state['online_df1']
    df['mark'] = True
    
    def show_par_region(df, filter):
        with st.sidebar:
            m = st.checkbox(filter, max(df.query("parent_regions == '{filter}'".format(filter = filter))['mark']))
        return  m
    def show_sub_region(df, filter):
        sub_ls = []
        st.markdown("`{t}`".format(t = filter[0]))
        ls = df[df['parent_regions'].isin(filter)]
        for _, row in ls.iterrows():
            keygen = key_gen() 

            m = st.checkbox(
                row['region'], 
                value = row['mark'], 
                key = keygen, 
                disabled=not row['mark'], 
                ) 
            sub_ls += [m]
        
        return sub_ls
    # ARAG,EMED,SAFR,WCI,Other,ECSA,NOPAC,SEASIA = st.columns(8)
    # ARAG1,EMED1,SAFR1,WCI1,Other1,ECSA1,NOPAC1,SEASIA1 = st.columns(8)
    # ARAG1,EMED1,  WCI1,SEASIA1 = st.columns([1,1,3,2])

    # with ARAG1:
    #* parent selector
    # st.write('')
    ARAG = show_par_region(df, "ARAG+WMED+BALTIC")
    EMED = show_par_region(df, "EMED+BLACKSEA")
    SAFR = show_par_region(df, "SAFR+EAFR")
    WCI  = show_par_region(df, "WCI+ECI+PG+RED SEA")
    # with EMED1:
    # st.write('')
    Other  = show_par_region(df, "Other N ATL")
    ECSA   = show_par_region(df, "ECSA+WCSA")
    NOPAC  = show_par_region(df, "NOPAC+WCCA")
    SEASIA = show_par_region(df, "SEASIA")
    # with WCI1:
    #     # show_sub_region(df, "*")
    #     pass
    # with SEASIA1:
    #     #* logo
    #     with st.container():

    #         # st.image("https://raw.githubusercontent.com/fyenne/picgallery/master/freight_research_1.svg")
    #         i = os.listdir("./logos/")[np.random.randint(0,4)]
    #         st.image("./logos/" + i)
    
    defaul_col = ["ARAG+WMED+BALTIC", 
                    "EMED+BLACKSEA", 
                    "SAFR+EAFR", 
                    "WCI+ECI+PG+RED SEA", 
                    "Other N ATL", 
                    "ECSA+WCSA", 
                    "NOPAC+WCCA", 
                    "SEASIA", ]
    # st.write('---')
    #* get parent region - sub region 
    marked_col = [ARAG]+[EMED]+[SAFR]+[WCI]+[Other]+[ECSA]+[NOPAC]+[SEASIA]
    select_df = pd.DataFrame({"defaul_col":defaul_col, "marked_col":marked_col})
    
    df['mark'] = df['parent_regions'].isin(list(select_df[select_df['marked_col']]['defaul_col']))
    # with st.sidebar:

    with st.expander("subregions", False):
        #* sub regions selector
        ARAG1,EMED1,SAFR1,WCI1,Other1,ECSA1,NOPAC1,SEASIA1 = st.columns(8)
        sub_ls = []
        with ARAG1:
            sub_ls += show_sub_region(df, ["ARAG+WMED+BALTIC"])
        with EMED1:
            sub_ls += show_sub_region(df, ["EMED+BLACKSEA"])       
        with SAFR1:
            sub_ls += show_sub_region(df, ["SAFR+EAFR"])   
        with WCI1:
            sub_ls += show_sub_region(df, ["WCI+ECI+PG+RED SEA"])       
        with Other1:
            sub_ls += show_sub_region(df, ["Other N ATL"])
        with ECSA1:
            sub_ls += show_sub_region(df, ["ECSA+WCSA"])       
        with NOPAC1:
            sub_ls += show_sub_region(df, ["NOPAC+WCCA"])       
        with SEASIA1:
            sub_ls += show_sub_region(df, ["SEASIA"])
        # st.write('---')
    df['mark'] = sub_ls
    
    list_of_select_regions_s = list(df[df['mark']]['region'])
    list_of_select_regions_ps = select_df[select_df['marked_col']]['defaul_col'] # for plot at the end. some content to load.
    return list_of_select_regions_s
    

def splited_table_plt(run_manual_table_plt_ ,hide = True):
    """
    * very complicated session and cache management. so the multiselect wont perform on click change. good job samo!
    first two *if* make online data in cache.
    try:except:
    then load selectors from session_cache data
    source ==> st.session_state ==> 
    """
    if 'online_df0' not in st.session_state:
        st.session_state['online_df0'] = load_online_data()[0] # just the online data for dtl
    if 'online_df1' not in st.session_state:
        st.session_state['online_df1'] = load_online_data()[1] # the online data of dim_region_map_mf
    try:
        df = st.session_state.online_df_changed_remained.copy(True)
    except:
        df = st.session_state.online_df0.copy(True)

    if  hide == True:            
        list_of_select_regions_s = selector_ontop() 
        df = st.session_state.online_df0.copy(True)
        # st.write(df)
        df = df[df['Region'].isin(list_of_select_regions_s)] # sub region to sub region filter.
        st.session_state.online_df_changed_remained = df 

    else:
        pass
    df = df.groupby('date', as_index=False)['count'].sum()     
    df = df.merge(run_manual_table_plt_[['date','P5TC']], on = 'date', how = 'left')
    df['year'] = df['date'].astype(str).str.extract('(^\d+)')
 
    return df

def figure_total(df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = df["date"],
            y = df["count"],
            # fill='tozeroy',
            name="count",
            line = dict(
                    color=color_func()[-1],
                    smoothing = 1.21,
                    width =  2.5 ),
            # fillcolor='#ff03'
        )
        ) 
    endpoint_annotation(df, "count", fig)
    shorter_init_plotxaxis(fig,df)
    fig.update_layout(dict1={
        "title": "Pmax open in selected regions (linear)", 
        "transition_duration":333
        }
        )

    return fig

def figure_total_2(df):
    fig = go.Figure()
    for i in range(4): 
        yr = list(df['year'].unique())[i]
        df['date'] = pd.to_datetime(df['date'].astype(str).str.replace('\d{4}', '2020'))
        fig = plot_seasonal(df.query("year == '{i}'".format(i = yr)), fig, i, yr)
    fig.update_layout(dict1={"title": "Pmaxes open in selected regions (seasonal total)"})
    fig.update_yaxes({"autorange" : True})
    shorter_init_plotxaxis2(fig,df)
    endpoint_annotation(df, 'count', fig)
    return fig 
# !---------------------------------------------------------------------------- #
#                                ! main content                                 #
# !---------------------------------------------------------------------------- #

# st.sidebar.button("Refresh data", on_click=clear_cache)
# st.sidebar.markdown("select parent region(s)")
def main_pmax_():
    global keygen
    keygen = 0
    mode = auto_clear_cache()

    run_manual_table_plt_ = run_manual_table_plt(mode)
    df = splited_table_plt(run_manual_table_plt_) 
    col1, col2 = st.columns(2)
    with col1:
        
        st.plotly_chart(
            plt_func_update(figure_total(df))
            , use_container_width=True)
        
    with col2:
        
        fig = plt_func_update(figure_total_2(df.copy(True)) )
        st.plotly_chart(
            fig
            , use_container_width=True)


    # ---------------------------------------------------------------------------- #
    #                            p5tc rate vs count plot                           #
    # ---------------------------------------------------------------------------- #
    col1 ,col2,col23 = st.columns([1,1,3])
    with col1:
        st.button("Refresh data", on_click=clear_cache)
    with col2:
        st.write("`"+ str(df.tail(1)['date'].iloc[0]) + '`')


    sys.path.append("D:\\samo\\bunge_freight_dashboard_ext\\pages\\")
    run_original_data_downloader()