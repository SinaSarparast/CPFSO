from sklearn.feature_extraction.text import CountVectorizer

def get_word_bag_vector(list_of_string, stop_words=None, max_features=None):
    """
    returns a vectorizer object

    To get vocabulary list: vectorizer.get_feature_names()
    
    To get vocabulary dict: vectorizer.vocabulary_
    
    To convert a list of strings to list of vectors: vectorizer.transform().todense()
    
    
    Example:
    
    word_bag = bow.get_word_bag_vector([
    'All my cats in a row',
    'When my cat sits down, she looks like a Furby toy!',
    'The cat from outer space'
    ], stop_words='english')
    
    word_bag_vec.get_feature_names()
    
    > ['cat', 'cats', 'furby', 'like', 'looks', 'outer', 'row', 'sits', 'space', 'toy']

    word_bag_vec.transform([
    'All my cats in a row'
    ]).todense()

    > [[0 1 0 0 0 0 1 0 0 0]]
    
    
    For full documentation on word vectorizer,
    http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
    """
    vectorizer = CountVectorizer(stop_words=stop_words, max_features=max_features)
    vectorizer.fit(list_of_string)
    return vectorizer
