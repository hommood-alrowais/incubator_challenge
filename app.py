# Stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Colors
colors = {
    'background': '#ffffff',
    'text': '#696969',
    'header_table': '#ffedb3'
}

# Markdown text
markdown_text1 = '''

This application gathers the latest news from the newspapers **El Pais**, **The Guardian** and **The Mirror**, predicts their category between **Politics**, **Business**, **Entertainment**, **Sport**, **Tech** and **Other** and then shows a graphic summary.

The news categories are predicted with a Support Vector Machine model.

Please enter which newspapers would you like to scrape news off and press **Submit**:

'''

markdown_text2 = '''

*The scraped news are converted into a numeric feature vector with TF-IDF vectorization. Then, a Support Vector Classifier is applied to predict each category.*

\n
\n
Warning: The Mirror takes approximately 30 seconds to gather the news articles.
\n
Created by Miguel Fernández Zafra.
'''

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    # Title
    html.H1(children='News Classification App',
            style={
                'textAlign': 'left',
                'color': colors['text'],
                'padding': '20px',
                'backgroundColor': colors['header_table']

            },
            className='banner',
            ),

    # Sub-title Left
    html.Div([
        dcc.Markdown(children=markdown_text1)],
        style={'width': '49%', 'display': 'inline-block'}),

    # Sub-title Right
    html.Div([
        dcc.Markdown(children=markdown_text2)],
        style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),

    # Space between text and dropdown
    html.H1(id='space', children=' '),

    # Dropdown
    html.Div([
        dcc.Dropdown(
            options=[
                {'label': 'El Pais English', 'value': 'EPE'},
                {'label': 'The Guardian', 'value': 'THG'},
                {'label': 'The Mirror', 'value': 'TMI'}
            ],
            value=['EPE', 'THG'],
            multi=True,
            id='checklist')],
        style={'width': '40%', 'display': 'inline-block', 'float': 'left'}),

    # Button
    html.Div([
        html.Button('Submit', id='submit', type='submit')],
        style={'float': 'center'}),

    # Output Block
    html.Div(id='output-container-button', children=' '),

    # Graph1
    html.Div([
        dcc.Graph(id='graph1')],
        style={'width': '49%', 'display': 'inline-block'}),

    # Graph2
    html.Div([
        dcc.Graph(id='graph2')],
        style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),

    # Table title
    html.Div(id='table-title', children='You can see a summary of the news articles below:'),

    # Space
    html.H1(id='space2', children=' '),

    # Table
    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in ['Article Title', 'Article Link', 'Newspaper', 'Prediction']],
            style_data={'whiteSpace': 'normal'},
            style_as_list_view=True,
            style_cell={'padding': '5px', 'textAlign': 'left', 'backgroundColor': colors['background']},
            style_header={
                'backgroundColor': colors['header_table'],
                'fontWeight': 'bold'
            },
            style_table={
                'maxHeight': '300',
                'overflowY': 'scroll'

            },
            css=[{
                'selector': '.dash-cell div.dash-cell-value',
                'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
            }]
        )],
        style={'width': '75%', 'float': 'left', 'position': 'relative', 'left': '12.5%', 'display': 'inline-block'}),

    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'})

])


@app.callback(
    Output('intermediate-value', 'children'),
    [],
    [State('checklist', 'value')],
    [Event('submit', 'click')])
def scrape_and_predict(values):
    df_features = pd.DataFrame()
    df_show_info = pd.DataFrame()

    if 'EPE' in values:
        # Get the scraped dataframes
        df_features = df_features.append(get_news_elpais()[0])
        df_show_info = df_show_info.append(get_news_elpais()[1])

    if 'THG' in values:
        df_features = df_features.append(get_news_theguardian()[0])
        df_show_info = df_show_info.append(get_news_theguardian()[1])

    if 'TMI' in values:
        df_features = df_features.append(get_news_themirror()[0])
        df_show_info = df_show_info.append(get_news_themirror()[1])

    df_features = df_features.reset_index().drop('index', axis=1)

    # Create features
    features = create_features_from_df(df_features)
    # Predict
    predictions = predict_from_features(features)
    # Put into dataset
    df = complete_df(df_show_info, predictions)
    # df.to_csv('Tableau Teaser/df_tableau.csv', sep='^')  # export to csv to work out an example in Tableau

    return df.to_json(date_format='iso', orient='split')


@app.callback(
    Output('graph1', 'figure'),
    [Input('intermediate-value', 'children')])
def update_barchart(jsonified_df):
    df = pd.read_json(jsonified_df, orient='split')

    # Create a summary df
    df_sum = df.groupby(['Newspaper', 'Prediction']).count()['Article Title']

    # Create x and y arrays for the bar plot for every newspaper
    if 'El Pais English' in df_sum.index:

        df_sum_epe = df_sum['El Pais English']
        x_epe = ['Politics', 'Business', 'Entertainment', 'Sport', 'Tech', 'Other']
        y_epe = [[df_sum_epe['politics'] if 'politics' in df_sum_epe.index else 0][0],
                 [df_sum_epe['business'] if 'business' in df_sum_epe.index else 0][0],
                 [df_sum_epe['entertainment'] if 'entertainment' in df_sum_epe.index else 0][0],
                 [df_sum_epe['sport'] if 'sport' in df_sum_epe.index else 0][0],
                 [df_sum_epe['tech'] if 'tech' in df_sum_epe.index else 0][0],
                 [df_sum_epe['other'] if 'other' in df_sum_epe.index else 0][0]]
    else:
        x_epe = ['Politics', 'Business', 'Entertainment', 'Sport', 'Tech', 'Other']
        y_epe = [0, 0, 0, 0, 0, 0]

    if 'The Guardian' in df_sum.index:

        df_sum_thg = df_sum['The Guardian']
        x_thg = ['Politics', 'Business', 'Entertainment', 'Sport', 'Tech', 'Other']
        y_thg = [[df_sum_thg['politics'] if 'politics' in df_sum_thg.index else 0][0],
                 [df_sum_thg['business'] if 'business' in df_sum_thg.index else 0][0],
                 [df_sum_thg['entertainment'] if 'entertainment' in df_sum_thg.index else 0][0],
                 [df_sum_thg['sport'] if 'sport' in df_sum_thg.index else 0][0],
                 [df_sum_thg['tech'] if 'tech' in df_sum_thg.index else 0][0],
                 [df_sum_thg['other'] if 'other' in df_sum_thg.index else 0][0]]
    else:
        x_thg = ['Politics', 'Business', 'Entertainment', 'Sport', 'Tech', 'Other']
        y_thg = [0, 0, 0, 0, 0, 0]

    if 'The Mirror' in df_sum.index:

        df_sum_tmi = df_sum['The Mirror']
        x_tmi = ['Politics', 'Business', 'Entertainment', 'Sport', 'Tech', 'Other']
        y_tmi = [[df_sum_tmi['politics'] if 'politics' in df_sum_tmi.index else 0][0],
                 [df_sum_tmi['business'] if 'business' in df_sum_tmi.index else 0][0],
                 [df_sum_tmi['entertainment'] if 'entertainment' in df_sum_tmi.index else 0][0],
                 [df_sum_tmi['sport'] if 'sport' in df_sum_tmi.index else 0][0],
                 [df_sum_tmi['tech'] if 'tech' in df_sum_tmi.index else 0][0],
                 [df_sum_tmi['other'] if 'other' in df_sum_tmi.index else 0][0]]

    else:
        x_tmi = ['Politics', 'Business', 'Entertainment', 'Sport', 'Tech', 'Other']
        y_tmi = [0, 0, 0, 0, 0, 0]

    # Create plotly figure
    figure = {
        'data': [
            {'x': x_epe, 'y': y_epe, 'type': 'bar', 'name': 'El Pais'},
            {'x': x_thg, 'y': y_thg, 'type': 'bar', 'name': 'The Guardian'},
            {'x': x_tmi, 'y': y_tmi, 'type': 'bar', 'name': 'The Mirror'}
        ],
        'layout': {
            'title': 'Number of news articles by newspaper',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            }
        }
    }

    return figure


@app.callback(
    Output('graph2', 'figure'),
    [Input('intermediate-value', 'children')])
def update_piechart(jsonified_df):
    df = pd.read_json(jsonified_df, orient='split')

    # Create a summary df
    df_sum = df['Prediction'].value_counts()

    # Create x and y arrays for the bar plot
    x = ['Politics', 'Business', 'Entertainment', 'Sport', 'Tech', 'Other']
    y = [[df_sum['politics'] if 'politics' in df_sum.index else 0][0],
         [df_sum['business'] if 'business' in df_sum.index else 0][0],
         [df_sum['entertainment'] if 'entertainment' in df_sum.index else 0][0],
         [df_sum['sport'] if 'sport' in df_sum.index else 0][0],
         [df_sum['tech'] if 'tech' in df_sum.index else 0][0],
         [df_sum['other'] if 'other' in df_sum.index else 0][0]]

    # Create plotly figure
    figure = {
        'data': [
            {'values': y,
             'labels': x,
             'type': 'pie',
             'hole': .4,
             'name': '% of news articles'}
        ],

        'layout': {
            'title': '% of news articles',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            }
        }

    }

    return figure


@app.callback(
    Output('table', 'data'),
    [Input('intermediate-value', 'children')])
def update_table(jsonified_df):
    df = pd.read_json(jsonified_df, orient='split')
    data = df.to_dict('rows')
    return data


# Loading CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})