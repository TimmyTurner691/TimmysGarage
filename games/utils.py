import requests
from django.conf import settings
from django.core.cache import cache

def get_external_game_data(game_title):
    cache_key = f'external_game_{game_title}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # Ejemplo con la API de RAWG (https://rawg.io/apidocs)
        url = f"https://api.rawg.io/api/games"
        params = {
            'key': settings.RAWG_API_KEY,
            'search': game_title,
            'page_size': 1
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['results']:
            game_data = data['results'][0]
            cache.set(cache_key, game_data, timeout=60*60*24)  # Cache por 24 horas
            return game_data
        
    except requests.RequestException as e:
        print(f"Error al consultar API externa: {e}")
    
    return None