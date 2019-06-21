import pandas as pd
import plotly as py
import plotly.graph_objs as go
import random
import numpy as np
from wordcloud import WordCloud

import matplotlib

# Special backend needed on macOS
matplotlib.use('TkAgg')
#import matplotlib.pyplot as plt



# First type of wordcloud
def plotly_wordcloud(top_words):
    words = []
    frequency = []
    word_freq_dict = {}
    for word_freq in top_words:
        words.append(word_freq[0])
        frequency.append(word_freq[1])
        word_freq_dict[word_freq[0]] = word_freq[1]

    lower, upper = 15, 55
    sum_freq = np.sum(frequency)
    percent = frequency/sum_freq

    frequency = [((x - min(frequency)) / (max(frequency) - min(frequency))) * (upper - lower) + lower for x in frequency]

    lenth = len(words)
    colors = [py.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(lenth)]

    data = go.Scatter(
        x=list(range(lenth)),
        y=random.choices(range(lenth), k=lenth),
        mode='text',
        text=words,
        hovertext=['% fréquence : {2}'.format(w, f, format(p, '.2%')) for w, f, p in zip(words, frequency, percent)],
        hoverinfo='text',
        textfont={'size': frequency, 'color': colors})

    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

    return [data], layout



#  Second type of wordcloud
def word_cloud_image(top_words):
    word_freq_dict = {}
    for word_freq in top_words:
        word_freq_dict[word_freq[0]] = word_freq[1]

    wordcloud = WordCloud(max_font_size=40, background_color="white")
    wordcloud.generate_from_frequencies(word_freq_dict)
    word_cloud_image = wordcloud.to_image()

    img_width = 2200
    img_height = 1000
    scale_factor = 0.5

    data=[{'x': [0, img_width*scale_factor],
            'y': [0, img_height*scale_factor],
            'mode': 'markers',
            'marker': {'opacity': 0}}]

    layout = go.Layout(
        xaxis = go.layout.XAxis(
            visible = False,
            range = [0, img_width*scale_factor]),
        yaxis = go.layout.YAxis(
            visible=False,
            range = [0, img_height*scale_factor],
            # the scaleanchor attribute ensures that the aspect ratio stays constant
            scaleanchor = 'x'),
        width = img_width*scale_factor,
        height = img_height*scale_factor,
        margin = {'l': 0, 'r': 0, 't': 0, 'b': 0},
        images = [go.layout.Image(
            x=0,
            sizex=img_width*scale_factor,
            y=img_height*scale_factor,
            sizey=img_height*scale_factor,
            xref="x",
            yref="y",
            opacity=1.0,
            layer="below",
            sizing="stretch",
            source=word_cloud_image)]
    )

    #data = []

    return data, layout
