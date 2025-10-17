# Sistema de Seguridad IoT

Videojuego educativo desarrollado en Python que simula la gestión de alertas en una red de dispositivos IoT. El jugador asume el rol de administrador de sistemas y debe analizar alertas para determinar cuáles son reales y cuáles falsas, manteniendo la seguridad de la red.

## Descripcion General

Este proyecto es una implementación de un videojuego de seguridad IoT que demuestra conceptos avanzados de programación en Python, incluyendo Programación Orientada a Objetos, herencia, patrones de diseño y arquitectura de software.

El juego presenta una red de 8 dispositivos IoT diferentes (sensores de movimiento, temperatura, energia, RFID, ruido, camaras, routers y cerraduras inteligentes) que generan alertas durante 5 rondas. El jugador debe decidir qué alertas atender basándose en el analisis de la informacion disponible.

## Caracteristicas Principales

Programacion Orientada a Objetos - Implementacion completa con clases, herencia y polimorfismo

Herencia y Clases Abstractas - Clase base DispositivoBase que define la interfaz comun para todos los dispositivos

Patron MVC - Separacion clara entre Modelo (logica), Vista (presentacion) y Controlador (coordinacion)

Dos Interfaces de Usuario - Version terminal simple y version grafica con Tkinter

Dispositivos IoT Variados - 8 tipos de dispositivos con comportamiento especializado

Sistema de Puntuacion Dinamico - Reglas de juego bien definidas con bonificaciones y penalizaciones

Simulacion Contextual - Alertas generadas segun factores como hora del dia, dia de la semana

## Requisitos del Sistema

Python 3.9 o superior

Tkinter (incluido en la instalacion estandar de Python)

Sistema operativo: Windows, macOS o Linux (probado en Fedora)

## Instalacion

Clonar el repositorio:

```bash
git clone https://github.com/tunombre/Sistema-Seguridad-IoT.git
cd Sistema-Seguridad-IoT
```

Verificar que Python este instalado:

```bash
python3 --version
```

No es necesario instalar dependencias adicionales, todas las librerias utilizadas vienen incluidas en Python.

## Como Ejecutar

Version Terminal:

```bash
python3 main.py
```

Version con Interfaz Grafica (Tkinter):

```bash
python3 main_gui.py
```

## Como Jugar

El juego presenta 5 rondas en las que se generan alertas automaticamente en la red.

En cada ronda:
1. Se mostran las alertas generadas por los dispositivos IoT
2. Cada alerta tiene informacion: hora, tipo de dispositivo, ubicacion, descripcion
3. Debes seleccionar cuales alertas atender
4. El sistema evalua tus decisiones

Sistema de Puntuacion:

Puntos iniciales: 15 puntos

Alerta real atendida correctamente: +2 puntos

Alerta falsa atendida: -1 punto

Alerta real no atendida (ignorada): -2 puntos

Alerta falsa ignorada correctamente: 0 puntos

Condiciones de Victoria/Derrota:

Victoria: Finalizar con 15 o mas puntos de seguridad

Derrota: Finalizar con menos de 15 puntos

## Estructura del Proyecto

Archivos Principales:

main.py - Punto de entrada para la version terminal

main_gui.py - Punto de entrada para la version grafica

juego.py - Logica principal del juego, manejo de rondas y puntuacion

red_iot.py - Gestor de la red que almacena todos los dispositivos

alerta.py - Clase que representa una alerta individual

controlador.py - Coordinador para la version terminal (patron MVC)

controlador_gui.py - Coordinador para la version grafica (patron MVC)

vista.py - Presentacion terminal

vista_gui.py - Presentacion grafica con Tkinter

Dispositivos IoT:

dispositivo_base.py - Clase abstracta base que define la interfaz comun

sensor_movimiento.py - Sensor de movimiento con logica especializada

sensor_temperatura.py - Sensor de temperatura

sensor_energia.py - Sensor de consumo energetico

sensor_rfid.py - Sensor de control de acceso RFID

sensor_ruido.py - Sensor de niveles de ruido

camara.py - Camara de vigilancia

router.py - Router de red

cerradura.py - Cerradura inteligente

## Conceptos Implementados

Programacion Orientada a Objetos

Uso completo de clases y objetos

Encapsulamiento con atributos privados (convencion _nombre)

Metodos de instancia, metodos estaticos

Herencia y Polimorfismo

Clase abstracta DispositivoBase que define la interfaz

Ocho clases concretas que heredan de DispositivoBase

Sobrescritura de metodos (override) con super()

Metodos abstractos que fuerzan implementacion en clases hijas

Patron de Diseno MVC

Modelo: Contiene la logica de negocio (juego.py, red_iot.py)

Vista: Responsable de presentacion (vista.py, vista_gui.py)

Controlador: Coordina modelo y vista (controlador.py, controlador_gui.py)

Beneficio: La logica del juego se reutiliza en dos interfaces diferentes

Buenas Practicas de Desarrollo

Separacion de responsabilidades

Constantes de clase para valores fijos

Metodos pequenos y especificos

Nombres descriptivos y consistentes

Comentarios en puntos complejos

Validacion de entrada del usuario

Manejo de excepciones

Reutilizacion de codigo (DRY - Don't Repeat Yourself)

## Diagrama de Flujo

```
Inicio del Juego
    |
    v
Mostrar Pantalla de Bienvenida
    |
    v
Para cada Ronda (1-5):
    |
    +-- Inicializar Ronda
    |   |
    |   v
    |   Generar Alertas en todos los Dispositivos
    |   |
    |   v
    |   Mostrar Alertas al Jugador
    |   |
    |   v
    |   Solicitar Decision (que alertas atender)
    |   |
    |   v
    |   Procesar Decisiones y Actualizar Puntos
    |   |
    |   v
    |   Mostrar Resultados de la Ronda
    |
    v
Mostrar Pantalla Final
    |
    v
Mostrar Victoria o Derrota segun Puntos
    |
    v
Fin del Juego
```

## Tecnologias Utilizadas

Lenguaje: Python 3.9+

Interfaz Grafica: Tkinter (libreria nativa de Python)

Librerias del Sistema: random, datetime, abc (Abstract Base Classes)

## Ejemplos de Uso

Ejemplo Terminal:

```
==============================================================
SISTEMA DE SEGURIDAD IoT - ADMINISTRADOR DE REDES
==============================================================
Puntos iniciales: 15
Rondas totales: 5

Objetivo: Mantener 15 o mas puntos

Reglas de puntuacion:
  Alerta real atendida: +2 puntos
  Alerta falsa atendida: -1 punto
  Alerta real NO atendida: -2 puntos
  Alerta falsa NO atendida: 0 puntos
==============================================================

============================================================== 
RONDA 1/5
Puntos actuales: 15
==============================================================

Alertas detectadas a las 08:00:
--------------------------------------------------------------
[1] 08:00 | Sensor de Movimiento
    Ubicacion: Entrada Principal
    Alerta: Movimiento detectado en area restringida
    ID: DEV-001
--------------------------------------------------------------
[2] 08:00 | Sensor de Temperatura
    Ubicacion: Sala de Servidores
    Alerta: Fluctuacion de temperatura
    ID: DEV-002
--------------------------------------------------------------

Ingrese numeros de alertas a atender (separados por comas)
O ingrese 0 para no atender ninguna:
> 1
```

## Arquitectura del Codigo

La estructura utiliza el patron MVC con separacion clara de responsabilidades:

El Modelo (juego.py) contiene la logica del juego pero NO imprime nada. Solo retorna datos estructurados en diccionarios.

La Vista (vista.py / vista_gui.py) recibe datos del modelo y los presenta. No contiene logica de negocio.

El Controlador (controlador.py / controlador_gui.py) coordina las llamadas entre modelo y vista, manejando el flujo de ejecucion.

Esta arquitectura permite tener dos interfaces completamente diferentes sin duplicar la logica del juego.

## Preguntas Frecuentes

¿Puedo ejecutar esto en Windows?

Si, Python y Tkinter funcionan perfectamente en Windows. Solo necesitas tener Python instalado.

¿Cual es la diferencia entre main.py y main_gui.py?

main.py ejecuta la version con interfaz de terminal (texto)
main_gui.py ejecuta la version con interfaz grafica (ventanas visuales)

La logica del juego es identica en ambas, solo cambia la presentacion.

¿Puedo modificar las reglas del juego?

Si, todas las constantes estan definidas en la clase JuegoSeguridadIoT:
PUNTOS_INICIALES
TOTAL_RONDAS
PUNTOS_ALERTA_REAL_ATENDIDA
etc.

Solo modificas estos valores y el juego se adapta automaticamente.

¿Como agrego un nuevo tipo de dispositivo?

1. Crea un nuevo archivo en la carpeta modelos/dispositivos/
2. Hereda de DispositivoBase
3. Implementa los metodos abstractos
4. Agregalo a la lista de dispositivos en red_iot.py

¿Necesito instalar Tkinter por separado?

No, Tkinter viene incluido en la instalacion estandar de Python. Si por alguna razon no lo tienes, instalalo con:

```bash
sudo dnf install python3-tkinter
```

## Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.