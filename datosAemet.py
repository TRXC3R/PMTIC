import requests
import json
import numpy as np
import pandas as pd

# python<version> -m venv <nombre_venv>
# source <nombre_venv>/bin/activate
# pip install -r requirements.txt

def get_datos_json (url : str):
    headers={'accept':'application/json', 
             'api_key': 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJtaXJpYW0uYWxvbnNvQGFsdW1ub3MudXBtLmVzIiwianRpIjoiOGRhYzdjZmYtNDA0Yi00Y2M4LTg2N2QtZTY0MzMxYzkzMDcxIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3MzE0ODczOTYsInVzZXJJZCI6IjhkYWM3Y2ZmLTQwNGItNGNjOC04NjdkLWU2NDMzMWM5MzA3MSIsInJvbGUiOiIifQ.e5ViEjDUMiRqZig_dkywKHRc_5CnsqIvUIml8-b6_eY' } 
    
    #Hacemos una petición GET que nos devuelve información
    r = requests.get(url, headers =  headers)

    #Obtenemos el cuerpo del mensaje de respuesta y procesamos ese JSON que nos ha devuelto la petición.
    if (r.status_code == 200):
        cuerpo = json.loads (r.text)  
    else:
        cuerpo = None
    #Devolvemos si ha habido algún error o no  y el JSON procesado
    return r.status_code, cuerpo

def getAEMETTable(*,url=None, file_name=None) -> pd.DataFrame | None: #El * indica que es necesario que si se pasa algún argumento tiene que tener nombre
    tabla_resultado=None
    if any((url is None and not file_name is None, not url is None and file_name is None)):
        if not url is None:
            status_code, primeros_datos=get_datos_json(url)
            if status_code==200:
                status_code, datos=get_datos_json(primeros_datos['datos'])
                if status_code == 200:
                    return pd.DataFrame(datos)
        if not file_name is None:
            return pd.read_csv(file_name)
    return tabla_resultado    

def main():
    tabla_pandas=getAEMETTable(file_name='todas-observaciones.csv')
    if not tabla_pandas is None:
        print(f'Los datos tienen {len(tabla_pandas)} tuplas')
        print(f'Los datos tienen {len(tabla_pandas["idema"].drop_duplicates())} estaciones')
        tabla_resultado=tabla_pandas.query('prec >0')[['idema','ubi']].drop_duplicates()
        print(tabla_resultado)
        print(f'La tabla resultados tiene {len(tabla_resultado)} tuplas.')
        # d = dtale.show(tabla_pandas, host='localhost', open_browser=True)
        # input('Pulsa para continuar')
        
        #que estaciones que registran nieve en algún momento
        tabla_resultado=tabla_pandas.query('nieve > 0')[['idema','ubi']].drop_duplicates()
        print(tabla_resultado)
        print(f'La tabla resultados tiene {len(tabla_resultado)} tuplas.')
        
        #que estaciones que no registran nieve en ningún momento
        idemas_con_nieve=set(tabla_resultado['idema'].to_list())
        todos_los_idemas=set(tabla_pandas['idema'].drop_duplicates().to_list())
        idemas_sin_nieve=pd.DataFrame(todos_los_idemas.difference(idemas_con_nieve))
        print(idemas_sin_nieve)
        print(f'La tabla resultados tiene {len(idemas_sin_nieve)} tuplas.')
        
        #que estaciones que registran nieve en algún momento con estaciones por debajo de los 1500m
        altura_maxima=1500
        tabla_resultado=tabla_pandas.query('`nieve` > 0 and `alt` < @altura_maxima')[['idema','ubi', 'alt']].drop_duplicates()
        print(tabla_resultado)
        print(f'La tabla resultados tiene {len(tabla_resultado)} tuplas.')
        
        #que estaciones que registran nieve en algún momento
        tabla_provincias=getAEMETTable(file_name='datos-idema-provincia.csv')
        tabla_resultado=tabla_pandas.query('`nieve` > 0 ')[['idema','ubi']].drop_duplicates()
        tabla_idema_provincia=tabla_resultado.merge(tabla_provincias, on='idema')
        tabla_final=tabla_idema_provincia['provincia'].drop_duplicates()
        print(tabla_final)
        print(f'La tabla resultados tiene {len(tabla_final)} tuplas.')
        
        #Pasar a csv:
        tabla_resultado.to_csv('estaciones_con_nieve.csv', index=False)
        
        #valor medio del espesor de la nieve en las estaciones que registran nieve. Consejo: mirad una tabla con una columna métodos para contabilizar
        #Estación a mayor y a menor altura donde se ha registrado nieve.
        
def old_main ():
    url = 'https://opendata.aemet.es/opendata/api/observacion/convencional/todas'
    status_code, primeros_datos =  get_datos_json (url)

    if (status_code == 200):    #Hemos hecho una petición y si no hay ningún error
        status_code, datos = get_datos_json (primeros_datos['datos'])

        if (status_code == 200):    #Hemos hecho una petición y si no hay ningún error
            print ('\n\n'+ str (type (datos)) +'\n\n')
            #print (datos)
            tabla_pandas = pd.DataFrame (datos)
            print (tabla_pandas)
            #url_tabla = dtale.show (tabla_pandas, host='localhost') #Devuelve una URL donde ver mejor los datos
            #print (url_tabla)

            #Para filtrar por condiciones:
            tabla_nieve = tabla_pandas.query ('nieve > 0')
            #Para obtener la tabla con las columnas que nos interesan
            tabla_resultado = tabla_nieve [['idema', 'ubi', 'nieve']]
            tabla_resultado.drop_duplicates ()
            print (tabla_resultado)
            pass
        else:                       #Si hay algún error
            print ("Error")
        
    else:                       #Si hay algún error
        print ("Error")

if __name__ == "__main__":
    main ()
    
    
    
    