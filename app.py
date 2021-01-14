import os

import dash
import dash_core_components as dcc
import dash_html_componenats as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
#df = pd.DataFrame({
#    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#    "Amount": [4, 1, 2, 2, 4, 5],
#    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
#})



# THis is preprocessing , it can be done before and the file would load wuickly

df_nat = pd.read_csv('data/nat2019.csv', ';')
df_nat['prenoms_s']=[str(df_nat.preusuel.iloc[i])+' - ♂' if df_nat.sexe.iloc[i]==1 else str(df_nat.preusuel.iloc[i])+' - ♀' for i in df_nat.index]  
prenoms_sel = [dict(label=prenom, value=prenom) for prenom in df_nat.prenoms_s.unique()]
#df_dpt = pd.read_csv('dpt2019.csv', ';')

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    #html.Div(["Prénoms: ",
    #          dcc.Input(id='my-input', value='CAMILLE', type='text')]),
    dcc.Dropdown(
        id='dropdown-prenoms',
        options=prenoms_sel,
        value=['ALIX - ♂'],
        multi=True
    ),
    dcc.Graph(
        id='example-graph',
    )
])


@app.callback(
    Output(component_id='example-graph', component_property='figure'),
    Input(component_id='dropdown-prenoms', component_property='value')
)
def update_output_div(input_value):
    fig = go.Figure()
    for prenom_s in input_value:
        prenom = prenom_s[:-4]
        if prenom_s[-1]=='♂':
            sexe = 1
        else :
            sexe = 2
        
        wanted_mask = (df_nat.preusuel==prenom) & (df_nat.sexe==sexe)
        fig.add_trace(
            go.Scatter(
                x=df_nat[wanted_mask].annais,
                y = df_nat[wanted_mask].nombre,
                name=prenom_s,
                mode='markers+lines',
                hovertemplate='Année : %{x}<br>Nombre : %{y}'))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)