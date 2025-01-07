import json
from typing import Union

import pandas as pd
import requests

class Datos_AEMET:
    def __init__(self):
        self.estaciones= Datos_AEMET.__get_estaciones__() #self.estaciones es un miembro de instancia
                                                      #Como es un método estático, para invocarlo hay que llamr a su clase
        self.convertir_coordenadas()
        
    def convertir_coordenadas(self):
        self.estaciones['latitud_decimal'] = self.estaciones['latitud'].apply(lambda lat: (int(lat[0:2]) + (int(lat[2:4])/60) + int(lat[4:6])/3600) * (1 if lat[6]=='N' else -1)) #lambda es una función anónima y hace lo que le sigue
        self.estaciones['longitud_decimal'] = self.estaciones['longitud'].apply(lambda lon: (int(lon[0:2]) + (int(lon[2:4])/60) + int(lon[4:6])/3600) * (1 if lon[6]=='E' else -1)) #lambda es una función anónima y hace lo que le sigue
        #self.estaciones['altitud'] = self.estaciones['altitud'].astype('int32')
        self.estaciones = self.estaciones.astype({'altitud': int})

    def get_estaciones(self, altura_minima, provincia, nieve_minima, /):  # / indica que los argumentos se pasan por posicion                                                  ojo con esto!!!! CAE EN ENERO
                                                            #Como queremos coger un dato del init, este método tiene que ser de instancia, es decir, self
        estaciones=self.estaciones
        #altura_minima=self.altura_minima
        estaciones = estaciones.query('`nieve` >= @nieve_minima and `altitud` >= @altura_minima')
        if provincia is not None and provincia != "TODAS":
            estaciones = estaciones.query('provincia == @provincia')  

        # estaciones = estaciones.query('altitud >= @altura_minima and provincia == @provincia')
        return estaciones
        
    def get_provincias(self):
        provincias = list(set(self.estaciones['provincia'].to_list())) #SET PARA ELIMINAR DUPLICADOS
        provincias.sort() # Ordena la lista alfabéticamente
        #provincias = ['TODAS'].extend(provincias) # DEVUELVE NONE; PORQUE ES INPLACE
        provincias.insert(0, 'TODAS')
        return provincias #Devuelve Object, es decir, cualquier cosa
    
    
    def get_altura_min_max(self):
        return int(self.estaciones['altitud'].min()), int(self.estaciones['altitud'].max())
    
    def get_nieve_min_max(self):
        return int(self.estaciones['nieve'].min()), int(self.estaciones['nieve'].max())
    
    @staticmethod
    def __get_estaciones__():
        url='https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones'
        # Renombrar la columna "indicativo" a "idema"
        tabla_provincias = Datos_AEMET.getAEMETTable(url=url).drop_duplicates()
        tabla_provincias.rename(columns={'indicativo': 'idema'}, inplace=True)

        url2='https://opendata.aemet.es/opendata/api/observacion/convencional/todas'
        tabla_todas = Datos_AEMET.getAEMETTable(url=url2)
        # Reemplazar valores nulos en la columna 'nieve' por 0
        tabla_todas['nieve'] = tabla_todas['nieve'].fillna(0)

        tabla_todas = tabla_todas[(tabla_todas['nieve'] >= 0)][['idema', 'ubi', 'nieve']].drop_duplicates()
        #tabla_todas.to_csv('tabla_todas.csv', index=False)                                                                                       DESCOMENTAR EN EL EXAMEN (PRUEBAS)


        tabla_provincias = tabla_provincias.merge(tabla_todas, on='idema')
        #tabla_provincias.to_csv('tabla_provincias_nieve.csv', index=False)                                                                       DESCOMENTAR EN EL EXAMEN (PRUEBAS)
        return  tabla_provincias
        #file_name = 'estaciones_con_nieve.csv'
        #return Datos_AEMET.getAEMETTable(file_name=file_name)
    
    @staticmethod #También existe @classmethod, esto obliga a que el primer parametro sea un parametro de clase
    def get_datos_json (url : str):
        headers={'accept':'application/json', 
                'api_key': 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkYXZpZC5tYXJxdWV6QGFsdW1ub3MudXBtLmVzIiwianRpIjoiN2RlM2M0YTctNGE3Yi00ODBiLTg3MzgtNzhjMDlkYTc4YTBiIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3MzYxODM2MzksInVzZXJJZCI6IjdkZTNjNGE3LTRhN2ItNDgwYi04NzM4LTc4YzA5ZGE3OGEwYiIsInJvbGUiOiIifQ.0i9gqkqMLljLNs0h0yjh3hcii0FfB1G_L9n1j8A3pO0' }
        
        #Hacemos una petición GET que nos devuelve información
        r = requests.get(url, headers =  headers)

        #Obtenemos el cuerpo del mensaje de respuesta y procesamos ese JSON que nos ha devuelto la petición.
        if (r.status_code == 200):
            cuerpo = json.loads (r.text)  
        else:
            cuerpo = None
        #Devolvemos si ha habido algún error o no  y el JSON procesado
        return r.status_code, cuerpo

    @staticmethod
    def getAEMETTable(*, url=None, file_name=None) -> pd.DataFrame:
        """
        Obtiene una tabla de datos meteorológicos de AEMET desde una URL o un archivo local.

        Args:
            url (str, opcional): URL desde la cual obtener los datos en formato JSON.
            file_name (str, opcional): Ruta del archivo CSV local que contiene los datos.

        Returns:
            pd.DataFrame: DataFrame con los datos meteorológicos obtenidos.
            None: Si no se proporciona una fuente válida o si ocurre algún error.
        """
        
        # Verificar si se proporciona una URL para obtener los datos
        if url:
            # Realizar la primera solicitud HTTP a la URL proporcionada
            status_code, primeros_datos = Datos_AEMET.get_datos_json(url)
            
            # Verificar si la primera solicitud fue exitosa (código HTTP 200)
            if status_code == 200:
                # Realizar una segunda solicitud a la URL contenida en 'primeros_datos'
                status_code, datos = Datos_AEMET.get_datos_json(primeros_datos['datos'])
                
                # Si la segunda solicitud también es exitosa, convertir los datos JSON a DataFrame
                if status_code == 200:
                    return pd.DataFrame(datos)
        
        # Si no hay URL pero se proporciona un archivo local, leerlo como DataFrame
        elif file_name:
            return pd.read_csv(file_name)
        
        # Si no se proporciona ninguna fuente válida o ocurre algún error, devolver None
        return None

    def main():
        url='https://opendata.aemet.es/opendata/api/observacion/convencional/todas'        
        url2='https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones'

        tabla_pandas = Datos_AEMET.getAEMETTable(url=url, file_name='todas-observaciones.csv')
        if not tabla_pandas is None:
            # Guardar el DataFrame en un archivo CSV
            tabla_pandas.to_csv('todas-observaciones.csv', index=False)
            print(f'Los datos tienen {len(tabla_pandas)} tuplas')
            print(f'Los datos tienen {len(tabla_pandas["idema"].drop_duplicates())} estaciones')
            tabla_resultado=tabla_pandas.query('prec >0')[['idema','ubi']].drop_duplicates()
            print(tabla_resultado)
            print(f'La tabla resultados tiene {len(tabla_resultado)} tuplas.')
            print()
            # d = dtale.show(tabla_pandas, host='localhost', open_browser=True)
            # input('Pulsa para continuar')
            
            #que estaciones que registran nieve en algún momento
            tabla_resultado=tabla_pandas.query('nieve > 0')[['idema','ubi']].drop_duplicates()
            print(tabla_resultado)
            print(f'La tabla resultados tiene {len(tabla_resultado)} tuplas.')
            print()
            
            #que estaciones que no registran nieve en ningún momento
            idemas_con_nieve=set(tabla_resultado['idema'].to_list())
            todos_los_idemas=set(tabla_pandas['idema'].drop_duplicates().to_list())
            idemas_sin_nieve=pd.DataFrame(todos_los_idemas.difference(idemas_con_nieve))
            print("idemas_sin_nieve")
            print(idemas_sin_nieve)
            print(f'La tabla resultados tiene {len(idemas_sin_nieve)} tuplas.')
            print()
            
            #que estaciones que registran nieve en algún momento con estaciones por debajo de los 1500m
            altura_maxima=1500
            tabla_resultado=tabla_pandas.query('`nieve` > 0 and `alt` < @altura_maxima')[['idema','ubi', 'alt']].drop_duplicates()
            print(tabla_resultado)
            print(f'La tabla resultados tiene {len(tabla_resultado)} tuplas.')
            print()
            
            #que estaciones que registran nieve en algún momento
            # Obtener la tabla de datos meteorológicos desde el archivo CSV
            tabla_provincias = Datos_AEMET.getAEMETTable(url=url2, file_name='datos-idema-provincia.csv')

            # Renombrar la columna "indicativo" a "idema"
            tabla_provincias.rename(columns={'indicativo': 'idema'}, inplace=True)

            # Guardar el DataFrame modificado en un nuevo archivo CSV
            tabla_provincias.to_csv('datos-idema-provincia.csv', index=False)
            #tabla_resultado=tabla_pandas.query('`nieve` > 0 and `nieve` = ')[['idema','ubi','nieve']].drop_duplicates()
            tabla_resultado = tabla_pandas[(tabla_pandas['nieve'] > 0)][['idema', 'ubi', 'nieve']].drop_duplicates()
            #tabla_resultado.to_csv('tabla_resultado.csv', index=False)

            tabla_idema_provincia=tabla_resultado.merge(tabla_provincias, on='idema')
            tabla_final=tabla_idema_provincia['provincia'].drop_duplicates()
            print(tabla_final)
            print(f'La tabla resultados tiene {len(tabla_final)} tuplas.')
            print() 
            
            #Pasar a csv:
            tabla_final.to_csv('estaciones_con_nieve.csv', index=False)
            
            #valor medio del espesor de la nieve en las estaciones que registran nieve. Consejo: mirad una tabla con una columna métodos para contabilizar
            #Estación a mayor y a menor altura donde se ha registrado nieve.

if __name__ == "__main__":
    Datos_AEMET.main()
