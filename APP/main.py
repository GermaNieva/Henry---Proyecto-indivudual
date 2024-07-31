from fastapi import FastAPI
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

app = FastAPI()

# Ruta relativa al archivo Parquet
relative_path = os.path.join(os.path.dirname(__file__), '../DATASET/merged_enriched_dataset.parquet')

# Verificar si el archivo existe
if not os.path.exists(relative_path):
    raise FileNotFoundError(f"El archivo no se encontró en la ruta: {relative_path}")

# Cargar el dataset
df = pd.read_parquet(relative_path)

# Convertir la columna de fecha a tipo datetime
df['release_date'] = pd.to_datetime(df['release_date'])

# Diccionario para traducir meses y días
meses = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

dias = {
    'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sábado': 5, 'domingo': 6
}

@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    mes_num = meses.get(mes.lower())
    if mes_num is None:
        return {"error": "Mes no válido"}
    cantidad = df[df['release_date'].dt.month == mes_num].shape[0]
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en el mes de {mes}"}

@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    dia_num = dias.get(dia.lower())
    if dia_num is None:
        return {"error": "Día no válido"}
    cantidad = df[df['release_date'].dt.dayofweek == dia_num].shape[0]
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en los días {dia}"}

@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    film = df[df['title'].str.lower() == titulo.lower()]
    if film.empty:
        return {"error": "Título no encontrado"}
    film = film.iloc[0]
    return {"mensaje": f"La película {film['title']} fue estrenada en el año {film['release_date'].year} con un score/popularidad de {film['popularity']}"}

@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo: str):
    film = df[df['title'].str.lower() == titulo.lower()]
    if film.empty:
        return {"error": "Título no encontrado"}
    film = film.iloc[0]
    if film['vote_count'] < 2000:
        return {"mensaje": "La película no cumple con la condición de tener al menos 2000 valoraciones"}
    promedio_votos = film['vote_average']
    return {"mensaje": f"La película {film['title']} fue estrenada en el año {film['release_date'].year}. La misma cuenta con un total de {film['vote_count']} valoraciones, con un promedio de {promedio_votos}"}

@app.get("/get_actor/{nombre_actor}")
def get_actor(nombre_actor: str):
    # Verificar que la columna 'actors' existe en el DataFrame
    if 'actors' not in df.columns:
        return {"error": "La columna 'actors' no se encontró en el dataset"}

    # Filtrar el dataset para las películas donde ha actuado el actor
    actor_films = df[df['actors'].str.contains(nombre_actor, case=False, na=False)]
    if actor_films.empty:
        return {"error": "Actor no encontrado"}
    
    cantidad = actor_films.shape[0]
    total_retorno = actor_films['return'].sum()
    promedio_retorno = actor_films['return'].mean()
    
    return {
        "mensaje": f"El actor {nombre_actor} ha participado de {cantidad} filmaciones, el mismo ha conseguido un retorno de {total_retorno} con un promedio de {promedio_retorno} por filmación"
    }

@app.get("/get_director/{nombre_director}")
def get_director(nombre_director: str):
    # Verificar que la columna 'directors' existe en el DataFrame
    if 'directors' not in df.columns:
        return {"error": "La columna 'directors' no se encontró en el dataset"}

    # Filtrar el dataset para las películas dirigidas por el director
    director_films = df[df['directors'].str.contains(nombre_director, case=False, na=False)]
    if director_films.empty:
        return {"error": "Director no encontrado"}
    
    films_info = director_films[['title', 'release_date', 'budget', 'revenue', 'return']]
    films_list = films_info.to_dict(orient='records')
    
    return {
        "mensaje": f"El director {nombre_director} ha dirigido las siguientes películas:",
        "películas": films_list
    }

# Seleccionar las columnas relevantes
data = df[['title', 'genre_name', 'overview', 'actors']]

# Crear una columna combinada de características
data['combined_features'] = data.apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)

# Implementación de la función de recomendación mejorada
def recomendacion(titulo):
    # Crear una matriz TF-IDF de las características combinadas
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['combined_features'])
    
    # Ajustar el modelo NearestNeighbors
    nn = NearestNeighbors(metric='cosine', algorithm='brute')
    nn.fit(tfidf_matrix)
    
    # Crear una serie para mapear los índices a los títulos de las películas
    indices = pd.Series(data.index, index=data['title']).drop_duplicates()
    
    # Verificar si el título está en el índice
    if titulo not in indices:
        return {"Error": "Título no encontrado"}
    
    # Obtener el índice de la película que coincide con el título
    idx = indices[titulo]
    
    # Encontrar las 5 películas más similares
    distances, indices = nn.kneighbors(tfidf_matrix[idx], n_neighbors=6)
    
    # Obtener los índices de las películas
    movie_indices = indices[0][1:]  # Excluyendo la misma película
    
    # Devolver los títulos y overview de las 5 películas más similares
    recommended_movies = {data['title'].iloc[i]: data['overview'].iloc[i] for i in movie_indices}
    return recommended_movies

@app.get("/recomendacion/{titulo}")
def get_recomendacion(titulo: str):
    return recomendacion(titulo)

# Ejecutar el servidor de FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
