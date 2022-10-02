# PRACTICA Final - Contenedores: más que VMs 

## Docker y Docker compose

Sección relacionada con Docker y docker-compose de la práctica final del módulo `Contenedores: más que VMs`

## Índice:
- [Repositorio GIT](#repositorio-git):
- [Describiendo la web](#describiendo-la-web)
- [Funcionamiento](#funcionamiento)
- [Requisitos para hacerla funcionar](#requisitos-para-hacerla-funcionar)
- [Variables configurables](#variables-configurables)
***

> La imagen generada puede funcionar de manera autónoma usando una base de datos sqlite3.
> 
> Esta base de datos no es persistente.
> 
> Para dotarla de persistencia es necesario conectarla con una base de datos postgressql


## Repositorio GIT

https://github.com/KeepCodingCloudDevops6/contenedores-roberto.git



## Describiendo la web

La aplicación a desplegar está desarrollada en python + django.

El frontend es un formulario para jugar a pares y nones y la base de datos una tabla con el histórico de partidas ganadas por el jugador y por la máquina.


Para dotar de persistencia la página puede usar sqlite3 o postgressql

> Se tiene en cuenta el objetivo del proyecto de trabajar con un sistema gestor de bases de datos externo. 
> 
> Sin embargo si la conexión a la base de datos postgres no se puede llevar a cabo la web no dará ningún error fatal. 
> 
> Para evitarlo, y de modo automático, la web funcionará utilizando una base de datos sqlite3 localizada en el directorio de trabajo para evitar que la aplicación devuelva un error al no poder conectar con la base de datos. 
> 
> También se muestra un aviso en caso de que no se esté usando la base de datos externa para poder solucionar la conexión.


Esta base de datos sqlite no es persistente una vez borrado el contenedor y la única finalidad es que la aplicación no de error fatal si la conexión a la base de datos externa no se produce correctamente.

Se puede probar renombrando en la raíz del repositorio el fichero docker-compose.yaml y el fichero docker-compose.yaml_standalone a docker-compose.yaml y ejecutar el siguiente comando:

```bash
docker-compose up --build --force-recreate
```

Con el comando indicado se puede ver que si se regeneran (o se eliminan) los contenedores no hay persistencia de datos y se pierde la información de los resultados anteriores.

A la hora de utilizar la web con contenedores es necesario utilizar un servidor de postgressql.



## Funcionamiento

La aplicación es una única página que permite jugar a pares y nones contra la máquina.

La aplicación consulta en la base de datos el histórico de partidas jugadas y los muestra en pantalla.
También se dispone de un formulario para poder jugar una partida.
Una vez se envía se resuelve la partida con los datos enviados en el formulario y el número elegido por la máquina, se actualiza la tabla con el nuevo resultado y se vuelve a cargar la página.

La aplicación es configurable en los siguientes valores:
- Puerto de acceso interno en el contenedor web
- Puerto de acceso externo vía web (puerto en la máquina local) 
- Nombre de la base de datos
- Usuario de la base de datos
- Contraseña de la base de datos

Se ejecuta con docker-compose y se construyen dos imágenes.

1. DB:

    La imágen de la base de datos utiliza una imagen oficial de postgres-alpine 15  desde el fichero `Dockerfile-db`.

    Se pasó de un tamaño de 376MB a 218MB al elegir la imagen postgres-alpine en lugar de la imagen de postgres sin reducir.

    Se configuran las siguientes variables de entorno siguiendo las indicaciones de la documentación de la imagen:
    - POSTGRES_DB
    - POSTGRES_USER
    - POSTGRES_PASSWORD

    Estas variables son configurables en el archivo `.env` que está en la raíz del repositorio

    La imagen utiliza 3 volúmenes.

    2 volumenes son bindmounts son los archivos necesarios para la configuración de la base de datos:
    1. Uno es un archivo dump con la creación de las tablas y registros necesarios para el funcionamiento de la web.
    2. El otro archivo es el script que prepara la configuración de postgres para que se guarden registros en formato json y realice la importación del dump de inicialización. Esto es necesario para poder aplicar de manera efectiva 

    El último volumen es un Volumen de docker para hacer la base de datos persistente.



2. Web:

    Para la imagen de la aplicación empecé utilizando una imagen de python a la que añado Django como base. La imagen tenía un tamaño de 900MB.

    Posteriormente realicé un cambio de imagen base por python:alpine reduciendo a la mitad el tamaño de la imagen.

    Aplicando técnicas de muti stage he conseguido un tamaño final de 95MB.

    Para la imagen de la aplicación web es posible configurar:
    - Puerto del servicio en el contenedor.
    - Puerto de acceso público (máquina local) a la web.
    - Tamaño máximo de los archivos de logs.
    - Numero de ficheros de logs antes de rotar.

    La aplicación ha sido programada para generar logs de actividad en formato json que se almacenan en el fichero /var/logs/evenodds.log.json
    
    También guarda en formato json ficheros de actividad a nivel de servidor en /var/log/evenodds.log

    ```bash
    docker exec -it practica_web_1 tail  /var/log/evenodds.log.json /var/log/evenodds.log
    ==> /var/log/evenodds.log.json <==
    {"server_time": "22/Sep/2022 08:00:36,190", "message": "{'id': 1, 'player': 21, 'pc': 16}"}
    {"server_time": "22/Sep/2022 08:00:57,069", "message": "{'id': 1, 'player': 21, 'pc': 16}"}
    {"server_time": "22/Sep/2022 08:00:57,069", "message": "{"winner": "", "player": 0, "ia": 3, "player_choice": "none", "nochoice": true}"}
    {"server_time": "22/Sep/2022 08:00:59,084", "message": "{'id': 1, 'player': 21, 'pc': 16}"}
    {"server_time": "22/Sep/2022 08:00:59,084", "message": "{"winner": "You", "player": 0, "ia": 2, "player_choice": "even"}"}
    {"server_time": "22/Sep/2022 08:01:00,675", "message": "{'id': 1, 'player': 22, 'pc': 16}"}
    {"server_time": "22/Sep/2022 08:01:03,864", "message": "{'id': 1, 'player': 22, 'pc': 16}"}
    {"server_time": "22/Sep/2022 08:01:03,864", "message": "{"winner": "You", "player": 0, "ia": 1, "player_choice": "odd"}"}

    ==> /var/log/evenodds.log <==
    {"server_time": "22/Sep/2022 08:00:36", "message": ""GET / HTTP/1.1" 200 3092"}
    {"server_time": "22/Sep/2022 08:00:57", "message": ""POST / HTTP/1.1" 200 3110"}
    {"server_time": "22/Sep/2022 08:00:59", "message": ""POST / HTTP/1.1" 200 3674"}
    {"server_time": "22/Sep/2022 08:01:00", "message": ""GET / HTTP/1.1" 200 3092"}
    {"server_time": "22/Sep/2022 08:01:03", "message": ""POST / HTTP/1.1" 200 3673"}
    ```


    
## Requisitos para hacerla funcionar.

Para que funcione con persistencia es necesario:
- disponer del código del repositorio.
- disponer en local de docker o docker desktop 
- disponer de docker-compose como aplicación o docker compose como plugin


d. Instrucciones para ejecutarla en local

1-. Descarga en un directorio vacío el código en un directorio de una máquina con docker y docker-compose como plugin o como aplicación:
    git clone git@github.com:KeepCodingCloudDevops6/contenedores-roberto.git

2-. No es necesario modificar la configuración por defecto pero es posible modificar varios parámetros en el archivo .env

3-. Para lanzar la aplicación ejecuta el comando:
docker-compose up

En los logs de la aplicación aparece un mensaje que se puede acceder con la dirección 0.0.0.0:PUERTO 
Hay que tener en cuenta que esa dirección se refiere a la máquina local y el puerto es el valor de APP_PORT en el fichero .env
No es posible acceder a esa dirección con el navegador directamente.

Para acceder desde el navegador es necesario acceder por 127.0.0.1:PUERTO siendo PUERTO el puerto configurado en el archivo .env en la variable EXPOSED_PORT

Por defecto la URL de acceso es http://127.0.0.1:9000



## Variables configurables

La aplicación funciona sin necesidad de hacer ningún ajuste de configuración.

Sin embargo es posible configurar los siguientes valores definidos en el archiov `.env` en la raíz del repositorio:

-  Base de datos 

| Variable | Valor por defecto |
| --- | ---
| POSTGRES_DB | postgres |
| POSTGRES_USER | postgres |
| POSTGRES_PASSWORD | postgres |

- WEB 

| Variable | Valor por defecto |
| --- | ---
| APP_PORT | 9000 |
| EXPOSED_PORT | 9000 |
| MAX_LOGS_SIZE | 20m |
| MAX_LOGS_FILES | 10 |
