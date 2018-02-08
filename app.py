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

# Import CSS
app.css.append_css({'external_url':'https://cdn.rawgit.com/IsaKiko/flavourNW/8808521a/style.css'})
app.layout = html.Div([
    # Header
    html.Div(
        html.H1('~A Dash Of Flavour~'),
         className="header"
    ),
    html.H2('Select an ingredient...'),
    # Dropdown
    html.Div(
        dcc.Dropdown(
              id='ing_dd',
              options=dd_options,
              value=dd_options[0]['label']
        ),
        className="header",
        id='div1'
    ),
    # Network Graph
    html.Div([
        # Slider
        dcc.Slider(
            id='strength-slider',
            max=df_original['value'].max(),
            value=df_original['value'].min(),
            step=df_original['value'].max()/100
            #step=None,
            #marks={str(value): str(value) for value in df_original['value'].unique()}
        ),
        dcc.Graph(
            id='network-graph'
        )],
        id='div2'
    ),
    html.Section([
        html.Div(
            # Map Graph
            dcc.Graph(
                id='map-graph'
            ),
            className='column',
            id='div3'
        ),
        html.Div(
            # Bar Graph
            dcc.Graph(
                id='bar-graph'
            ),
            className="column",
            id='div4'
        )
        ],
        className="columns"
    ),
], className="wrapper")



@app.callback(
    dash.dependencies.Output('bar-graph', 'figure'),
    [dash.dependencies.Input('ing_dd', 'value')
    ])
def update_bargraph(selected_ingredient):
    bar_traces = []
    bar_traces.append(go.Bar(
        y = list(df_regiondata['Cuisine']),
        x = df_regiondata[selected_ingredient],
        orientation="h"))
    return {
        'data': bar_traces,
        'layout': go.Layout(
            margin=dict(l=150),
            autosize=True,
            titlefont=dict(size=16),
            showlegend=False,
            hovermode='closest',
            title="Ingredient popularity"
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

    x_norm = (12-1)*(df.value - df.value.min()) / (df.value.max() - df.value.min())
    df.value = x_norm

    G = nx.convert_matrix.from_pandas_edgelist(df, 'ingredients', 'variable', edge_attr='value')
    pos = nx.shell_layout(G)
    #pos = nx.spectral_layout(G)
    #pos = nx.circular_layout(G)

    #pos = nx.graphviz_layout(G)
    #pos = nx.draw_circular(G)
    #pos = nx.draw_random(G)
    #G=nx.random_geometric_graph(200,0.125)
    #pos=nx.get_node_attributes(G,'pos')

    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        # Draw edges
        edge_traces.append(go.Scattergl(
            x=[x0, x1, None],
            y=[y0, y1, None],
            text=[edge[2]['value']],
            line=go.Line(width=edge[2]['value'],
                         #color='rgba(100, 0, 0, 0.4)',
                         color='rgb(45, 175, 78, 0.4)',
                         ),#dash="dot"),
            hoverinfo='text',
            mode='lines',
        ))


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
                color='rgba(0, 0, 0, 0.4)'
            )
        )
    )

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['text'].append(node)
        if node == selected_ingredient:
            colorarray.append("rgb(45, 175, 78)")
        else:
            colorarray.append('white')

    traces = []

    for trace in edge_traces:
        traces.append(trace)

    traces.append(node_trace)

    return {
        'data': traces,
        'layout': go.Layout(
            title="Ingredients combinations",
            autosize=True,
            height=1000,
            titlefont=dict(size=16),
            showlegend=False,
            hovermode='closest',
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                showticklabels=False
            )
        )
    }


@app.callback(
    dash.dependencies.Output('map-graph', 'figure'),
    [dash.dependencies.Input('ing_dd', 'value')]
    )
def update_map(selected_ingredient):
    df_map = pandas.read_csv('choropleth_norm.csv')
    data = [ dict(
            type='choropleth',
            locations=df_map['CODE'],
            z=df_map[selected_ingredient],
            text=df_map['region'],
            colorscale=[[0,"rgb(238,238,238)"],
                        [0.35,"rgb(78,144,190)"],
                        [0.5,"rgb(118,167,202)"],
                        [0.6,"rgb(158,191,214)"],
                        [0.7,"rgb(198,214,226)"],
                        [1,"rgb(38,120,178)"]],
            autocolorscale=False,
            reversescale=True,
            marker=dict(
                line=dict(
                    color='rgb(180,180,180)',
                    width=0.5
                )),
            showscale=False
    )]
    layout = dict(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection=dict(
                type='Orthographic'
            )
        ),
        title="Ingredient popularity map",
        autosize=True,
        margin=go.Margin(
            l=0,
            r=0,
            b=0,
            pad=0
        ),
    )
    return{
        'data': data,
        'layout': layout
    }


if __name__ == '__main__':
    app.run_server()
