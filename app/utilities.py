import requests

def obtener_datos_pelicula(title, year):
    base_url = "https://api.themoviedb.org/3"
    search_url = f"{base_url}/search/movie?query={title}&primary_release_year={year}"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhMTJhZjZhMjRlYjhiYTEzMTg2YjIyY2MzYmU3NDM1OCIsIm5iZiI6MTczMDU1NjcyMy4zNDU2MTQ3LCJzdWIiOiI2NzI2MzBkMWU3MjU4NDhhMTkzYWJjNTYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.WnA94wxrpQ-ixwG3hQ_7lId3GfZq_pJbZvnRsy5gmQQ"
    }

    response = requests.get(search_url, headers=headers)


    data = response.json()
    
    if data['results']:
        pelicula = data['results'][0]
        poster_path = pelicula.get('backdrop_path')
        description = pelicula.get('overview')
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return poster_url, description
    return None, "This movie has not an available description."