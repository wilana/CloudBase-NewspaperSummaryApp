import streamlit as st
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from newspaper import Article


# ----------- Functions --------------

# Summarize text using SpaCy's pre-trained NLP
# text is the text to summarize, per is the percent amount to summarize
# code from https://www.activestate.com/blog/how-to-do-text-summarization-with-python/
def summarize(text, per):
    # load the NLP pipeline (English)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    # divide text into grammatical segments (words, punctuation, etc.)
    tokens = [token.text for token in doc]
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                # number of times word is used if not a common word/punctuation
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    # normalize the count (more frequent = higher count)
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency
    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}

    # find the sentences' words' normalized sum
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    # only grab the sentences with the highest normalized sum
    select_length = int(len(sentence_tokens) * per)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary = ''.join(final_summary)
    return summary


# ----------- Main --------------

# Set page title in web browser
st.set_page_config(page_title="Wilana's Cloud Project")

# intro titles
st.title("News Article Summarizer")
st.subheader("By: Wilana Matthews (1120464)")

# formatting to have user input smaller and centered
col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    # user input
    default_article = "https://news.mit.edu/2022/solving-brain-dynamics-gives-rise-flexible-machine-learning-models-1115"
    user_article = st.text_input("Enter article url: ", default_article)

    per_summary = st.slider("Length of summary (as a percent of original text): ", min_value=5, max_value=95, value=20)

# if the site or percent is updated, run the summarizer and display
if user_article or per_summary:
    try:
        # get article
        article = Article(user_article)
        article.download()
        article.parse()

        # get the percent to summarize to
        per_summary = per_summary / 100
        newText = summarize(article.text, per_summary)


        # display summary
        st.header(article.title)
        st.caption(f'Author(s): {article.authors}')
        if article.has_top_image():
            st.image(article.top_img)
        st.write(newText)
    except:
        st.header("OOPS!")
        st.write("I don't like that...\nPlease enter a different article url and/or change the requested length")
