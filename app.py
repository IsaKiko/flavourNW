# -*- coding: utf-8 -*-
import pandas
import networkx as nx
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from sklearn import preprocessing

df_original = pandas.read_csv("connection_strength_norm.csv")
df_original = df_original[df_original.value >= 0.2]

df_regiondata = pandas.read_csv("occurrences_per_cuisine_remove_unused_nodes_normalised.csv")

ingredients = df_original.ingredients

dd_options = []
for i in ingredients:
    dd_options.append({'label': i, 'value': i})

app = dash.Dash()
"""
app.layout = html.Div([
    html.H1(children='~A Dash Of Flavour~'),
    html.Div(children="Naviguate the world of ingredients"),
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
    dcc.Graph(id='bar-graph') ,
    dcc.Graph(id='map-graph')
])
"""

# Import CSS
app.css.append_css({'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css'})
app.layout = html.Div([
    # Dropdown
    html.Div(
    dcc.Dropdown(
        id='ing_dd',
        options=dd_options,
        value=dd_options[0]['label']
     ),
    className="col-4",
    id='div1'
    ),

    # Network Graph
    html.Div(
        dcc.Graph(
            id='network-graph'
        ),
        className="col-4",
        id='div2'
    ),

    # Slider
    html.Div(
        dcc.Slider(
            id='strength-slider',
            max=df_original['value'].max(),
            value=df_original['value'].min(),
            step=None,
            marks={str(value): str(value) for value in df_original['value'].unique()}
    ),
    className="col-4",
    id='div3'
    ),

    # Bar Graph
    html.Div(
        dcc.Graph(
            id='bar-graph'
        ),
        className="col-4",
        id='div4'
    ),

    # map Graph
    html.Div(
        dcc.Graph(id='map-graph'),
        className="col-4",
        id='div4'
    )

], className="row")



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

    """
    #print df.value
    # Scaling values from 1 to 4
    #min_max_scaler = preprocessing.MinMaxScaler()
    #x_scaled min_max_scaler.fit_transform(df.value.values.astype(float))
    # Create x, where x the 'scores' column's values as floats
    x = df[['value']].values.astype(float)
    # Create a minimum and maximum processor object
    min_max_scaler = preprocessing.MinMaxScaler()
    # Create an object to transform the data to fit minmax processor
    x_scaled = min_max_scaler.fit_transform(x)
    # Run the normalizer on the dataframe
    df_normalized = pd.DataFrame(x_scaled)
    """
    #print df_normalized
    #df.value = min_max_scaler.fit_transform(df.value)
    #df.value = (4 -1) * df.value + 1

    #x_norm = (20-1)*(df.value - df.value.min()) / (df.value.max() - df.value.min()) + 1
    #df.value = x_norm

    #df.value = np.log(df.value)

    #df.value

    #print df.value

    G = nx.convert_matrix.from_pandas_edgelist(df, 'ingredients', 'variable', edge_attr='value')
    pos = nx.spring_layout(G)

    traces = []
    # Draw edges
    edge_trace = go.Scattergl(
        x=[],
        y=[],
        text=[],
        line=go.Line(width=1, color='rgba(0, 0, 0, 0.4'),
        hoverinfo='text',
        mode='lines',
    )
    for i, edge in enumerate(G.edges(data=True)):
        #print edge[2]['value']
        if edge[2]['value'] > selected_strength:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += [x0, x1, None]
            edge_trace['y'] += [y0, y1, None]
            edge_trace['text'].append(edge[2]['value'])
            #if i % 2 == 0:
            #    edge_trace['line'] = go.Line(width=edge[2]['value'],
            #                                 color='rgba(0, 0, 0, 0.4')
            #else:
            #    edge_trace['line'] = go.Line(width=4,
            #                                 color='rgba(0, 0, 0, 0.4')
            """
            edge_trace['line'] = go.Line(width=edge[2]['value'],
                                         color='rgba(0, 0, 0, 0.4')
            """
        #edge_trace['line'] = go.Line(width=100,
        #                             color='rgba(0, 0, 0, 0.4')

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
            colorarray.append('white')

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

@app.callback(
    dash.dependencies.Output('map-graph', 'figure'),
    [dash.dependencies.Input('ing_dd', 'value')]
    )
def update_map(selected_ingredient):
    df_map = pandas.read_csv('occurrences_per_cuisine_countries.csv')

    data = [ dict(
            type='choropleth',
            locations=df_map['CODE'],
            z=df_map[selected_ingredient],
            text=df_map['region'],
            colorscale=[[0,"rgb(5, 10, 172)"],
                          [0.35,"rgb(40, 60, 190)"],
                          [0.5,"rgb(70, 100, 245)"],
                          [0.6,"rgb(90, 120, 245)"],
                          [0.7,"rgb(106, 137, 247)"],
                          [1,"rgb(220, 220, 220)"]],
            autocolorscale=False,
            reversescale=True,
            marker=dict(
                line=dict(
                    color='rgb(180,180,180)',
                    width=0.5
                )),
            colorbar=dict(
                autotick=False,
                title='Number of recipes'),
    )]
    layout = dict(
        title="Popularity of " + selected_ingredient,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection=dict(
                type='Orthographic'
            )
        )
    )
    return{
        'data': data,
        'layout': layout
    }



'''
@app.callback(
    dash.dependencies.Output('map-graph', 'figure'),
    [dash.dependencies.Input('ing_dd', 'value')]
    )
def update_map(selected_ingredient):
    df_map = pd.read_csv('occurrences_per_cuisine_countries.csv')

    """
    data = go.Data[dict(
            type = 'choropleth',
            locations = df_map['CODE'],
            z = df_map['black_pepper'],
            text = df_map['region'],
            colorscale = [[0,"rgb(5, 10, 172)"],
                          [0.35,"rgb(40, 60, 190)"],
                          [0.5,"rgb(70, 100, 245)"],
                          [0.6,"rgb(90, 120, 245)"],
                          [0.7,"rgb(106, 137, 247)"],
                          [1,"rgb(220, 220, 220)"]],
            autocolorscale = False,
            reversescale = True,
            marker = dict(
                line = dict(
                    color = 'rgb(180,180,180)',
                    width = 0.5
                )),
            colorbar = dict(
                autotick = False,
                title = 'Number of recipes'),
          )]

    layout = dict(
        title = "Popularity of the INGREDIENT",
        geo = dict(
            showframe = False,
            showcoastlines = False,
            projection = dict(
                type = 'Orthographic'
            )
        )
    )
    """

    data=[ dict(type='scattermapbox',
            lat= lat,
            lon=lon,
            mode='markers',
            text=regions,
            marker=dict(size=0.5, color= '#a490bd'),
            showlegend=False,
            hoverinfo='text'
            )]

    layers=[dict(sourcetype = 'geojson',
                       source =shape,
                       below="water",
                       type = 'fill',
                       color = '#a490bd',
                       opacity=0.8
       )]

    #bar_traces.append(go.Bar(
    #    x = list(df_regiondata['Cuisine']),
    #    y = df_regiondata[selected_ingredient]))

    #fig = dict( data=data, layout=layout )
    #iplot( fig, validate=False, filename='map_ingredient' )

    """
    return {
        'data': data,
        'layout': layers
    }
    """

    return {
        'data': data,
        'layout': go.Layout(
            autosize=True,
            titlefont=dict(size=16),
            showlegend=False,
            height=1000,
            hovermode='closest'
        )
    }
'''


if __name__ == '__main__':
    app.run_server()
