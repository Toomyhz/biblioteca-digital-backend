import re , unicodedata

def generar_slug(texto):
    if not texto:
        return None
    #Normalizar para quitar tildes, acentos y caracteres especiales
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    #Convertir en minúsculas
    texto = texto.lower()
    # Reemplazar espacios y caracteres especiales por guiones
    texto = re.sub(r'[^a-z0-9]+', '-', texto).strip('-')
    return texto