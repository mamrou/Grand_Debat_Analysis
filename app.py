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

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = ["https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css"]




# Load data
data_dem = json.loads(open('data/democratie.json').read())
data_fisc = json.loads(open('data/fiscalite.json').read())
data_eco = json.loads(open('data/ecologie.json').read())
data_org = json.loads(open('data/organisation.json').read())
text_dict = json.loads(open('data/theme.txt').read())

themes = {'Dem':"Démocratie et Citoyenneté", 'Fis':"Fiscalité", 'Eco':"Ecologie", 'Org':"Organisation"}
data_dict = {'Dem':data_dem, 'Fis':data_fisc, 'Eco':data_eco, 'Org':data_org}

overall_stats = ['n_questions', 'n_answers','n_participants', 'answer_rate', 'avg_answer_per_participant']
n_answers = {'Dem':2768140, 'Fis':1101287, 'Eco':1857257, 'Org':1414633}

def get_data(data_key):
    return data_dict[data_key]

def get_num_answer(data_key):
    return n_answers[data_key]


def get_stats(data_dict, overall_stats):
    n_questions=[]
    n_participants = []
    answer_rate = []
    avg_answer_per_participant = []

    for i,data in enumerate(data_dict.values()):
        n_questions.append(data['n_questions'])
        n_participants.append(data['n_participants'])
        answer_rate.append(data['answer_rate'])
        avg_answer_per_participant.append(data['avg_answer_per_participant'])

    return n_questions, n_participants, answer_rate, avg_answer_per_participant


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
                            font=dict(family='Arial', size=14,
                            color=bar_colors[i]),
                            showarrow=False,
                            yshift = 16))

    return bar_colors, annotations

def theme_opacity(themes, selected_theme, n_questions, n_answers, n_participants, avg_answer_per_participant):
    bar_opacity = []
    annotations = []

    for i,theme in enumerate(list(themes.keys())):
        # Defining color
        if theme != selected_theme:
            bar_opacity.append(transparency["transparent"])
        else:
            bar_opacity.append(transparency["full"])

        annotations.append(dict(x=theme, y=n_questions[i], text=str(n_questions[i]),
                                    xref='x1',
                                    yref='y1',
                                    showarrow=False,
                                    yshift = 14)
                                    )
        annotations.append(dict(x=theme, y=list(n_answers.values())[i], text="{0:.1f}".format(list(n_answers.values())[i]/1e6) + "M",# annotation point
                                    xref='x2',
                                    yref='y2',
                                    showarrow=False,
                                    yshift = 14)
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
         'background' : '#e8f1f7', #'#45546B',
         'bar_unselected' : '#2678B2',
         'bar_selected' : '#FD7F28'
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
            html.H1('Etudes des propositions citoyennes du Grand Débat', className='landing-text')
        ]
    ),

    # themes
    html.Div([
        dcc.Tabs(
            id="tabs",
            className="tabs",
            #style={"height":"20","verticalAlign":"middle"},
            children=[
                dcc.Tab(label="Démocration et Citoyenneté", value="Dem"),
                dcc.Tab(label="Fiscalité et dépenses publiques", value="Fis"),
                dcc.Tab(label="Transition écologique", value="Eco"),
                dcc.Tab(label="Organisation de l'état et service publique", value="Org"),
            ],
            value="Dem",
        )

        ],
        className="card-text",

        ),




        html.Div([
            html.Div([html.P(id="text_theme",
                            style={'font-size':'32px',
                                    'font-style':'italic',
                                    'line-height':'50px',
                                    'position': 'relative',
                                    'top': '+22.5%',
                                    'border-left':'30px white solid',
                                    'border-right':'20px white solid'
                                    })
                            ],
                        style={'width': '40%',
                                'height': '550px',
                                'display': 'inline-block',
                                'background-color':colors['background_content'],
                                'border-left': "20px #e8f1f7 solid",
                                'border-top': "20px #e8f1f7 solid",
                                }),

            html.Div([html.H2('Nombre de Participants',
                        style={
                            'display': 'inline-block',
                            'margin-left':'200px',
                            'color': "black",
                            'border-top': "20px white solid"}),

                    html.H2('Pourcentage de',
                        style={
                            'float': 'right',
                            'margin-right':'200px',
                            'color': "black",
                            'border-top': "20px white solid"}),

                    dcc.Graph(id='global_stats')],
                        style={'width': '60%',
                                'height': '550px',
                                'float':'right',
                                'border-left': "20px #e8f1f7 solid",
                                'border-right': "20px #e8f1f7 solid",
                                'border-top': "20px #e8f1f7 solid"
                                })],
                style={'width': '100%',
                        'height': '500px',
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
                dcc.Dropdown(id='question_choice' , value='Q1'),

                dcc.Graph(id='figure_questions')],

                style={'width': '59%',
                       'height': '800px',
                       'display': 'inline-block',
                       'border-left': "20px #e8f1f7 solid",
                       'border-top': "20px #e8f1f7 solid",}),

            html.Div([

                html.H2('Taux de réponse par Question',
                    style={
                        'textAlign': 'center',
                        'color': "black",
                        'border-top': "10px white solid"}),

                dcc.Graph(id='answer_rate')],

                style={'width': '41%',
                        'height': '800px',
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
    [Output('question_choice', 'options'),
    Output('answer_rate', 'figure'),
    Output('global_stats', 'figure'),
    Output('figure_questions', 'figure'),
    Output('text_theme', 'children')],
    [Input('tabs', 'value'),
    Input('question_choice','value')])

def update_page(selected_theme, selected_question):
    data = get_data(selected_theme)
    text_theme = get_theme_text(selected_theme)
    questions_num, answer_rate, question_type, questions, questions_formated = get_questions(data)
    n_questions, n_participants, theme_answer_rate, avg_answer_per_participant = get_stats(data_dict, overall_stats)

    if selected_question==None:
        selected_question=questions_num[0]

    # Reformating possible questions of selected theme for display
    options = [{'label': questions_num[i] + " - " + question, 'value':questions_num[i]} for i,question in enumerate(questions)]

    # Defining specific color for selected question, and creating annotation list
    bar_colors, annotations_1 = color_question(questions_num, selected_question, answer_rate)
    bar_opacity, annotations_2 = theme_opacity(themes, selected_theme, n_questions, n_answers, n_participants, avg_answer_per_participant)

    # Getting global statistics for selected theme
    stat_names = overall_stats
    values = []
    for stat in stat_names:
        values.append(data[stat])

    # Extract the more frequent words of the theme open questions
    top_words_list = get_open_questions_words(data)

    # Choosing the good chart (map or wordcloud)
    if question_type[questions_num.index(selected_question)]=="binary":
        # If binary question : figure=heatmap
        # TO DO cf Théo
        question_data = [go.Bar(x=["MAP"], y=[0])]
        question_layout = None


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
            annotations = annotations_1)
            }

    y_axis_dict = dict(
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False)

    figure_global_stats = {
        'data':[go.Bar(
                    y=n_questions,
                    x=list(data_dict.keys()),
                    xaxis='x1',
                    yaxis='y1',
                    marker = dict(opacity=bar_opacity),
                    hoverinfo = "none"),
                go.Bar(
                    y= list(n_answers.values()),
                    x=list(data_dict.keys()),
                    xaxis='x2',
                    yaxis='y2',
                    marker = dict(opacity=bar_opacity),
                    hoverinfo = "none")],
        'layout': go.Layout(
            showlegend=False,
            grid= dict(rows= 1, columns= 2),
            xaxis1=global_stats_axis_font[0],
            xaxis2=global_stats_axis_font[1],
            yaxis1 = y_axis_dict,
            yaxis2 = y_axis_dict,
            annotations=annotations_2,
            titlefont= chart_title_font,
            plot_bgcolor = colors["background_content"],
            paper_bgcolor = colors["background_content"])
                    }



    return options, figure_answer_rate, figure_global_stats, figure_questions, text_theme


if __name__ == '__main__':
    app.run_server(debug=True)
