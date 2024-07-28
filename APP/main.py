from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import os

app = FastAPI()

# Ruta relativa al archivo Parquet
relative_path = os.path.join(os.path.dirname(__file__), '../DATASET/movies_credits_merged.parquet')

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

# Ejecutar el servidor de FastAPI
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
