Uso
===

Instalacion
-----------

Solo se necesita Python 3.9 o superior (Tkinter para la version grafica).

.. code-block:: bash

   git clone https://github.com/rafj26/JuegoIoT.git
   cd JuegoIoT

Ejecucion
---------

.. code-block:: bash

   python3 main.py          # Version terminal
   python3 main_gui.py      # Version grafica

Reglas de puntuacion
--------------------

==============================  ======
Decision                        Puntos
==============================  ======
Alerta real atendida            +2
Alerta falsa atendida           -1
Alerta real ignorada            -2
Alerta falsa ignorada           0
==============================  ======

Se empieza con 15 puntos y se gana terminando las 5 rondas con 15 o mas.

Arquitectura
------------

El proyecto sigue el patron MVC:

* :mod:`modelos` contiene la logica de negocio y no imprime nada.
* :mod:`vistas` presenta los datos (terminal o Tkinter).
* :mod:`controladores` coordina el modelo y la vista.

Generar esta documentacion
--------------------------

.. code-block:: bash

   pip install -r requirements-docs.txt
   cd docs
   make html        # Resultado en docs/_build/html/index.html
