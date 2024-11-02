import requests
import random

# Definición de la URL de la API de Wikidata
url = "https://query.wikidata.org/sparql"

# Función para realizar la consulta
def query_wikidata(event_year, event_month, event_day):
    query = f"""
    SELECT ?label ?description WHERE {{
      ?event wdt:P31/wdt:P279* wd:Q1190554 .
      ?event wdt:P585 "{event_year}-{event_month}-{event_day}T00:00:00Z"^^xsd:dateTime .
      ?event rdfs:label ?label .
      ?event schema:description ?description .
      FILTER(lang(?label) = 'es' && lang(?description) = 'es')
      
      ?article_en schema:about ?event ; schema:isPartOf <https://es.wikipedia.org/> .
    }} 
    LIMIT 10
    """
    
    headers = {"User-Agent": "MyApp/1.0 (https://myapp.com/contact)"}
    response = requests.get(url, params={'query': query, 'format': 'json'}, headers=headers)

    if response.ok:
        return response.json()['results']['bindings']
    else:
        print("Error:", response.status_code)
        return []

def find_event(month, day):
  # Inicialización de la fecha y búsqueda de eventos
  initial_date = random.randint(1000, 2023)
  results = query_wikidata(initial_date, month, day)

  # Si no se encuentran resultados, probar con fechas aleatorias desde 1000
  if not results:
      print(f"No se encontraron eventos en la fecha {initial_date}. Buscando con fechas aleatorias...")
      while not results:
          random_year = random.randint(1000, 2023)  # Cambia 2023 a la fecha actual deseada
          random_date = f"{random_year}-{month}-{day}"
          print(f"Intentando con la fecha aleatoria: {random_date}")
          results = query_wikidata(random_year, month, day)

  # Mostrar resultados
  for item in results:
      event_label = item['label']['value']
      description = item['description']['value']
      print(f"Event: {event_label}, Date: {random_year}, Description: {description}")


find_event(11, 8)
