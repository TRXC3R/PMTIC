import param
import geoviews as gv
from Datos_AEMET import Datos_AEMET

class EstacionesAEMET(param.Parameterized):
    """
    Clase interactiva para visualizar estaciones meteorológicas en un mapa.

    Atributos:
        altura_minima (param.Integer): Altura mínima seleccionable por el usuario.
        provincias (param.ListSelector): Selector múltiple para elegir provincias.

    Métodos:
        plot(): Devuelve un objeto GeoViews con el mapa y las estaciones filtradas.
    """

    # Aquí se crean los objetos que luego se representan en la interfaz gráfica
    altura_minima = param.Integer()
    provincias = param.ListSelector(default=['TODAS'])
    nieve_minima = param.Integer()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datos_aemet = Datos_AEMET()
        self.param['provincias'].objects = self.datos_aemet.get_provincias()
        limites_altura = self.datos_aemet.get_altura_min_max()
        self.param['altura_minima'].bounds = (limites_altura[0], limites_altura[1])
        limites_nieve = self.datos_aemet.get_nieve_min_max()
        self.param["nieve_minima"].bounds = (limites_nieve[0], limites_nieve[1])

    def get_estaciones_filtradas(self):
        """
        Filtra las estaciones según los parámetros actuales.

        Returns:
            pd.DataFrame: DataFrame con las estaciones filtradas.
        """
        # Verificar si el atributo `self.provincias` contiene una lista válida y si incluye "TODAS".
        # Si "TODAS" está seleccionada, se obtienen todas las provincias disponibles excepto "TODAS" misma.
        # Esto se realiza llamando al método `get_provincias()` y excluyendo el primer elemento (que es "TODAS").
        if self.provincias and "TODAS" in self.provincias:
            provincias_seleccionadas = self.datos_aemet.get_provincias()[1:]  # Excluir "TODAS"
        else:
            # Si no se seleccionó "TODAS", usar las provincias seleccionadas por el usuario.
            # Si `self.provincias` es None (no se ha seleccionado nada), usar una lista vacía para evitar errores.
            provincias_seleccionadas = self.provincias or []

        # Llamar al método `get_estaciones` de la clase `Datos_AEMET` para obtener las estaciones filtradas.
        # Se filtran las estaciones según la altitud mínima (`self.altura_minima`) y las provincias seleccionadas.
        return self.datos_aemet.get_estaciones(self.altura_minima, provincias_seleccionadas, self.nieve_minima)



    def plot(self):
        """
        Genera un mapa interactivo con las estaciones meteorológicas filtradas.

        Returns:
            gv.Element: Objeto GeoViews con el mapa y puntos representando las estaciones.
        """
        mapa = gv.tile_sources.OSM.options(width=1000, height=500)
        estaciones = self.get_estaciones_filtradas()

        if estaciones.empty:
            print("No hay estaciones disponibles con los filtros seleccionados.")
            return mapa

        # Crear un conjunto de puntos geográficos a partir del DataFrame `estaciones`.
        # Los puntos se ubican en el mapa usando las columnas 'longitud_decimal' y 'latitud_decimal' como coordenadas.
        # La columna 'altitud' se incluye como una dimensión adicional para representar atributos de los puntos (por ejemplo, para colorearlos).
        puntos = gv.Points(estaciones, ['longitud_decimal', 'latitud_decimal'], ['altitud'])

        # Configurar opciones visuales para los puntos en el mapa:
        # - `size=12`: Establece el tamaño de los puntos.
        # - `color='altitud'`: Colorea los puntos según los valores de la columna 'altitud'.
        # - `cmap='viridis'`: Utiliza la paleta de colores 'viridis' para representar la altitud (gradiente de color).
        puntos = puntos.opts(size=12, color='altitud', cmap='viridis')

        
        return mapa * puntos
