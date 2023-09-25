import os
import streamlit.components.v1 as components
import pandas as pd
import numpy
import json
import sys
import re
import datetime
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = False
st.set_page_config(layout="wide")
# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    cwd = os.getcwd()
    if re.findall('component-template$', cwd) == []:
        path_prefix = './backend'
    else:
        path_prefix = ''
    sys.path.append(path_prefix)
    from backend.backend_util import get_df,get_df_atl_summarized, get_df_pac_summarized
    import backend.cape_summ_table as cape_summ_table #import get_russian_vessels
    import backend.plot_util as plot_util
    import backend.backend_util as backend_util
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "my_component",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url = "http://10.92.1.57:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend-react/build")
    _component_func = components.declare_component("my_component", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.


def load_data_from_origin_():

    
    
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
                ]
            ]
            summ_table_present.rename({'new_cnt': 'new', 'roll_cnt': 'roll', 'gone_cnt':'gone'}, inplace = True, axis = 1)

            st.table(
                plot_util.table_decorater_(summ_table_present,1)
            )
            st.write("last refresh: ", df['last_modified_time'].max())
        file_time_stamp = chart_data['file_time_stamp'].max()
        chart_data = chart_data[chart_data["file_time_stamp"]==file_time_stamp]    

        with col3:
            i = ["non_scrubbed", "scrubber"]
            plt = plot_util.plot_summ_count(i,chart_data, color_pair_controller=-1)
            st.plotly_chart(plt, use_container_width=True) 

        col1, col2, col3, col4 = st.columns([3,1,1,1])
        col_list = [col2,col3,col4]
        # col5,col6 = st.columns(2)
        with col1:
            plt = plot_util.plot_general_count(cd1,cd2)
            st.plotly_chart(plt, use_container_width=True)
            st.plotly_chart(plot_util.operator_plot(df))
            # df_operator_summarized = backend_util.get_df_operator_summarized(df)
            # st.plotly_chart(px.bar(df_operator_summarized, x = 'operator', y = 'occurence'))
        # with col6:
        #     st.write(chart_data)
        m = 0
        for i in [
            ["not_drafty","drafty"],
            ["under_15yo","over_15yo"], 
            ['isopen_med','isopen_nwe']
            ]:
                plt = plot_util.plot_summ_count(i,chart_data,color_pair_controller = m)
                with col_list[m]:
                    st.plotly_chart(plt, use_container_width=True)
                    m+=1
        
        return df,cd1,cd2, tab2


def interactive_table_compo(df, cd1):
    st.write('Currente Atlantic Open Ships')
    ca = cape_summ_table.present_df_(df, cd1)
    df_open_time_min, df_open_time_max  = pd.to_datetime(
        df['early_open'].min()
        ), pd.to_datetime(df['late_open'].max()) + datetime.timedelta(days=60) 
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
    check_interval = pd.Interval(
        pd.to_datetime(start_date)- datetime.timedelta(days=1),
        pd.to_datetime(end_date) + datetime.timedelta(days=1)
        )
    ca['overlap'] = ca.apply(lambda row: pd.Interval(
            row['early_open'], 
            row['late_open']
        ).overlaps(check_interval), axis=1)
    ca = ca[ca['overlap']].drop(['overlap'], axis = 1) 
    len_ = 300 if len(ca)*45 < 300 else len(ca)*45
    ca = ca.drop(
        ['early_open', 'late_open', 'early_second_eta', 'late_second_eta'], axis = 1
        ) #.drop(['early_open', 'late_open'], axis = 1), 
    return pd.DataFrame(ca)

def my_component(greetings, name, key=None):
    
    ls = json.dumps(os.listdir('./frontend/'))

    df, ca1, ca2, tab2 = load_data_from_origin_()
    ca = interactive_table_compo(df,ca1)
    ca.columns = pd.Series(ca.columns).str.replace(' ', '')
    ca.Speed = ca.Speed.round(2)
    df1 = ca.to_json(orient='records') 
    # df2 = summ_table_present.to_json(orient='records') 
    component_value = _component_func(
        greetings = greetings, 
        name=name, 
        ls  = ls,
        df1 = df1,
        # df2 = df2, 
        key = key, 
        default=0)

    
    return component_value


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
if not _RELEASE:

    # st.subheader("Component with constant args")

    # Create an instance of our component with a constant `name` arg, and
    # print its output value.
    num_clicks = my_component("ahoy","World")
    # st.markdown("You've clicked %s times!" % int(num_clicks))


    # Create a second instance of our component whose `name` arg will vary
    # based on a text_input widget.
    #
    # We use the special "key" argument to assign a fixed identity to this
    # component instance. By default, when a component's arguments change,
    # it is considered a new instance and will be re-mounted on the frontend
    # and lose its current state. In this case, we want to vary the component's
    # "name" argument without having it get recreated.
    # name_input = st.text_input("Enter a name", value="Streamlit")
    # num_clicks = my_component("greetings", name_input, key="foo")
    # st.markdown("You've clicked %s times!" % int(num_clicks))
