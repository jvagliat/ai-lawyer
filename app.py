import sqlite3
import requests
from flask import Flask, render_template

app = Flask(__name__)


DB_NAME = "data.db"

def init_db():
    """
    Esto hace que inicializa la base de datos creando la tabla si no existe.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentencias (
            id INTEGER PRIMARY KEY,
            numero_sentencia TEXT,
            fecha_publicacion TEXT,
            nombre_demandante TEXT,
            nombre_demandado TEXT,
            numero_expediente TEXT,
            fundamentos TEXT,
            url_archivo TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(data):
    """
    esto guarda las sentencias en la base de datos.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for item in data:
        cursor.execute('''
            INSERT OR REPLACE INTO sentencias (
                id, numero_sentencia, fecha_publicacion, nombre_demandante,
                nombre_demandado, numero_expediente, fundamentos, url_archivo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['id'], item['numero_sentencia'], item['fecha_publicacion'],
            item['nombre_demandante'], item['nombre_demandado'],
            item['numero_expediente'], '\n'.join(item['fundamentos']),
            item['url_archivo']
        ))
    conn.commit()
    conn.close()

def fetch_data(api_url):
    """
    esto realiza una solicitud GET a la API y devuelve los datos procesados.
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://jurisprudencia.sedetc.gob.pe/"
    }
    all_data = []
    page = 1

    while True:
        response = requests.get(f"{api_url}?page={page}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data['error'] and 'data' in data:
                for item in data['data']:
                    source = item.get('_source', {})
                    all_data.append({
                        'id': source.get('id'),
                        'numero_sentencia': source.get('numero_sentencia', 'N/A'),
                        'fecha_publicacion': source.get('fecha_publicacion', 'N/A'),
                        'nombre_demandante': source.get('nombre_demandante', 'N/A'),
                        'nombre_demandado': source.get('nombre_demandado', 'N/A'),
                        'numero_expediente': source.get('numero_expediente', 'N/A'),
                        'fundamentos': source.get('fundamentos', []),
                        'url_archivo': source.get('url_archivo', 'N/A'),
                    })
                
                if page >= data['pagination']['num_pages']:
                    break
            else:
                break
        else:
            break
        page += 1

    return all_data

@app.route("/")
def index():
    """
    este es la ruta principal que muestra las sentencias almacenadas en la base de datos.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sentencias")
    rows = cursor.fetchall()
    conn.close()

    sentencias = [
        {
            "id": row[0],
            "numero_sentencia": row[1],
            "fecha_publicacion": row[2],
            "nombre_demandante": row[3],
            "nombre_demandado": row[4],
            "numero_expediente": row[5],
            "fundamentos": row[6].split('\n'),
            "url_archivo": row[7]
        }
        for row in rows
    ]

    return render_template("index.html", sentencias=sentencias)

if __name__ == "__main__":
    init_db()
    api_url = "https://jurisbackend.sedetc.gob.pe/api/visitor/sentencia/busqueda"
    data = fetch_data(api_url)
    save_to_db(data)
    app.run(debug=True)
