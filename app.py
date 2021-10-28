# Biblioteca que nós instalamos manualmente
from bs4 import BeautifulSoup

# Bibliotecas nativas do Python
import json
import bs4
import requests
import re

# Função de formatação usando módulo de regex
def regex_format(text):
    text = re.sub(r'[\n\$]', '', text)
    text = re.sub(r'[\ ]{2}', '', text)
    return text

# URL do site
url = 'https://storage.googleapis.com/infosimples-public/commercia/case/product.html'

# Objeto contendo a resposta final
resposta_final = {}

# Faz o request
response = requests.get(url)

# Parse do responses
parsed_html = BeautifulSoup(response.content, 'html.parser')



# Vamos pegar o título do produto, na tag H2, com ID "product_title"
resposta_final['title'] = parsed_html.select_one('h2#product_title').get_text()

# Vamos pegar o nome da marca do produto
resposta_final['brand'] = parsed_html.select_one('div.brand').get_text()

# Vamos pegar as categorias do produto
resposta_final['categories'] = [category.get_text() for category in parsed_html.find('nav', attrs={'class' : 'current-category'}).find_all(href=True)]

# Vamos pegar o texto que descreve o produto
resposta_final['description'] = regex_format(parsed_html.find('div', attrs={'class' : 'product-details'}).select_one('p').get_text())

# Vamos formar uma lista de objetos com detalhes de cada uma das variações do produto
array_skus = [] # Lista de objetos skus
product_skus = parsed_html.find_all('div', attrs={'class' : 'card-container'}) # Lista com variações de cada produto
for each in product_skus:
    object_skus = {} # Novo objeto skus
    object_skus['name'] = regex_format(each.select_one('div.sku-name').get_text())
    if each.select_one('div.sku-current-price') != None:
        object_skus['current_price'] = float(regex_format(each.select_one('div.sku-current-price').get_text()))
    else:
        object_skus['current_price'] = None
    if each.select_one('div.sku-old-price') != None:
        object_skus['old_price'] = float(regex_format(each.select_one('div.sku-old-price').get_text()))
    else:
        object_skus['old_price'] = None
    if each.select_one('i') != None:
        object_skus['available'] = False
    else:
        object_skus['available'] = True
    array_skus.append(object_skus) # Adicionando objeto dentro da lista
resposta_final['skus'] = array_skus

# Vamos formar uma lista de objetos com as propriedades do produto
array_properties = [] # Lista de objetos properties
product_properties = [row.find_all('td') for row in parsed_html.select_one('table.pure-table.pure-table-bordered').find_all('tr')] # Lista de propriedades do produto
addtitional_product_properties = [row.find_all('td') for row in parsed_html.select_one('div#additional-properties').find_all('tr')] # Lista de propriedades adicionais do produto
all_product_properties = product_properties + [ele for ele in addtitional_product_properties if ele != []] # Unir duas listas e tratar o elemento vazio da segunda
for each in all_product_properties:
    object_properties = {} # Novo objeto properties
    object_properties['label'] = regex_format(each[0].get_text())
    object_properties['value'] = regex_format(each[1].get_text())
    array_properties.append(object_properties) # Adicionando objeto dentro da lista
resposta_final['properties'] = array_properties

# Vamos formar uma lista de objetos com as avaliações do produto
array_reviews = [] # Lista de objetos reviews
product_reviews = parsed_html.find_all('div', attrs={'class' : 'review-box'}) # Lista com as caixas de avaliações
for each in product_reviews:
    object_reviews = {} # Novo objeto reviews
    object_reviews['name'] = regex_format(each.select_one('span.review-username').get_text())
    object_reviews['date'] = regex_format(each.select_one('span.review-date').get_text())
    c = 0
    for star in regex_format(each.select_one('span.review-stars').get_text()): # Loop para contar as estrelas preenchidas da pontuação
        if star == '★': c+=1
        else: break
    object_reviews['score'] = c
    object_reviews['text'] = regex_format(each.select_one('p').get_text())
    array_reviews.append(object_reviews) # Adicionando objeto dentro da lista
resposta_final['reviews'] = array_reviews

# Vamos obter a média das avaliações do produto
review_sum_score = 0
for review in array_reviews:
    review_sum_score += review['score'] # Somando avaliações
resposta_final['reviews_average_score'] = review_sum_score/len(array_reviews) # Média das avaliações

# Vamos obter a URL da página do produto
resposta_final['url'] = url



# Gera string JSON com a resposta final
json_resposta_final = json.dumps(resposta_final, ensure_ascii=False, indent=4)

# Salva o arquivo JSON com a resposta final
with open('produto.json', 'w', encoding='utf8') as arquivo_json:
    arquivo_json.write(json_resposta_final)