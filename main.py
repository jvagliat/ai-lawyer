import requests

def fetch_data(api_url):
    """
    Esto realiza realiza una solicitud GET a la API y procesa la respuesta con paginación.
    :param api_url: URL base de la API.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://jurisprudencia.sedetc.gob.pe/"
    }

    page = 1
    while True:
        try:
            response = requests.get(f"{api_url}?page={page}", headers=headers)

            if response.status_code == 200:
                data = response.json()

               
                if not data['error']:
                    print(f"Página {page} - {data['message']}")

                    if 'data' in data and isinstance(data['data'], list):
                        print("Datos obtenidos:")
                        for item in data['data']:
                            source = item.get('_source', {})
                            print(f"ID Sentencia: {source.get('id', 'N/A')}")
                            print(f"Número de Sentencia: {source.get('numero_sentencia', 'N/A')}")
                            print(f"Fecha de Publicación: {source.get('fecha_publicacion', 'N/A')}")
                            print(f"Nombre Demandante: {source.get('nombre_demandante', 'N/A')}")
                            print(f"Nombre Demandado: {source.get('nombre_demandado', 'N/A')}")
                            print(f"Número de Expediente: {source.get('numero_expediente', 'N/A')}")
                            print("Fundamentos:")
                            for fundamento in source.get('fundamentos', []):
                                print(f"  - {fundamento}")
                            print(f"Enlace al archivo PDF: {source.get('url_archivo', 'N/A')}")
                            print("-")
                    else:
                        print("No se encontraron datos en 'data'.")

                   
                    pagination = data.get('pagination', {})
                    if page >= pagination.get('num_pages', page):
                        print("Se han obtenido todas las páginas.")
                        break
                else:
                    print(f"Error en la API: {data['message']}")
                    break
            else:
                print(f"Error en la solicitud: {response.status_code}")
                print(response.text)  
                break

            page += 1

        except Exception as e:
            print(f"Ocurrió un error: {e}")
            break

if __name__ == "__main__":
    
    api_url = "https://jurisbackend.sedetc.gob.pe/api/visitor/sentencia/busqueda"
    fetch_data(api_url)
