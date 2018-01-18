import csv
import re
from collections import Counter
import nltk


while True:

    date = input('type in target date : ')

    with open(date + ".csv", 'r') as doc_en:
        pencil = csv.reader(doc_en)
        total = []

        for row in pencil:
            if not row:
                continue
            texts = nltk.word_tokenize(row[0])

            total += texts

    nonPunct = re.compile('.*[A-Za-z0-9].*')
    filtered = [w for w in total if nonPunct.match(w)]
    counts = Counter(filtered)

    # with open ("wordcount_" + date + ".csv", "w", encoding = "utf-8") as wordcount_file:
    # 	pencil = csv.writer(wordcount_file)
    # 	pencil.writerow([counts])
    print(counts)

    doc_en.close()

