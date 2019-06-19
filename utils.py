import pandas as pd
import plotly as py
import plotly.graph_objs as go
import random
import numpy as np
from wordcloud import WordCloud



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

    #figure = go.Figure(data=[data], layout=layout)
    return [data], layout




    '''def word_cloud_image(top_words):
        word_freq_dict = {}
        for word_freq in top_words:
            word_freq_dict[word_freq[0]] = word_freq[1]

        wordcloud = WordCloud(max_font_size=40, background_color="white")
        wordcloud.generate_from_frequencies(word_freq_dict)
        word_cloud_image = wordcloud.to_image()

        data = []

        layout = go.Layout(images=[dict(
              source=word_cloud_image,
              xref="paper", yref="paper",
              x=1, y=1.05,
              sizex=0.2, sizey=0.2,
              xanchor="right", yanchor="bottom"
            )],
              {'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
               'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

        return data, layout'''
