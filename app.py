# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.plotly as py
import json
import plotly.tools as tools
from utils import *
import seaborn as sns
import numpy as np

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = ["https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css"]

mapbox_access_token = 'pk.eyJ1IjoibWFyaWVpIiwiYSI6ImNqeDR2bG1ybjAxcmc0OG4wdmNza2luYXkifQ.hECaeMskkpv2CoirEUywlg'



# Load data
data_dem = json.loads(open('data/democratie.json').read())
data_fisc = json.loads(open('data/fiscalite.json').read())
data_eco = json.loads(open('data/ecologie.json').read())
data_org = json.loads(open('data/organisation.json').read())
text_dict = json.loads(open('data/theme.txt').read())

with open("data/departements-version-simplifiee.geojson") as geofile:
    geojson_layer = json.load(geofile)


themes = {'Dem':"Démocratie", 'Fis':"Fiscalité", 'Eco':"Ecologie", 'Org':"Organisation"}
data_dict = {'Dem':data_dem, 'Fis':data_fisc, 'Eco':data_eco, 'Org':data_org}

n_answers = {'Dem':2768140, 'Fis':1101287, 'Eco':1857257, 'Org':1414633}

def get_data(data_key):
    return data_dict[data_key]

def get_num_answer(data_key):
    return n_answers[data_key]


def get_stats(data_dict, n_answers):
    n_participants = []
    completion_rates = []
    n_questions = []

    for i,data in enumerate(data_dict.values()):
        n_question = data['n_questions']
        n_answer = list(n_answers.values())[i]
        n_participant = data['n_participants']
        completion_rate = n_answer/(n_participant*n_question)

        n_questions.append(n_question)
        n_participants.append(n_participant)
        completion_rates.append(completion_rate)

    return n_participants, completion_rates, n_questions

def get_questions(data):
    questions_num = list(data.keys())[5:]
    answer_rate = [data[question]['answer_rate'] for question in questions_num]
    question_type = [data[question]['type'] for question in questions_num]
    questions =  [data[question]['question'] for question in questions_num]

    questions_num = [question.upper() for question in questions_num]

    # Formatting string of questions for later display
    questions_formated = []
    split_len = 50
    for question in questions:
        if len(question)<=split_len:
            questions_formated.append(question)
        else:
            split = len(question)//split_len
            questions_formated.append('<br>'.join(
                [question[i:i+split_len] for i in range(0, len(question), split_len)]))

    return questions_num, answer_rate, question_type, questions, questions_formated

def get_question(questions, questions_num, selected_question):
    for i,ques in enumerate(questions):
        if selected_question==questions_num[i]:
            out=ques

    return out


def get_open_questions_words(data):
    top_words_list = {}
    for key in data:
        try:
            if data[key]['type'] == 'open':
                # Take Top 20 occurences in the question corpus
                top_words_list[key.upper()] = data[key]['word_freq'][0:50]
        except:
            pass

    return top_words_list

def color_question(questions_num, selected_question, answer_rate):
    bar_colors = []
    annotations = []
    for i,question in enumerate(questions_num):
        # Defining color
        if question != selected_question:
            bar_colors.append(colors["bar_unselected"])
        else:
            bar_colors.append(colors["bar_selected"])

        # Annotation list
        annotations.append(dict(x=question, y=answer_rate[i], text="{0:.0f}".format(answer_rate[i]*100) + "%",
                            font=dict(family='Arial', size=26,
                            color=bar_colors[i]),
                            showarrow=False,
                            yshift = 16))

    return bar_colors, annotations


def centeroidnp(arr):
    arr = np.array(arr)
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return [sum_x/length, sum_y/length]


# Define color for map per department
# color = sns.diverging_palette(10, 220, sep=10, n=100)
color = sns.diverging_palette(10, 220, sep=20, n=24)
color = color.as_hex()


# Store macro-data at departement level (centroid, code, name) for hovering
departement = [
    dict(
        code = geojson_layer['features'][k]['properties']['code'],
        name=geojson_layer['features'][k]['properties']['nom'],
        centroid=centeroidnp(geojson_layer['features'][k]['geometry']['coordinates'][0])
    )
    for k in range(len(geojson_layer['features']))]


def process_data(dic):

    for k, v in dic.items():
        if k.startswith('q'):
            if v['type']=='open':
                continue
            # For each question, get the list of pct_yes_per_dep
#             print(k)
            else:
                sub_dic = dic[k]['pct_yes_per_dep']
    #             print(sub_dic)
                # Replace the dpt 97/98 by 2A/2B
                sub_dic['2A'] = sub_dic.pop('97')
                sub_dic['2B'] = sub_dic.pop('98')

                # Update dict by reviewed department names
                dic[k]['pct_yes_per_dep'] = sub_dic
                # print(dic[k]['pct_yes_per_dep'])
                for key, value in dic[k]['pct_yes_per_dep'].items():
                    # print(key)
                    # print(value)
                    if key == 'all':
                        continue
                    else:

                        dic[k]['pct_yes_per_dep'][key] = [value, value - dic[k]['pct_yes_per_dep'].get('all', 0)]

    return dic

# Define lon and lat of department centroid
lon = [dep['centroid'][0] for dep in departement]
lat = [dep['centroid'][1] for dep in departement]


# Modify department keys
data_dem = process_data(data_dem)
data_fisc = process_data(data_fisc)
data_eco = process_data(data_eco)
data_org = process_data(data_org)

def define_index_for_color(delta):
    '''
    Given a delta vs. average, define the index of color to display at departement level
    '''
    # Scale to percentage
    delta = round(delta*100 + 11.5)

    # Index of colours goes from 0 to 23, we cap the potential index
    adjusted_value = min(23, max(0, delta))

    return adjusted_value

def get_closed_question_params(data, selected_question):

    dic_answers = data[selected_question.lower()]['pct_yes_per_dep']

    # Define text that will appear when hovering over a department
    hovering_text = ['{} - {}<br>Pourcentage de Oui : {}%<br>Ecart vs. moy. : {}%'.format(dep['code'],dep['name'], round(100*dic_answers[dep['code']][0]), round(100*dic_answers[dep['code']][1])) for dep in departement]

    data = [
        go.Scattermapbox(
            lat= lat,
            lon=lon,
            mode='markers',
            text=hovering_text,
            marker=dict(
                size=0.5,
                color= '#a490bd',
                colorbar=dict(
                    title = '% Oui vs. moyenne',
                    titleside = 'top',
                    tickmode = 'array',
                    tickvals = [0,4.5,9],
                    ticktext = ['>-10','0','>+10'],
                    ticks = 'outside'
                ),
            colorscale=[[idx/23, elem] for idx, elem in enumerate(sns.diverging_palette(10, 220, sep=20, n=24).as_hex())]),
        showlegend=False,
        hoverinfo='text',

        ),
    ]

    layers=[dict(sourcetype = 'geojson',
             source =geojson_layer['features'][k]['geometry'],
             below="water",
             type = 'fill',
             name=geojson_layer['features'][k]['properties']['nom'],
             color = color[define_index_for_color(dic_answers[geojson_layer['features'][k]['properties']['code']][1])],
             opacity=0.8
            ) for k in range(len(geojson_layer['features']))]

    layout = go.Layout(
        title='Pourcentage de Oui - delta vs. moyenne nationale ({}%)'.format(round(100*dic_answers['all'],1)),
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            layers=layers,
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=46.4,
                lon=2.3
            ),
            pitch=0,
            zoom=5.2,
            style='light'
        )
    )

    return data, layout


def theme_opacity(themes, selected_theme,  n_participants, completion_rates):
    bar_opacity = []
    annotations = []

    for i,theme in enumerate(list(themes.keys())):
        # Defining color
        if theme != selected_theme:
            bar_opacity.append(transparency["transparent"])
        else:
            bar_opacity.append(transparency["full"])

        annotations.append(dict(x=list(themes.values())[i], y=n_participants[i], text="{0:.0f}".format(n_participants[i]/1000) + "k",
                                    xref='x1',
                                    yref='y1',
                                    showarrow=False,
                                    yshift = 14,
                                    font=dict(family='Arial', size=26))
                                    )
        annotations.append(dict(x=list(themes.values())[i], y=completion_rates[i]*100, text="{0:.0f}".format(completion_rates[i]*100)+"%",# annotation point
                                    xref='x2',
                                    yref='y2',
                                    showarrow=False,
                                    yshift = 14,
                                    font=dict(family='Arial', size=26))
                                    )


    return bar_opacity, annotations

def get_theme_text(selected_theme):
    text = text_dict[selected_theme]

    return [text]

app = dash.Dash(__name__)

# Load styles
css_file = 'assets/style.css'
css_bootstrap_url = 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css'
app.css.append_css({
    "external_url": [css_bootstrap_url, css_file],
})

text_color = "black"

colors = {'background_content': 'white',#'#8597AF','white',
         'background' : '#e8f1f7',
         'bar_unselected' : '#C5D5E4',
         'bar_selected' : '#19647E'
         }

transparency = {"full":1,
                "transparent":0.5}

chart_axis_font = dict(
                    titlefont=dict(
                        size=12,
                        color=text_color),
                    tickfont=dict(
                        color=text_color))

global_stats_axis_font = [
    dict(
        titlefont=dict(
            size=12,
            color=text_color),
        tickfont=dict(
            color=text_color),
        domain=[0, 0.45]),
    dict(
        titlefont=dict(
            size=12,
            color=text_color),
        tickfont=dict(
            color=text_color),
        domain=[0.55, 1])]

chart_title_font = dict(
                    size=16,
                    color=text_color)

app.layout = html.Div([
    # LANDING
    html.Div(
        className='section',
        children=[
            html.H1('Le grand débat national',
                    className='landing-text')
        ]
    ),

    # themes
    html.Div([
        dcc.Tabs(
            id="tabs",
            className="tabs",
            #style={"height":"20","verticalAlign":"middle"},
            children=[
                dcc.Tab(label="Démocratie et Citoyenneté", value="Dem"),
                dcc.Tab(label="Fiscalité et Dépenses Publiques", value="Fis"),
                dcc.Tab(label="Transition Écologique", value="Eco"),
                dcc.Tab(label="Organisation de l'État et Service Public", value="Org"),
            ],
            value="Dem",
        )

        ],
        className="card-text",

        ),




        html.Div([
            html.Div([html.P(id="text_theme",
                            style={'font-size':'200%',
                                    'font-style':'italic',
                                    'line-height':'50px',
                                    'position': 'relative',
                                    'top': '+22.5%',
                                    'border-left':'30px white solid',
                                    'border-right':'20px white solid'
                                    })
                            ],
                        style={'width': '40%',
                                'height': 550,
                                'display': 'inline-block',
                                'background-color':colors['background_content'],
                                'border-left': "20px #e8f1f7 solid",
                                'border-top': "20px #e8f1f7 solid",
                                }),

            html.Div([html.H2('Nombre de Participants',
                        style={
                            'display': 'inline-block',
                            'width':'50%',
                            'text-align':'center',
                            'color': "black",
                            'border-top': "20px white solid"}),

                    html.H2("  Niveau d'implication des participants",
                        style={
                            'float': 'right',
                            'width':'50%',
                            'text-align':'center',
                            'color': "black",
                            'border-top': "20px white solid"}),

                    dcc.Graph(id='global_stats',
                              style={
                                  'height': 525,
                                  "display": "block",
                                  "margin-top": -75})],

                        style={'width': '60%',
                                'height': 600,
                                'float':'right',
                                'border-left': "20px #e8f1f7 solid",
                                'border-right': "20px #e8f1f7 solid",
                                'border-top': "20px #e8f1f7 solid"
                                })],
                style={'width': '100%',
                        'height': 600,
                        'background-color':colors['background_content']
                        }),

        html.Div([
            html.Div([
                html.H2('Choisir une Question',
                        style={
                            'textAlign': 'center',
                            'color': "black",
                            'border-top': "10px white solid"}
                        ),

                dcc.Tabs(
                    id="question_choice",
                    className="tab",
                    value='Q1'),

                html.Div([html.P(id="text_question",
                                style={'font-size':'200%',
                                        'font-style':'italic',
                                        'line-height':'50px',
                                        'position': 'relative',
                                        'textAlign': 'center',
                                        'border-left':'30px white solid',
                                        'border-right':'20px white solid'
                                        })
                                ],
                            style={'width': '100%',
                                    'height': 200,
                                    'display': 'inline-block',
                                    'background-color':colors['background_content']
                                    }),

                dcc.Graph(id='figure_questions',
                            style={'border-left': "100px white solid",
                                    'height': '75%',
                                    'width': '80%',
                                    'margin-top': -60})],

                style={'width': '59%',
                       'height': 1300,
                       'display': 'inline-block',
                       'border-left': "20px #e8f1f7 solid",
                       'border-top': "20px #e8f1f7 solid",}),

            html.Div([

                html.H2('Taux de réponse par Question',
                    style={
                        'textAlign': 'center',
                        'color': "black",
                        'border-top': "10px white solid"}),

                dcc.Graph(id='answer_rate',
                          style={
                            'height': 500,
                            "display": "block",
                            "margin-top": 300,
                            "margin-left": "auto",
                            "margin-right": "auto"})],

                style={'width': '41%',
                        'height': 1300,
                        'float': 'right',
                        'display': 'inline-block',
                        'border-left': "20px #e8f1f7 solid",
                        'border-right': "20px #e8f1f7 solid",
                        'border-top': "20px #e8f1f7 solid",
                        'margin':"50px blue solid"}),

                    ])],

                    style={'background-color':colors["background_content"]}

                    )



@app.callback(
    [Output('question_choice', 'children'),
    Output('answer_rate', 'figure'),
    Output('global_stats', 'figure'),
    Output('figure_questions', 'figure'),
    Output('text_theme', 'children'),
    Output('text_question', 'children')],
    [Input('tabs', 'value'),
    Input('question_choice','value')])

def update_page(selected_theme, selected_question):
    data = get_data(selected_theme)
    text_theme = get_theme_text(selected_theme)
    questions_num, answer_rate, question_type, questions, questions_formated = get_questions(data)
    n_participants, completion_rates, n_questions = get_stats(data_dict, n_answers)


    if selected_question==None:
        selected_question=questions_num[0]

    # Reformating possible questions of selected theme for display
    options = [dcc.Tab(label=questions_num[i], value=questions_num[i]) for i,question in enumerate(questions)]

    question = get_question(questions, questions_num, selected_question)

    # Defining specific color for selected question, and creating annotation list
    bar_colors, annotations_1 = color_question(questions_num, selected_question, answer_rate)
    bar_opacity, annotations_2 = theme_opacity(themes, selected_theme,  n_participants, completion_rates)


    # Extract the more frequent words of the theme open questions
    top_words_list = get_open_questions_words(data)

    # Choosing the good chart (map or wordcloud)
    if question_type[questions_num.index(selected_question)]=="binary":
        # If binary question : figure=heatmap
        # TO DO cf Théo
        quest = questions_num.index(selected_question)
        data_binary, layout_binary = get_closed_question_params(data, selected_question)
        question_data = data_binary
        question_layout = layout_binary


    else:
        top_words = top_words_list[selected_question]
        #question_data, question_layout = plotly_wordcloud(top_words)
        question_data, question_layout = word_cloud_image(top_words)

    figure_questions = {'data': question_data,
                        'layout': question_layout}



    figure_answer_rate = {
        'data':[go.Bar(
                x=questions_num,
                y=answer_rate,
                orientation = 'v',
                textposition = 'outside',
                hoverinfo = 'text',
                hovertext = questions_formated,
                hoverlabel = dict(bgcolor='#F3F1F3',
                                  namelength=-1,
                                  font = dict(color='#8597AF')),
                marker = dict(color=bar_colors)
                            )],
        'layout': go.Layout(
            titlefont= chart_title_font,
            xaxis = chart_axis_font,
            yaxis = dict(
                    autorange=True,
                    showgrid=False,
                    zeroline=False,
                    showline=False,
                    ticks='',
                    showticklabels=False),
            plot_bgcolor = colors["background_content"],
            paper_bgcolor = colors["background_content"],
            font=dict(family='Arial', size=26),
            annotations = annotations_1)
            }

    y_axis_dict = dict(
            showline=False,
            autorange=True,
            showgrid=False,
            zeroline=False,
            showticklabels=False)

    figure_global_stats = {
        'data':[go.Bar(
                    y=n_participants,
                    x=list(themes.values()),
                    xaxis='x1',
                    yaxis='y1',
                    marker = dict(opacity=bar_opacity),
                    hoverinfo = "none"),
                go.Bar(
                    y = [rate*100 for rate in completion_rates],
                    x =list(themes.values()),
                    xaxis ='x2',
                    yaxis ='y2',
                    marker = dict(opacity=bar_opacity),
                    hoverinfo = "none")],
        'layout': go.Layout(
            showlegend = False,
            grid = dict(rows= 1, columns= 2),
            xaxis1 = global_stats_axis_font[0],
            xaxis2 = global_stats_axis_font[1],
            yaxis1 = y_axis_dict,
            yaxis2 = y_axis_dict,
            annotations = annotations_2,
            font=dict(family='Arial', size=26),
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)')
                    }



    return options, figure_answer_rate, figure_global_stats, figure_questions, text_theme, question


if __name__ == '__main__':
    app.run_server(debug=True)
