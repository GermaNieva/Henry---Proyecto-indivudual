# Henry---Proyecto-indivudual

Descripción del Proyecto
En este proyecto, asumí el rol de un MLOps Engineer para desarrollar un sistema de recomendación de películas desde cero. El trabajo incluyó desde la ingeniería de datos hasta el despliegue del modelo y la API.

# Transformaciones de Datos
Realicé varias transformaciones esenciales para preparar los datos:

Desanidado de datos: Extraje y normalicé campos anidados como belongs_to_collection y production_companies.
Relleno de valores nulos: Rellené los valores nulos en revenue y budget con 0.
Eliminación de valores nulos: Eliminé filas con valores nulos en release_date.
Formateo de fechas: Convertí las fechas al formato AAAA-mm-dd y creé la columna release_year.
Cálculo de retorno: Creé la columna return dividiendo revenue por budget, asignando 0 cuando los datos no estaban disponibles.
Eliminación de columnas innecesarias: Eliminé columnas no utilizadas como video, imdb_id, adult, original_title, poster_path y homepage.
Todos estos procesos los documenté y ejecuté en los notebooks dentro de la carpeta notebooks/.

# Desarrollo de la API

Implementé una API usando FastAPI con los siguientes endpoints:
cantidad_filmaciones_mes(Mes): Devuelve la cantidad de películas estrenadas en un mes.
cantidad_filmaciones_dia(Dia): Devuelve la cantidad de películas estrenadas en un día.
score_titulo(titulo_de_la_filmación): Devuelve el título, año de estreno y score de una filmación.
votos_titulo(titulo_de_la_filmación): Devuelve el título, cantidad de votos y promedio de votaciones de una filmación.
get_actor(nombre_actor): Devuelve el éxito del actor medido a través del retorno, cantidad de películas y promedio de retorno.
get_director(nombre_director): Devuelve el éxito del director, nombre de cada película, fecha de lanzamiento, retorno individual, costo y ganancia.
La API también incluye el endpoint recomendacion(titulo), que recomienda películas similares basadas en la puntuación.

# Deployment
Deployé la API en Render. Aunque enfrenté algunos desafíos debido a la limitada memoria y poder de procesamiento, finalmente logré deployar con éxito.

Análisis Exploratorio de Datos (EDA)
Llevé a cabo un análisis exploratorio de los datos para entender las relaciones entre las variables, identificar outliers y patrones interesantes. Utilicé visualizaciones y una nube de palabras para analizar los títulos de las películas.

# Estructura del Proyecto
notebooks/: Archivos de ETL y EDA (data_analysis).
APP: Archivo principal de la API (Main.py) con los endpoints y la función del modelo de recomendación.
DATASETS/: Archivo de datos transformado y convertido a formato Parquet para mejorar el tamaño y procesamiento.
# Conclusiones
Este proyecto me permitió aplicar conocimientos de ingeniería de datos, machine learning y despliegue de modelos. La experiencia adquirida ha sido invaluable para entender el ciclo de vida completo de un proyecto de Machine Learning y las herramientas necesarias para su implementación y mantenimiento.