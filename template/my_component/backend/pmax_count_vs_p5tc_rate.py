
import streamlit as st
from plot_modify import *
from plotly.subplots import make_subplots
import numpy as np
from pages_component.arrow_pmax_list import run_manual_table_plt, splited_table_plt, auto_clear_cache # list_of_select_regions_ps

def clear_cache():
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.clear()

def plot_rate_count(df, x):
    df['tt_rolling'] = df['count'].rolling(5).mean() # smooth the line.
    df['lag_10_tt_rolling'] = df['tt_rolling'].shift(x)

    # ---------------------------------------------------------------------------- #
    #                    df_extension for little tail at the end                   #
    # ---------------------------------------------------------------------------- #
    df_extension = df.tail(x+1)
    df_extension['lag_10_tt_rolling'] = df.iloc[-x-1:,]['tt_rolling']
    df_extension['date'] = pd.to_datetime(df_extension['date'])+timedelta(x)
    df_extension['tt_rolling'] = np.nan
    # df_extension['tt_rolling'] = np.nan
    # ---------------------------------------------------------------------------- #
    #                                  fig content                                 #
    # ---------------------------------------------------------------------------- #
    colors = color_func() + ["#cc7111", "#cc0001"]
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    #* p5tc rate line
    fig.add_trace(go.Scatter(
        x = df["date"],
        y = df['P5TC'],
        name = "rate",
        line_shape = 'spline',
        fill='tozeroy',
        line = dict(
            color=color_func()[5],
            smoothing = 1.21,
            width =  2.5 ),
        hovertemplate='P5TC rate: <b><i>%{y}</i></b>'
    ), secondary_y=False)
    
    #* hidden original line of count
    # fig.add_trace(go.Scatter(
    #     x = df["date"],
    #     y = df['tt_rolling'],
    #     name = 'count',
    #     text = df['date'],
    #     # fill='tozeroy',
    #     line = dict(
    #         color=colors[-2],
    #         smoothing = 1.21,
    #         width =  2.5 ),
    #     hovertemplate='count: <b><i>%{y}</i></b> <extra></extra>'

    # ), secondary_y=True,)
    #* lag line of count
    fig.add_trace(go.Scatter(
        x = df["date"],
        y = df['lag_10_tt_rolling'],
        name = 'count',
        text = df['date'],
        line = dict(
            color=colors[-1],
            smoothing = 1.21,
            width =  2.5 ),
        hovertemplate='count: <b><i>%{y}</i></b> <extra></extra>'

    ), secondary_y=True,)
    # df_extension
    #* redundant, but lazy to recode.
    fig.add_trace(go.Scatter(
        x = df_extension["date"],
        y = df_extension['lag_10_tt_rolling'],
        name = 'count',
        mode = 'lines',
        text = df_extension['date'],
        line = dict(
            color=colors[-1],
            smoothing = 1.21,
            width =  2.5 ),
        hovertemplate='count: <b><i>%{y}</i></b> <extra></extra>'
    ), secondary_y=True,)
    #* MARKS of current
    fig.add_trace(go.Scatter(
        x=[df['date'].iloc[0], df['date'].iloc[-1]],
        y=[df['tt_rolling'].iloc[0], df['tt_rolling'].iloc[-1]],
        mode='markers', 
        name = 'current counts'
    ),secondary_y=True,)

    
    fig.add_trace(go.Scatter(
        x=[df['date'].iloc[-1]], #  df['date'].iloc[0],
        y=[df['P5TC'].iloc[-1]], # df['P5TC'].iloc[0],
        mode='markers', 
        name = 'current P5TC'
        
    ),secondary_y=False,)
    
    #* annotations of current
    annotations = []  
    annotations.append(dict(xref='paper', x=0.892, y=df['P5TC'].iloc[-1],
                                xanchor='left', yanchor='top',
                                text='{}'.format("P5TC " + str("{:.0f}").format(df['P5TC'].iloc[-1])), #str("{:.0f}").format(y_value)
                                font=dict(family='Arial Black',
                                            size=14,
                                            color = colors[7]),
                                
                                showarrow=False))
    annotations.append(dict(xref='paper', yref = 'y2', x=0.892, y=df['tt_rolling'].iloc[-1] - 5.2,
                                xanchor='left', yanchor='top',
                                text='{}'.format("count " +  str("{:.0f}").format(df['tt_rolling'].iloc[-1])),
                                font=dict(family='Arial Black',
                                            size=14,
                                            color = colors[7]),
                                
                                showarrow=False), )
    fig.update_yaxes(
        {
            "showspikes":True
            , "spikecolor": '#33ffcc'
            , "spikedash" : "2px"
            # , "autorange": "reversed"
            , "fixedrange": False

        }
            )
    fig.update_layout(
        shapes = [
            {
            'type': 'line',
            'x0': df['date'].iloc[-1], 
            'x1': df['date'].iloc[-1], 
            'y0': 1,
            'y1': 0,
            'yref': 'paper',
            'line': {
                'color': 'red',
                'width': 2,
                'dash': 'dot'
            }
        }
            ],
        title = "5 days average Pmaxes open vs P5TC lag for {x} days <br>".format(x = x, ), # <sup>{Total}</sup> ; Total= list(list_of_select_regions_ps)
        # captions = "{Total}".format(Total = list(list_of_select_regions_ps)),
        annotations=annotations
        )
    plt_func_update(fig, 1)
    shorter_init_plotxaxis(fig,df, 360, 20)
    return fig

# ---------------------------------------------------------------------------- #
#                             ADD SLIDER TO 3RD PIC                            #
# ---------------------------------------------------------------------------- #

def plot_prices(run_manual_table_plt_):
    df = run_manual_table_plt_.tail(1500)

    fig = go.Figure()
    for i in [
        "C5TC"
        ,"C5TC vs C10"
        ,"C5TC vs C16"
        ,"Cape 5TC-Pmax 5TC Spread"
        ,"Capes5TC"
        ,"Capes4TC"
        ,"P5TC"
        ,"Pmax5TC"]:
        if i == "Cape 5TC-Pmax 5TC Spread":
            fill_ = 'tozerox'
        else:
            fill_ = None
        fig.add_trace(go.Scatter(
            x = df['date'],
            y = df[i],
            name = i,
            fill=fill_,
        ))
    st.plotly_chart(fig, use_container_width=True)
    return 1

# df = st.session_state.online_df0
def main_rates_():
    mode = auto_clear_cache()
    run_manual_table_plt_ = run_manual_table_plt(mode)
    df = splited_table_plt(run_manual_table_plt_, hide = False)
    t_roll = 0 #st.slider("move count line.", min_value=0,max_value=91,value=0) 
    # st.write(df.head(5))
    st.plotly_chart(
        plot_rate_count(df , t_roll)
        , use_container_width=True)

    # st.write(list(run_manual_table_plt_.columns))


    st.button("Refresh data", on_click=clear_cache)


    plot_prices(run_manual_table_plt_)
    st.write(run_manual_table_plt_.tail(50))
