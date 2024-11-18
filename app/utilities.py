import requests

def obtener_datos_pelicula(title, year, apiKey):
    base_url = "https://api.themoviedb.org/3"
    search_url = f"{base_url}/search/movie?query={title}&primary_release_year={year}"

    auth = f"Bearer {apiKey}"
    headers = {
        "accept": "application/json",
        "Authorization": auth
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
        
    search_url = f"{base_url}/search/movie?query={title}"
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