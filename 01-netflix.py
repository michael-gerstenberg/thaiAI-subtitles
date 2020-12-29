from datetime import datetime
from mongo_db import connect_mongo_db
from tqdm import tqdm
from pprint import pprint
from bs4 import BeautifulSoup
import bs4
import json
import re
import requests
import time
import random
import os
import tltk
import sklearn

db = connect_mongo_db()

def main():

    path = 'sources/netflix/Rick.and.Morty'
    for filename in tqdm(os.listdir(path)):
        if db.word_count.count_documents({'filename': filename}) < 1:
            # if filename.find('.th.vtt') > 0 or filename.find('.th[cc].vtt') > 0:
            #     episode = build_description(filename)
            #     episode['word_count'] = scrape_vtt_th(path, filename)
            #     episode['different_words'] = len(episode['word_count'])
            #     db.word_count.insert_one(episode)
            #     return True
            
            if filename.find('.de.dfxp') > 0:
                episode = build_description(filename)
                episode['word_count'] = scrape_dfxp_de(path, filename)
                #print(scrape_dfxp_de)
                print(normalize_german_verbs(episode['word_count']))
                episode['different_words'] = len(episode['word_count'])
                #db.word_count.insert_one(episode)
                return True
            
        #else:
            #print(filename)

def build_description(filename):
    details = {
        'filename': filename,
        'source': 'netflix',
        'date': datetime.now(),
        'words_to_ignore': {
            'characters': {},
        },
        'word_count': {},
        'different_words': 0,
    }
    return dict(details, **extract_season_and_episode(filename))

def extract_season_and_episode(filename):
    parts = filename.split('.')
    for part in parts:
        if len(part) == 6 and part[0] == "S":
            return {
                'season': int(part[1:3]),
                'episode': int(part[4:6]),
            }

def scrape_vtt_th(path, filename):
    word_count = {}
    with open(path + '/' + filename) as file_in:
        #print(filename)
        for line in tqdm(file_in):
            if line.count('<c.thai>') > 0:
                thai_string = line.replace('&lrm;', '').replace('<c.thai><c.bg_transparent>', '').replace('</c.bg_transparent></c.thai>', '').strip()
                thai_string = replace_nonchar(thai_string)
                thai_sentences = thai_string.split()
                for thai_sentence in thai_sentences:
                    thai_sentence_words_separated = tltk.nlp.word_segment(thai_sentence)
                    thai_words = thai_sentence_words_separated.split('|')
                    del thai_words[-1]
                    for thai_word in thai_words:
                        if thai_word in word_count.keys():
                            word_count[thai_word] += 1
                        else:
                            word_count[thai_word] = 1
        return dict(sorted(word_count.items(), key=lambda item: item[1],reverse=True))

def scrape_dfxp_de(path, filename):
    print(filename)
    word_count = {}
    f = open(path + '/' + filename, "r")
    soup = BeautifulSoup(f.read(), 'html.parser')
    f.close()
    for p in soup.find_all('p'):
        for line in p.contents:
            if str(line) != '<br/>':
                sentence = ''
                if type(line) == bs4.element.NavigableString:
                    sentence = replace_nonchar(str(line))
                if type(line) == bs4.element.Tag:
                    for s in line.find_all('s'):
                        sentence = replace_nonchar(str(s[0]))
                
                sentence = sentence.split(' ')
                for word in sentence:
                    if word in word_count.keys():
                        word_count[word] += 1
                    else:
                        word_count[word] = 1

    return dict(sorted(word_count.items(), key=lambda item: item[1],reverse=True))

def normalize_german_verbs(words):
    verbs = {}
    for word in words:
        word = word.lower()
        result = db.verbs.find({'keywords': word})
        for r in result:
            if r['word'] in verbs.keys():
                verbs[r['word']] += 1
            else:
                verbs[r['word']] = 1
    print(len(verbs))
    return dict(sorted(verbs.items(), key=lambda item: item[1],reverse=True))

def replace_nonchar(string):
    string = string.replace('-  ', '').replace('- ', '').replace('...', '').replace('?', '').replace('!', '').replace('-', '')
    string = re.sub("[\(\[].*?[\)\]]", "", string)
    string = string.replace('"', '').replace('.', '').replace('ฯ', '').replace('[', '').replace(']', '').replace("'", '').replace(',', '')
    pattern = r'[0-9]'
    string = re.sub(pattern, '', string)
    return string.strip()

if __name__ == "__main__":
    main()