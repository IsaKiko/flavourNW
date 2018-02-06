# -*- coding: utf-8 -*-
import pandas
import networkx as nx
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

df = pandas.read_csv("srep00196-s2.csv", header=None, names=['ingredient1', 'ingredient2', 'popularity'])
G = nx.convert_matrix.from_pandas_edgelist(df, 'ingredient1', 'ingredient2', edge_attr='popularity')
pos = nx.spring_layout(G, k=1)

# Draw edges
edge_trace = go.Scattergl(
    x=[],
    y=[],
    line=go.Line(width=0.1,color='rgba(0, 0, 0, 0.5'),
    hoverinfo='text',
    mode='lines'
)

for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_trace['x'] += [x0, x1, None]
    edge_trace['y'] += [y0, y1, None]

edge_trace['text'] = list(df['popularity'])
# Draw nodes
node_trace = go.Scattergl(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=go.Marker(
        size=10,
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



app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='Plotly tests'),

    dcc.Graph(
        id='example-graph',
        figure=go.Figure(data=go.Data([edge_trace, node_trace]),
             layout=go.Layout(
                autosize=True,
                titlefont=dict(size=16),
                showlegend=False,
                height=1500,
                hovermode='closest',
                xaxis=go.XAxis(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=go.YAxis(showgrid=False, zeroline=False, showticklabels=False)))
        )
])

if __name__ == '__main__':
    app.run_server(debug=True)