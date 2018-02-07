# -*- coding: utf-8 -*-
import pandas
import networkx as nx
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

df_original = pandas.read_csv("connection_strength_norm.csv")
df_original = df_original[df_original.value >= 0.2]

df_regiondata = pandas.read_csv("occurrences_per_cuisine_remove_unused_nodes_normalised.csv")

ingredients = df_original.ingredients

dd_options = [] 
for i in ingredients:
    dd_options.append({'label': i, 'value': i})

app = dash.Dash()
app.layout = html.Div([
    dcc.Dropdown(
        id='ing_dd',
        options=dd_options,
        value=dd_options[0]['label']),
    dcc.Graph(id='network-graph'),
    dcc.Slider(
        id='strength-slider',
        max=df_original['value'].max(),
        value=df_original['value'].min(),
        step=None,
        marks={str(value): str(value) for value in df_original['value'].unique()}
    ),
    dcc.Graph(id='bar-graph') 

])

@app.callback(
    dash.dependencies.Output('bar-graph', 'figure'), 
    [dash.dependencies.Input('ing_dd', 'value')
    ])
def update_bargraph(selected_ingredient):
    bar_traces = []
    bar_traces.append(go.Bar(
        x = list(df_regiondata['Cuisine']),
        y = df_regiondata[selected_ingredient]))
    return {
        'data': bar_traces,
        'layout': go.Layout(
            autosize=True,
            titlefont=dict(size=16),
            showlegend=False,
            height=1000,
            hovermode='closest'
        )
    }

@app.callback(
    dash.dependencies.Output('network-graph', 'figure'),
    [
    dash.dependencies.Input('strength-slider', 'value'),
    dash.dependencies.Input('ing_dd','value')
    ])
def update_figure(selected_strength, selected_ingredient):

    df = df_original[df_original.value >= selected_strength]

    G = nx.convert_matrix.from_pandas_edgelist(df, 'ingredients', 'variable', edge_attr='value')

    pos = nx.spring_layout(G)

    traces = []
    # Draw edges
    edge_trace = go.Scattergl(
        x=[],
        y=[],
        text=[],
        line=go.Line(width=2, color='rgba(0, 0, 0, 0.4'),
        hoverinfo='text',
        mode='lines',
    )
    for edge in G.edges(data=True):
        if edge[2]['value'] > selected_strength:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += [x0, x1, None]
            edge_trace['y'] += [y0, y1, None]
            edge_trace['text'].append(edge[2]['value'])

    # Draw nodes
    colorarray = []
    node_trace = go.Scattergl(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=go.Marker(
            size=20,
            color=colorarray,
            line=dict(
                width=2,
                color='rgba(0, 0, 0, .2)'
            )
        )
    )
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['text'].append(node)
        if node == selected_ingredient:
            colorarray.append('red')
        else:
            colorarray.append('orange')

    traces.append(edge_trace)
    traces.append(node_trace)
    return {
        'data': traces,
        'layout': go.Layout(
            autosize=True,
            titlefont=dict(size=16),
            showlegend=False,
            height=1000,
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server()