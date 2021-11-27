from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

documentA = 'a qqq fox jumps fox'
documentB = 'fox adad fox re fox'
vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform([documentA,documentB])
feature_names = vectorizer.get_feature_names_out()
dense = vectors.todense()
denselist = dense.tolist()
df = pd.DataFrame(denselist, columns=feature_names)
print(df)