# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.plotly as py
import json
from utils import *
#, word_cloud_image

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
print('run')
# Load data
data_dem = json.loads(open('data/democratie.json').read())
data_fisc = json.loads(open('data/fiscalite.json').read())
data_dict = {"Dem":data_dem, "Fis":data_fisc}

def get_data(data_key):
    return data_dict[data_key]

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

overall_stats = ['n_questions', 'n_answers','n_participants', 'answer_rate', 'avg_answer_per_participant']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {'background_right':'#8597AF',
         'background_left' : '#45546B',
         'bar_unselected' : '#2678B2',
         'bar_selected' : '#FD7F28'
         }

chart_axis_font = dict(
                    titlefont=dict(
                        size=12,
                        color='white'),
                    tickfont=dict(
                        color='white'))
chart_title_font = dict(
                    size=16,
                    color='white')

app.layout = html.Div([
    html.H1(children='Visualization Tool for "Le Grand Débat"',
            style={
                'textAlign': 'center',
                'color': "blue"}
            )
            ,
     dcc.Dropdown(
        id='theme_choice',
        options=[
            {'label': u'Démocration et Citoyenneté', 'value': 'Dem'},
            {'label': 'Fiscalité', 'value': 'Fis'},
        ],
        value='Dem'
    ),

    html.Div([
        html.Div([
            html.H2('Interactive Part - Theme & Questions',
                    style={
                        'textAlign': 'center',
                        'color': "white"}
                    ),
            dcc.Dropdown(id='question_choice'),
            dcc.Graph(id='graph_question')],

             style={'width': '59%',
                          'height': '900px',
                          'display': 'inline-block',
                          'padding': '0 0',
                          'background-color':colors["background_left"]}
                )
        ,
        html.Div([
            html.H2('Overview Theme',
                    style={
                        'textAlign': 'center',
                        'color': "white"}
                    ),

            dcc.Graph(id='answer_rate'),
            dcc.Graph(id='global_stats')],

            style={'width': '40.5%',
                    'height': '50%',
                    'float': 'right',
                    'display': 'inline-block',
                    'padding': '0 0',
                    'background-color':colors["background_right"]}),

                    ])

    ])

@app.callback(
    [Output('question_choice', 'options'),
    Output('answer_rate', 'figure'),
    Output('global_stats', 'figure'),
    Output('graph_question', 'figure')],
    [Input('theme_choice', 'value'),
    Input('question_choice','value')])

def update_page(selected_theme, selected_question):
    data = get_data(selected_theme)
    questions_num, answer_rate, question_type, questions, questions_formated = get_questions(data)
    if selected_question==None:
        selected_question=questions_num[0]

    # Reformating possible questions of selected theme for display
    options = [{'label': questions_num[i] + " - " + question, 'value':questions_num[i]} for i, question in enumerate(questions)]

    # Defining specific color for selected question, and creating annotation list
    bar_colors = []
    annotations = []
    for i, question in enumerate(questions_num):
        # Defining color
        if question != selected_question:
            bar_colors.append(colors["bar_unselected"])
        else:
            bar_colors.append(colors["bar_selected"])

        # Annotation list
        annotations.append(dict(x=question, y=answer_rate[i], text="{0:.0f}".format(answer_rate[i]*100) + " %",
                            font=dict(family='Arial', size=20,
                            color='white'),
                            showarrow=False,
                            yshift = 20))

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
        question_data = []
        question_layout = None
    else:
        top_words = top_words_list[selected_question]
        #question_data, question_layout = plotly_wordcloud(top_words)
        question_data, question_layout = word_cloud_image(top_words)

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
            title='Answer Rates',
            titlefont= chart_title_font,
            xaxis = chart_axis_font,
            yaxis = dict(
                    autorange=True,
                    showgrid=False,
                    zeroline=False,
                    showline=False,
                    ticks='',
                    showticklabels=False),
            plot_bgcolor = colors["background_right"],
            paper_bgcolor = colors["background_right"],
            annotations = annotations)
            }

    figure_global_stats= {
        'data':[go.Bar(
                x=values,
                y=stat_names,
                orientation = 'h')],
        'layout': go.Layout(
            title='Global Statistics',
            titlefont= chart_title_font,
            xaxis = chart_axis_font,
            yaxis = chart_axis_font,
            plot_bgcolor = colors["background_right"],
            paper_bgcolor = colors["background_right"])
                    }

    figure_graph_question = {'data': question_data, 'layout': question_layout}

    return options, figure_answer_rate, figure_global_stats, figure_graph_question

if __name__ == '__main__':
    app.run_server(debug=True)
