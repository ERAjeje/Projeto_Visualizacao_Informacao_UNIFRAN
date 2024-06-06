# Caso ainda não tenha instado as bibliotecas pode utilizar os comandos abaixo
# !pip install WordCloud
# !pip install pandas
# !pip install numpy
# !pip install matplotlib
# !pip install PIL
# !pip install nltk
# !pip install prince
# !pip install squarify
# !pip install seaborn

# importar os pacotes necessários
import re
import nltk
import squarify
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

# importar o arquivo csv em um df
df = pd.read_csv('DataSets/train.csv', low_memory = False)

# Visualizando as primeiras linhas do DataFrame
print(df.head())

# eliminar as colunas com valores ausentes e utilizar somente a coluna title
titles = df.dropna(subset=['title'], axis=0)['title']

# exemplos de descrições para os imóveis no Airbnb
print(titles.iloc[100])

# lista de stopword
nltk.download('punkt')
nltk.download('stopwords')
nltk_stopwords.words('english')

stop_words = set(nltk_stopwords.words('english'))

# concatenar as palavras
titles_on_string = " ".join(s for s in titles)

# tokenizando o set
tokens = word_tokenize(titles_on_string)

# removendo stopwords no set
filtered_titles = [w for w in tokens if not w.lower() in stop_words]

# Gerando a WordCloud
wordcloud = WordCloud(stopwords=nltk_stopwords.words('english'),
                      background_color="black",
                      width=1600, height=800).generate(titles_on_string)

# Mostrar a imagem final da WordCloud
fig, ax = plt.subplots(figsize=(10,6))
ax.imshow(wordcloud, interpolation='bilinear')
ax.set_axis_off()
plt.title('Núvem de palavras extraídas dos títulos das notícias')
plt.imshow(wordcloud)

# segunda visualização

# definindo a lista de palavras que serão buscadas
words = ['New York Times', 'York Times', 'New York', 'Breitbart', 'Trump', 'Donald Trump', 'Hillary', 'Hillary Clinton', 'Clinton', 'Obama', 'Election', 'Russia', 'Putin', 'American', 'Video', 'Syria']

# filtrando o dataset para apresentar somente as colunas necessárias
titles_filtered_df = df.iloc[:, [1,4]]

# Definindo a função que encontra os termos presentes na string
def hasSubstrings(title, terms):
    matching_terms = [term for term in terms if term in title]
    return matching_terms

# Verificar se o valor é uma string antes de aplicar a função e criar uma nova coluna com os valores retornados
titles_filtered_df['words'] = titles_filtered_df['title'].apply(lambda x: hasSubstrings(x, words) if isinstance(x, str) else [])

# Definindo a função de para filtro de array vazio
def hasWords(x):
    return len(x) > 0

# Removendo do dataset as linhas que não possuem termos setados na coluna words
titles_filtered_df = titles_filtered_df[titles_filtered_df['words'].apply(lambda x: hasWords(x))]

# Visualizando as primeiras linhas do DataFrame
print(titles_filtered_df.head())

# preparando o dataset de visualização

# criando o dicionário que será usando na visualização
words_dict = []
for w in words:
    words_dict.append({ w: { 'true': 0, 'false': 0 }})

# verificando o dicionário
print(words_dict)

# percorrendo o dataframe titles_filtered_df para hidratar com a quantas notícias falsas e quantas verdadeiras
# cada termo possui associado
for index, _ in titles_filtered_df.iterrows():
    for w in titles_filtered_df['words'][index]:
        for obj in words_dict:
            if w in obj.keys():
                if titles_filtered_df['label'][index] == 1:
                    obj[w]['false'] += 1
                else:
                    obj[w]['true'] += 1
        
# verificando o resultado
print(words_dict)

# Criar uma lista de dicionários com os dados
data = []
for item in words_dict:
    word = list(item.keys())[0]
    false_value = item[word]['false']
    true_value = item[word]['true']
    data.append({'word': word, 'false': false_value, 'true': true_value})

# Criar o DataFrame a partir da lista de dicionários
word_titles_by_label = pd.DataFrame(data)

#visualizando o dataset
print(word_titles_by_label)

# Remover as 4 primeiras linhas do dataset word_titles_by_label pois se tratavam de nomes de jornais e não existia uma quantidade significativa de notícias falsas
word_titles_by_label = word_titles_by_label.iloc[4:]

# plotando o gráfico
words = word_titles_by_label['word']
false = word_titles_by_label['false']
true = word_titles_by_label['true']

# Ajustar a largura das barras
bar_width = 0.35

# Calcular a posição x para as barras de "falsa" e "verdadeira" lado a lado
x = np.arange(len(words))

plt.bar(x - bar_width/2, true, width=bar_width, color='blue', label='Verdadeira')
plt.bar(x + bar_width/2, false, width=bar_width, color='red', label='Falsa')

plt.xticks(x, words, rotation=90)
plt.legend()
plt.title('Relação entre notícias falsas e verdadeiras para cada palavra chave da nuvem de palavras')
plt.show()

# terceira visualização

# criando o dataset de notícias falsas
fake_news = df[df['label'] == 1]['text'].astype(str)

# unindo as notícias
fake_news = " ".join(fake_news)

# Definir as stopwords da língua portuguesa
stop_words = set(nltk_stopwords.words('english'))

# tokenizando o set
tokens = word_tokenize(fake_news)
chars = ['!', '\"', '#', '$', '%', '&', "\'", '(', ')', '*', '+', ',', '’', '“', "”", "''", "``", "‘‘", "‘", "'s", "—", "–", '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '\t', '\n', '\x0c', '...']

# removendo stopwords no set
fake_news_without_stopwords = [w for w in tokens if not w.lower() in stop_words and not w in chars]

# Contando a frequência de cada termo
term_counts = Counter(fake_news_without_stopwords)

# Criando um DataFrame com os termos e suas contagens
terms_df = pd.DataFrame(list(term_counts.items()), columns=['term', 'count'])

# Ordenando o DataFrame pelas contagens em ordem decrescente
terms_df = terms_df.sort_values(by='count', ascending=False).reset_index(drop=True)

# Calcular as proporções dos retângulos no treemap com base nas contagens
sizes = terms_df['count'][:30].values
label = terms_df['term'][:30].values

# Criar o gráfico treemap
plt.figure(figsize=(12, 8))
squarify.plot(sizes=sizes, label=label, alpha=0.6, color=sb.color_palette('pastel6', len(sizes)))  # Especificar cores com base nos tamanhos
plt.axis('off')  # Remover os eixos
plt.title('Gráfico Treemap mostrando a relação do número de repetição dos termos entre si')
plt.show()