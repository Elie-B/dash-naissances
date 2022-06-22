import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pickle as pkl


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                update_title='Chargement...')
server = app.server

dict_prénoms = pkl.load(open('data/dict_prenoms.pkl', 'rb'))
df_nat = pd.read_feather('data/df_nat.feather')
# Suppression des prénoms trop rares :
masque_prénoms_rares = (
    df_nat.prénoms_s == '_PRENOMS_RARES - ♂') | (df_nat.prénoms_s == '_PRENOMS_RARES - ♀')
# drop des prénoms rares
df_nat = df_nat.drop(df_nat[masque_prénoms_rares].index)

app.layout = html.Div(children=[
    html.H1(children='Naissances France'),

    html.Div(id='sous-titre', children='''
        Fréquence des prénoms de naissance en France de 1900 à nos jours
    '''),
    dcc.Dropdown(
        id='dropdown-prénoms',
        options=dict_prénoms,
        value=[dict_prénoms[888]['value']],
        placeholder="Chercher un prénom",
        multi=True
    ),
    dcc.Graph(
        id='graph-fréquences',
        style={'height': '80vh'},
        config={'displayModeBar': False}
    ),
    html.Div(id='bandeau', children=""),
])


@app.callback(
    Output(component_id='bandeau', component_property='children'),
    [Input(component_id='dropdown-prénoms', component_property='value')]
)
def maj_bandeau(prénoms_selectionnés):
    if len(prénoms_selectionnés) == 0:
        return ""
    else:
        masque = df_nat.prénoms_s == prénoms_selectionnés[0]
        genre = "e" if prénoms_selectionnés[0][-1] == '♀' else ""
        return f"Il y a {df_nat[masque].nombre.sum()} {prénoms_selectionnés[0]} né{genre}s  en France depuis 1900"


@app.callback(
    Output(component_id='graph-fréquences', component_property='figure'),
    [Input(component_id='dropdown-prénoms', component_property='value')]
)
def maj_graph(prénoms_selectionnés):
    fig = go.Figure()
    for prénom_select in prénoms_selectionnés:
        masque = df_nat.prénoms_s == prénom_select
        fig.add_trace(
            go.Scatter(
                x=df_nat[masque].annais,
                y=df_nat[masque].nombre,
                name=prénom_select,
                text=df_nat[masque].rangs,
                mode='markers+lines',
                hovertemplate='Année : %{x}<br>Nombre : %{y}<br>Rang : <b>%{text}ème</b>'))
        fig.update_layout(
            xaxis=dict(title="Année de naissance"),
            yaxis=dict(title="Nombre de naissances"),
        )
    return fig


if __name__ == '__main__':
    app.run_server()
