import bs4 as bs  
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import heapq
import stop_words
import wikipedia
import requests
from nltk.corpus import wordnet

# Have the set of stopwords which you want to later filter out
stop_words = stop_words.stopWords

# Returns the url of search results based on search term

# Asks user what topic they would like summarized
def asktopic():
    topic_ask = input("What topic would you like to summarize? \n")
    return topic_ask

# Converts the topic url to text by parsing through html
def scrape_page():
    global article, formatted_text, paragraphs
    scraped_page = requests.get(url)
    article = scraped_page.text
    parsed_article = bs.BeautifulSoup(article,'html.parser')
    paragraphs = parsed_article.find_all('p')
    text = ""
    for p in paragraphs:  
        text += p.text
    article = re.sub(r'\s+', ' ', text)
    formatted_text = re.sub('[^a-zA-Z]', " ", article)
    formatted_text = re.sub(r'\s+', " ", formatted_text)

    
def topic_to_text():   
    global article, formatted_text, paragraphs, url
    topic_ask = asktopic()
    url = wikipedia.page(topic_ask).url
    scrape_page()
   

# Tokenizes the text into words and sentences
def tokenize():
    global sentences, words
    sentences = sent_tokenize(article)
    words = word_tokenize(formatted_text)

""" Creates a dictionary of important words with the keys as 
  words and values as their relative frequencies. """
def word_frequency_dict_creator():
    global word_frequency_dictionary
    word_frequency_dictionary = dict() # Dictionary of words and their frequencies
    for word in words:
        if word not in stop_words:
            if word not in word_frequency_dictionary.keys():
                word_frequency_dictionary[word] = 1
            else:
                word_frequency_dictionary[word] += 1
    max_frequency = max(word_frequency_dictionary.values())
    
    # Relative frequency of words in the frequency dictionary
    for word in word_frequency_dictionary:
        word_frequency_dictionary[word] = word_frequency_dictionary[word]/max_frequency

#Creates a dictionary of sentences and their scores based on the word frequency
def sentence_freq_score_calculator(sentences):
    global sentencevalue
    sentencevalue = dict()
    for sentence in sentences:
        tokenized_list = nltk.word_tokenize(sentence)
        for word in tokenized_list:
            word_freq_keys = word_frequency_dictionary.keys()
            if word in word_freq_keys:
                    if sentence not in sentencevalue:
                        sentencevalue.update({sentence : word_frequency_dictionary[word]})
                    else:
                        sentencevalue[sentence] += word_frequency_dictionary[word]
    return sentencevalue

# Updates the dictionary sentence score values based on other parameters
def sentence_value_updater(): 
    sentencevalue = sentence_freq_score_calculator(sentences)
        
    for sentence in sentencevalue:
        # for each word in topic_ask check
        if topic_ask.lower() + "is" in sentence.lower():
            sentencevalue[sentence] += 4
    
        elif sentences.index(sentence) < 2:
            sentencevalue[sentence] += 23
        elif topic_ask.lower() in sentence.lower(): 
            sentencevalue[sentence] += 3


# Creates a summary based on how many sentences the user would like it to be.            
def summary_creator():
    n = int(input("How many sentences would you like your summary to be? (Recommended 5 - 8 Lines) \n"
                  "Enter a Number \n"))
    summary = ''
    summary_sentences = heapq.nlargest(n,sentencevalue,key = sentencevalue.get)
    summary = " ".join(summary_sentences)
    summary =  re.sub(r'\[[0-9]*\]'," ", summary)
    summary = re.sub(r'\s+', ' ', summary)
    return summary
   
def main():
    global topic_ask, url
    text_or_topic = input("Do you want a text, topic or url summarized? \n"
                          "For topic, enter topic. \n For text, enter text. \n For url, enter url: \n")
    if text_or_topic == "topic":
        topic_to_text()
        tokenize()
        word_frequency_dict_creator()
        sentence_value_updater()
        summary = summary_creator()
        print(summary)
    elif text_or_topic == "text":
        global article,topic_ask,formatted_text
        topic_ask = input("Enter the title of the text you want summarized (Or give the text a title): \n")
        article = input("Enter the text here: \n")
        formatted_text = re.sub('[^a-zA-Z.]', " ", article)
        formatted_text = re.sub(r'\s+', " ", formatted_text)
        tokenize()
        word_frequency_dict_creator()
        sentence_value_updater()
        summary = summary_creator()
        print(summary)
    else:
        url = input("Enter url here: \n")
        topic_ask = input("Enter the topic here: \n")
        scrape_page()
        tokenize()
        word_frequency_dict_creator()
        sentence_value_updater()
        summary = summary_creator()
        print(summary)
main()