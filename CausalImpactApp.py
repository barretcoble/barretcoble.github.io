# %%
# Could easily combine all the callbacks if you just adjust the outputs, call the figs 1,2, and 3, and adjust x and y to be unique for each


import base64
import datetime
import io
import plotly.graph_objs as go
from datetime import date, timedelta
# import dash_uploader as du


import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table

from causalimpact import CausalImpact
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {"graphBackground": "#F5F5F5", "background": "#ffffff", "text": "#000000"}

instructions = ["Upload a spreadsheet with the following columns: Dates, Experiment Data, Control Data","Select the name of the column with your dates","Select the range of the historical data from before the experiment started that will be used to build the model","Select the range your experiment started and finished","Hit 'Run Analysis'"]


app.layout = html.Div(
    [   html.H1("Causal Impact Analysis", style={"font-family":"sans-serif"}),
        html.Br(),
    html.Div([
    html.Div([html.P(id='summary',style={"white-space": "pre-wrap",'word-wrap':'break-word'}),html.P(children="Instructions:",id='instructions',style={'font-weight':'bold',"white-space": "pre-wrap",'word-wrap':'break-word'}),html.Ol(children=[html.Li(i) for i in instructions]),html.Br(), html.P('A summary of the findings will be output above.'), html.Br(),html.P("Note: This analysis will only be valuable if the control and experiment groups are reasonably correlated. The model is only as good as the data it is built on.",style={'font-weight':'bold'})],style={'text-align':'left','width':'40%','margin-left':'5%','border-width':'3px','border-style':'solid','padding':'25px'}),
    html.Div([
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),
        html.Br(),

        dcc.Dropdown(
            id="date column name",
            options=[],
            placeholder="Select your date column",
            style={'width':'100%'}
        ),
        html.Br(),
        html.Br(),
        
        dcc.Dropdown(
            id="experiment column name",
            options=[],
            placeholder="Select your experiment column",
            style={'width':'100%'}
        ),

        html.Br(),
        html.Br(),

        dcc.Dropdown(
            id="control column name",
            options=[],
            placeholder="Select your control column",
            style={'width':'100%'}
        ),

        # du.Upload(
        #     text="This is the test one",
        #     text_completed='File Uploaded'),

        html.Div([

        html.Br(),
            
            html.Label('Historical Date Range',style={'text-align':'center'}),
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(2022, 1, 1),
                max_date_allowed=date(2023, 3, 14),
                style={'text-align':'center'}),

        html.Br(),
        html.Br(),

            html.Label('Experiment Date Range',style={'text-align':'center'}),
            dcc.DatePickerRange(
                id='experiment-date-picker-range',
                min_date_allowed=date(2022, 1, 1),
                max_date_allowed=date(2023, 3, 14))],
                style={'text-align':'center'}),

        html.Br(),

            html.Button('Run Analysis', id='submit-val',n_clicks=0,style={'textAlign':'center'})],style={'margin-left':'auto','margin-right':'15%','border-width':'3px','border-style':'solid','padding':'25px'})],style={'display':'flex'}),

        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),

        html.P('This will show your daily performance vs. projected'),
        dcc.Graph(id="Mygraph",style={'width':'95%',"margin-left":"auto","margin-right":"auto","display":"block"}),
        html.Br(),        
        html.P('This will show how each day compared to the projected performance'),
        dcc.Graph(id="daygraph",style={'width':'95%',"margin-left":"auto","margin-right":"auto","display":"block"}),
        html.Br(),
        html.P('This will show how the experiment performed cumulatively'),
        dcc.Graph(id="cumulativegraph",style={'width':'95%',"margin-left":"auto","margin-right":"auto","display":"block"}),
        html.Div(id="output-data-upload"),
    ],style={'textAlign':'center','background-color': '#4dbac1', 'paper_bgcolor':'#4dbac1'}
)

# @app.callback(
#     Output("output-data-upload", "children"),
#     [Input("upload-data", "contents"), Input("upload-data", "filename")])
def parse_data(contents, filename):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif "txt" or "tsv" in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return df


@app.callback(
    Output('experiment-date-picker-range', 'start_date'),
    Output('experiment-date-picker-range','min_date_allowed'),
    Input('my-date-picker-range', 'end_date'))
def update_daterange(end_date):
    end_date = pd.to_datetime(end_date)
    start_date = end_date + timedelta(days=1)
    min_date_allowed = end_date + timedelta(days=2)
    return start_date, min_date_allowed


@app.callback(
    Output('date column name','options'),    
    Output('experiment column name','options'),
    Output('control column name','options'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename'),)
def update_dropdowns(contents,filename):
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
    return [{'label':k,'value':k} for k in df.columns], [{'label':k,'value':k} for k in df.columns], [{'label':k,'value':k} for k in df.columns]



@app.callback(
    Output('Mygraph', 'figure'),
    Output('summary','children'),
    Output('daygraph', 'figure'), 
    Output('cumulativegraph', 'figure'), 
    # Output(component_id='my-spinner', component_property='children'), 
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('my-date-picker-range', 'start_date'),
    State('my-date-picker-range', 'end_date'),
    State('experiment-date-picker-range', 'start_date'),
    State('experiment-date-picker-range', 'end_date'),
    State('experiment column name','value'),
    State('control column name','value'),
    State('date column name','value'),
    Input('submit-val','n_clicks'),
    # Input(component_id='upload-data', component_property='loading_state'),
    prevent_initial_call=True)
def update_graph(contents, filename, start_date, end_date, experiment_start_date, experiment_end_date, experimentColumn, controlColumn,dateColumn,n):
    x = []
    y = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df[dateColumn] = pd.date_range(start = start_date, periods = len(df),freq='D')
        causalImpactDF = df[[experimentColumn,controlColumn]]
        
        causalImpactDF = causalImpactDF.set_index(pd.date_range(start=start_date, periods=len(causalImpactDF)))
        pre_period = [start_date, end_date]
        post_period = [experiment_start_date, experiment_end_date]
        ci = CausalImpact(causalImpactDF, pre_period, post_period, alpha=.1)
        causalImpactLength = df[df[dateColumn] == experiment_end_date].index[0]
        causalImpactDF = causalImpactDF.iloc[1:causalImpactLength+1]
        x=df[dateColumn].iloc[0:causalImpactLength+1]
        y=df[experimentColumn].iloc[0:causalImpactLength+1]

    fig = go.Figure([
        go.Scatter(
            name='Causal Impact',
            x=x,
            y=y,
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
        ),
        go.Scatter(
            name='Upper Bound',
            x=causalImpactDF.index,
            y=pd.DataFrame(ci.inferences['preds_upper'])['preds_upper'].iloc[1:],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=causalImpactDF.index,
            y=pd.DataFrame(ci.inferences['preds_lower'])['preds_lower'].iloc[1:],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])

    fig2 = go.Figure([
        go.Scatter(
            name='Point Effects',
            x=x,
            y=pd.DataFrame(ci.inferences['point_effects'])['point_effects'].iloc[0:],
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
        ),
        go.Scatter(
            name='Upper Bound',
            x=causalImpactDF.index,
            y=pd.DataFrame(ci.inferences['point_effects_upper'])['point_effects_upper'].iloc[1:],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=causalImpactDF.index,
            y=pd.DataFrame(ci.inferences['point_effects_lower'])['point_effects_lower'].iloc[1:],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    fig3 = go.Figure([
        go.Scatter(
            name='Causal Impact',
            x=x,
            y=pd.DataFrame(ci.inferences['post_cum_effects'])['post_cum_effects'].iloc[0:],
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
        ),
        go.Scatter(
            name='Upper Bound',
            x=causalImpactDF.index,
            y=pd.DataFrame(ci.inferences['post_cum_effects_upper'])['post_cum_effects_upper'].iloc[1:],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=causalImpactDF.index,
            y=pd.DataFrame(ci.inferences['post_cum_effects_lower'])['post_cum_effects_lower'].iloc[1:],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])

    return fig, ci.summary('report')[33:].replace('\n\n\n','LINEBREAK').replace('\n',' ').replace('LINEBREAK','\n\n'), fig2, fig3


# @app.callback(
#     Output('daygraph', 'figure'), 
#     State('upload-data', 'contents'),
#     State('upload-data', 'filename'),
#     State('my-date-picker-range', 'start_date'),
#     State('my-date-picker-range', 'end_date'),
#     State('experiment-date-picker-range', 'start_date'),
#     State('experiment-date-picker-range', 'end_date'),
#     Input('submit-val','n_clicks'))
# def update_graph(contents, filename, start_date, end_date, experiment_start_date, experiment_end_date,n):
#         x = []
#         y = []
#         if contents:
#             contents = contents[0]
#             filename = filename[0]
#             df = parse_data(contents, filename)
#             df['Day'] = pd.date_range(start = start_date, periods = len(df),freq='D')
#             causalImpactDF = df[['Experiment','Control']]
#             causalImpactDF = causalImpactDF.set_index(pd.date_range(start=start_date, periods=len(causalImpactDF)))
#             pre_period = [start_date, end_date]
#             post_period = [experiment_start_date, experiment_end_date]
#             ci = CausalImpact(causalImpactDF, pre_period, post_period, alpha=.1)
#             causalImpactLength = df[df['Day'] == experiment_end_date].index[0]
#             causalImpactDF = causalImpactDF.iloc[1:causalImpactLength+1]
#             x=df['Day'].iloc[0:causalImpactLength+1]
#             y=df['Experiment'].iloc[0:causalImpactLength+1]

#         fig = go.Figure([
#             go.Scatter(
#                 name='Point Effects',
#                 x=x,
#                 y=pd.DataFrame(ci.inferences['point_effects'])['point_effects'].iloc[0:],
#                 mode='lines',
#                 line=dict(color='rgb(31, 119, 180)'),
#             ),
#             go.Scatter(
#                 name='Upper Bound',
#                 x=causalImpactDF.index,
#                 y=pd.DataFrame(ci.inferences['point_effects_upper'])['point_effects_upper'].iloc[1:],
#                 mode='lines',
#                 marker=dict(color="#444"),
#                 line=dict(width=0),
#                 showlegend=False
#             ),
#             go.Scatter(
#                 name='Lower Bound',
#                 x=causalImpactDF.index,
#                 y=pd.DataFrame(ci.inferences['point_effects_lower'])['point_effects_lower'].iloc[1:],
#                 marker=dict(color="#444"),
#                 line=dict(width=0),
#                 mode='lines',
#                 fillcolor='rgba(68, 68, 68, 0.3)',
#                 fill='tonexty',
#                 showlegend=False
#             )
#         ])

#         return fig



# @app.callback(
#     Output('cumulativegraph', 'figure'), 
#     State('upload-data', 'contents'),
#     State('upload-data', 'filename'),
#     State('my-date-picker-range', 'start_date'),
#     State('my-date-picker-range', 'end_date'),
#     State('experiment-date-picker-range', 'start_date'),
#     State('experiment-date-picker-range', 'end_date'),
#     Input('submit-val','n_clicks'))
# def update_graph(contents, filename, start_date, end_date, experiment_start_date, experiment_end_date,n):
#         x = []
#         y = []
#         if contents:
#             contents = contents[0]
#             filename = filename[0]
#             df = parse_data(contents, filename)
#             df['Day'] = pd.date_range(start = start_date, periods = len(df),freq='D')
#             causalImpactDF = df[['Experiment','Control']]
#             causalImpactDF = causalImpactDF.set_index(pd.date_range(start=start_date, periods=len(causalImpactDF)))
#             pre_period = [start_date, end_date]
#             post_period = [experiment_start_date, experiment_end_date]
#             ci = CausalImpact(causalImpactDF, pre_period, post_period, alpha=.1)
#             causalImpactLength = df[df['Day'] == experiment_end_date].index[0]
#             causalImpactDF = causalImpactDF.iloc[1:causalImpactLength+1]
#             x=df['Day'].iloc[0:causalImpactLength+1]
#             y=df['Experiment'].iloc[0:causalImpactLength+1]

#         fig = go.Figure([
#             go.Scatter(
#                 name='Causal Impact',
#                 x=x,
#                 y=pd.DataFrame(ci.inferences['post_cum_effects'])['post_cum_effects'].iloc[0:],
#                 mode='lines',
#                 line=dict(color='rgb(31, 119, 180)'),
#             ),
#             go.Scatter(
#                 name='Upper Bound',
#                 x=causalImpactDF.index,
#                 y=pd.DataFrame(ci.inferences['post_cum_effects_upper'])['post_cum_effects_upper'].iloc[1:],
#                 mode='lines',
#                 marker=dict(color="#444"),
#                 line=dict(width=0),
#                 showlegend=False
#             ),
#             go.Scatter(
#                 name='Lower Bound',
#                 x=causalImpactDF.index,
#                 y=pd.DataFrame(ci.inferences['post_cum_effects_lower'])['post_cum_effects_lower'].iloc[1:],
#                 marker=dict(color="#444"),
#                 line=dict(width=0),
#                 mode='lines',
#                 fillcolor='rgba(68, 68, 68, 0.3)',
#                 fill='tonexty',
#                 showlegend=False
#             )
#         ])

#         return fig



# def update_table(contents, filename):
#     table = html.Div()

#     if contents:
#         contents = contents[0]
#         filename = filename[0]
#         df = parse_data(contents, filename)
#         df['Day'] = pd.DatetimeIndex(df.Day).strftime("%Y-%m-%d")

#         table = html.Div(
#             [
#                 html.H5(filename),
#                 dash_table.DataTable(
#                     data=df.to_dict("rows"),
#                     columns=[{"name": i, "id": i} for i in df.columns],
#                 ),
#                 html.Hr(),
#                 html.Div("Raw Content"),
#                 html.Pre(
#                     contents[0:200] + "...",
#                     style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
#                 ),
#             ]
#         )

#     return table



if __name__ == "__main__":
    app.run_server(debug=False)


