"""
visualizarDatosAEMET.py

Este script crea una interfaz interactiva para visualizar datos meteorológicos obtenidos de estaciones AEMET.
Requiere el módulo 'EstacionesAEMET' y la librería 'panel'.
"""

import EstacionesAEMET
import panel as pn

def main():
    try:
        # Inicialización del componente principal
        componente = EstacionesAEMET.EstacionesAEMET(name='Panel de estaciones meteorológicas')
        #text_input_provinicas = pn.widgets.TextInput(name = "Provincias")

        #Sincronizar los widgets con el parametro
        #pn.bind(lambda v, setattr(componente, 'provinicas', v), text_input_provincias)
        
        # Diseño interactivo con título y elementos organizados en columnas
        layout = pn.Column(
            "## Visualización de Datos Meteorológicos",
            pn.Row(componente.param, componente.plot)
            #pn.Row(componente.param, componente.plot, text_input_provinicas)

        )
        
        # Mostrar la interfaz (puede usarse servable() para servidores web)
        layout.show()
    except Exception as e:
        print(f"Error al ejecutar la aplicación: {e}")

if __name__ == "__main__":
    main()
