# version: 0.0.1
# data: 2021.04.26
# author: Roy Kid
# contact: lijichen365@126.com

from paperSpider.npl import NPL
from paperSpider.parser import PdfParser

# debug lib



class Backend:

    def __init__(self) -> None:
        self.refPaths = []
        self.refPDFParsers = []
        self.npl = NPL()

    def update_refs(self, refPaths):

        #! TODO: incremental update
        for refPath in refPaths:
            if refPath not in self.refPaths:
                self.refPaths.append(refPath)
                pdfperser = PdfParser(refPath)

                # ---npl process section---
                # e.g. exclude verbose

                # ---npl process end---
                self.refPDFParsers.append(pdfperser)

    def drawWordCloud(self):
        words = []
        for parser in self.refPDFParsers:
            words.extend(parser.extract_words())
        from collections import Counter

        import wordcloud

        word_counts = Counter(words)
        
        with open('word_counts', 'w', encoding='utf-8') as f:
            f.write(str(word_counts))
        
        wordCloudDraw = wordcloud.WordCloud()
        wordCloudDraw.generate_from_frequencies(word_counts)
        return wordCloudDraw  # "WordFreQ.png")
