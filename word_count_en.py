import re
from collections import Counter
import nltk
doc_en = open("news.txt", 'r')
total = []

while True:
    line = doc_en.readline()
    texts = nltk.word_tokenize(line)
    if not line:
        break
    total += texts

nonPunct = re.compile('.*[A-Za-z0-9].*')
filtered = [w for w in total if nonPunct.match(w)]
counts = Counter(filtered)
print(counts)

doc_en.close()