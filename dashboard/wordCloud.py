import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from io import BytesIO
import base64


def generate_wordcloud(text, title, colormap):
    plt.switch_backend('agg')  # Switch to non-interactive backend
    custom_stopwords = STOPWORDS.union({"want", "desire"})
    wc = WordCloud(width=800, height=500, background_color='white'
                   , colormap=colormap, stopwords=custom_stopwords).generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    ax.set_title(title, fontsize=16)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
