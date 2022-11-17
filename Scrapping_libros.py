import requests
import bs4
from bs4 import BeautifulSoup    
from urllib.parse import urljoin
import pandas as pd
from IPython.display import Image

#Traer el url
url_inicial = 'https://books.toscrape.com/index.html'
#Hacer el request
r= requests.get(url_inicial)

#Ahora vamos a generar texto plano en html de la respuesta(requests) que hemos recibido, para eso usamos BeautifulSoup, y 
s= BeautifulSoup(r.text, 'lxml')


#CREAR FUNCION QUE HAGA TODO!
def traer_url_links(sopa, url):
    url_root= 'https://books.toscrape.com/'
    #vamos a buscar primeramente los links de cada uno de los libros
    lista_articulos = s.find_all('article', class_="product_pod" )  
    #buscar especificamente dentro del contenedor lo que queremos
    links_libros= []
    for x in lista_articulos:
        links_libros.append(x.find('h3').find('a').get('href'))
    #vamos a parsear los links porque sus url estan incompletas, y las concatenamos a la variable url_root
    links_completos =[]
    for i in links_libros:
        links_completos.append(urljoin(url_root,i))
    #retornar la variable con los links
    return links_completos


urlI = 'https://books.toscrape.com/index.html'
links_items=[]
contador = 0
while contador <2:
    print(f"Estoy en la pagina{urlI}")
    r_pagina= requests.get(urlI)
    sopa_pag= BeautifulSoup(r_pagina.text, 'lxml')
    links= traer_url_links(sopa_pag, urlI)
    #Pasar a la siguiente pagina
    next_page = sopa_pag.select('li.next > a')
    #verificar si hay mas paginas o no
    if not next_page:
        break
    #concatenar la siguiente pagina y actualizar el url 
    urlI = urljoin(urlI,next_page[0].get('href'))
    
    links_items.append(links)
    contador+=1
    
#UNIR TODOS LOS LINKS EN UNA VARIABLE, YA QUE ESTAN ALMACENADOS COMO 50 LISTAS DENTRO DE UNA
links_limpios= []
for i in links_items:
    for j in i:
        links_limpios.append(j)

print(links_limpios) 
print(len(links_limpios))






#FUNCION PARA INICIAR EL SCRAPER DE CADA LIBRO
def scraper_libro(linkk):
    content_book ={}
    r = requests.get(linkk)
    s = BeautifulSoup(r.text, 'lxml')
     #titulo del libro
    titulo=s.find('h1').get_text(strip=True)
    if titulo:
        content_book['Titulo']=titulo
    else :
        content_book['Titulo']=None    
    #obtener ptrecio
    precio=s.find('p', class_='price_color').get_text(strip=True)
    if precio:
        content_book['Precio']=precio
    else :
        content_book['Precio']=None 
    #obtener la descripcion de producto
    ancla_desc=s.find('div', id='product_description')
    if ancla_desc:
        content_book['Descripcion']=ancla_desc.find_next_sibling('p').get_text(strip=True)
    else :
        content_book['Descripcion']=None  
    #obtener imagen
    src_img=s.find('div', class_='item active').find('img').get('src')
    if src_img:
        content_book['Url_img']=urljoin(url_inicial, src_img)
    else :
        content_book['Url_img']=None
    '''Para visualizar la imagen
    Image(requests.get(imagen).content)
    '''
    return content_book

#SCRAP COMPLETO
datos_libros= []
for i in links_limpios:
    print(f'Estamos scrapeando la pag {i}')
    datos_libros.append(scraper_libro(i))
    
    
#CONVERTIR EN DATAFRAME
df_catalogo = pd.DataFrame(datos_libros) 

#AGREGAR UNA COLUMNA TRANSFORMANDO EL LINK DE LA IMAGEN EN ETIQUETA HTML Y VISUALIZANDOLA EN EL DF
from IPython.core.display import HTML

def path_html_img(url):
    return '<img src="'+url+'"width="60">'
df_catalogo['Vis_img']=df_catalogo['Url_img'].apply(lambda x : path_html_img(x))

#EXPORTAR EL DF A CSV
df_catalogo.to_csv('DataFrameScrapingCatalogoLibro.csv', encoding='utf-8')


