import pandas as pd
from texthero import preprocessing
import texthero as hero
import string
import contractions
import spacy
import nltk

nltk.download('stopwords')
nlp=spacy.load("/opt/miniconda/lib/python3.8/site-packages/pt_core_news_sm/pt_core_news_sm-2.3.0")

# TODO Divide the Preprocessing from DataProcessing, It is important to preprocess text regardless of Data Preparation.
class PreProcessing():
    def __init__(self, data: pd.DataFrame, text_col:str="text", languages:list=['portuguese', 'english'], lowercase: bool=True, 
                    whitespace: bool=True, diacritics: bool=True, 
                    brackets: bool=True, digits: bool=True, 
                    punctuation: bool=True, contraction: bool=True, 
                    user_stop_words:bool=True, lemmatizer:bool = True):
        if not isinstance(data, pd.DataFrame):
            raise Exception(f"This class handle only pandas dataFrame!")
     
        self.text_col = text_col
        self.text_processed_col = text_col + "_processed"
        self.data = data
        self.punctuation = punctuation
        self.contraction = contraction
        self.lemmatizer = lemmatizer
        self.languages = languages
        self.user_stop_words = user_stop_words
        self.user_selections = [lowercase, whitespace, diacritics, brackets, digits]
        self.current_selection_actions = [preprocessing.lowercase,
                       preprocessing.remove_whitespace,
                       preprocessing.remove_diacritics,
                       preprocessing.remove_brackets, # This will also remove text inside the brackets
                       preprocessing.remove_digits
                       ]
        self.stop_words = set()
        self.class_stop_words = self.stopword_removal()
            
    def remove_punctuation(self):
         # Keep ! as it gives strong positive or negative sentiment
         
        remove = string.punctuation
        # remove = remove.replace("!", "") # don't remove ! and '
        self.pattern = r"[{}]".format(remove) # create the pattern
        self.data[self.text_processed_col]=self.data[self.text_col].str.replace(self.pattern, '')
    
    def remove_contractions(self):
        # Change the contractions like don't becomes do not aren't becomes are not
        self.data[self.text_processed_col]=self.data[self.text_processed_col].apply(lambda x:contractions.fix(x))
        self.data[self.text_processed_col]=preprocessing.remove_whitespace(self.data[self.text_processed_col])    
    def user_selections_cleaning(self):
        # Get the user selections from given selection
        self.user_selection_actions = [self.current_selection_actions[i] for i, selection in enumerate(self.user_selections) if selection]
        # clean the data
        self.data[self.text_processed_col] = self.data[self.text_processed_col].pipe(hero.clean, self.user_selection_actions)
    
    def stopword_removal(self):
        """_Separating the negative words from Stopwords to keep negative sentiment
        """

        # Keep all negative words in the NLTK list
        temp_direct = []
        for lan in self.languages:
            temp = pd.Series((nltk.corpus.stopwords.words(lan)))
            self.stop_words = self.stop_words.union(set(nltk.corpus.stopwords.words(lan)))
            self.stop_words = self.stop_words.union(set(preprocessing.remove_diacritics(temp).values))
        self.stop_words = self.stop_words.union()    
        # TODO Evaluate the importance of this step
        exclude_words = set(('don', "don't","aren't","couldn", "couldn't", "didn", 
                             "didn't", "doesn", "doesn't", "hadn", "hadn't", "hasn", 
                             "hasn't", "haven", "haven't", "isn", "isn't", "ma", "mightn", 
                             "mightn't", "mustn", "mustn't", "needn", "needn't", "shan", "shan't", 
                             "shouldn", "shouldn't", "wasn", "wasn't", "weren", 
                             "weren't", "won", "won't", "wouldn", "wouldn't","not"))
        self.class_stop_words = self.stop_words.difference(exclude_words)
        
    def clean_stop_words(self):
        self.data[self.text_processed_col] = self.data[self.text_processed_col].apply(lambda x: ' '.join([word for word in x.split() if word not in (self.stop_words)]))
        # self.data[self.text_processed_col] = self.data[self.text_processed_col].apply(lambda x: ' '.join([word for word in x.split() if word not in (self.class_stop_words)]))     
        
    def apply_lemmatizer(self):
        self.data[self.text_processed_col]=self.data[self.text_processed_col].apply(lambda x:PreProcessing.get_lemmatizer(x)) 
            
    def clean_text(self):
        """_Function to preprocess 'comment' attribute of a dataframe_
        Args:
            self.data (_DataFrame_): _Raw  DataFrame received form customer_
        Returns:
            _DataFrame_: _ Return a comments without punctuations_
        """
        # Remove punctuation
        if self.punctuation:
            self.remove_punctuation()
        # Clean according to user selected options
        self.user_selections_cleaning()
        # Clean the contractions I'm to I am 
        if self.contraction:
            self.remove_contractions()
        # remove stop words, list of word in the self.stop_words are removed
        if self.user_stop_words:
            self.clean_stop_words()    
        if self.lemmatizer:
            self.apply_lemmatizer()    
        # TODO Feel repetition 
        self.data = self.data.reset_index(drop=True)
    
      # Lemmatization on both positive and negative sentiments
    @staticmethod
    def get_lemmatizer(text):
        """_Function to perform Lemmatization_
        Args:
            x (_string_): _clean_custom_content string_
        Returns:
            _string_: _clean_custom_content string_
        """
        text=str(text)
        text_list=[]
        doc=nlp(text)
        
        for token in doc:
            lemma=token.lemma_
            text_list.append(lemma)
        return ' '.join(text_list)     
          
