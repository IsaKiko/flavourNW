# -*- coding: utf-8 -*-
import pandas
import networkx as nx
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

df = pandas.read_csv("connection_strength_norm.csv")

G = nx.convert_matrix.from_pandas_edgelist(df, 'ingredients', 'variable', edge_attr='value')
pos = nx.spring_layout(G)
app = dash.Dash()

app.layout = html.Div([
    dcc.Graph(id='network-graph'),
    dcc.Slider(
        id='strength-slider',
        max=df['value'].max(),
        value=df['value'].min(),
        step=None,
        marks={str(value): str(value) for value in df['value'].unique()}
    )
])


@app.callback(
    dash.dependencies.Output('network-graph', 'figure'),
    [dash.dependencies.Input('strength-slider', 'value')])
def update_figure(selected_strength):
    traces = []
    # Draw edges
    edge_trace = go.Scattergl(
        x=[],
        y=[],
        text=[],
        line=go.Line(width=0.5, color='rgba(0, 0, 0, 0.8'),
        hoverinfo='text',
        mode='lines'
    )
    for edge in G.edges(data=True):
        if edge[2]['value'] > selected_strength:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += [x0, x1, None]
            edge_trace['y'] += [y0, y1, None]
            edge_trace['text'].append(edge[2]['value'])

    # Draw nodes
    node_trace = go.Scattergl(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=go.Marker(
            size=20,
            line=dict(
                width=2,
                color='rgba(0, 0, 0, .8)'
            )
        )
    )
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['text'].append(node)

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