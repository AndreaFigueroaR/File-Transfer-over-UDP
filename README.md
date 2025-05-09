# File-Transfer-over-UDP

***
Trabajo práctico I: File Transfer (over UDP)

Introducción a los Sistemas Distribuidos (1c-2025)
***

## Integrantes
| Nombre   | Apellido  | Padrón | Correo FIUBA         | Usuario de Github                                 |
|----------|-----------|--------|----------------------|--------------------------------------------------|
| Jesabel  | Pugliese  | 110860 | jpugliese@fi.uba.ar |  [jesapugliese](https://github.com/jesapugliese) |
| Josué    | Martel    | 110696 | nmartel@fi.uba.ar   | [josValentin-fiuba](https://github.com/josValentin-fiuba) |
| Leticia  | Figueroa  | 110510 | lfigueroar@fi.uba.ar| [leticiafrR](https://github.com/leticiafrR)      |
| Andrea   | Figueroa  | 110450 | afigueroa@fi.uba.ar | [AndreaFigueroaR](https://github.com/AndreaFigueroaR)      |
| Kevin    | Vallejo   | 109975 | kvallejop@fi.uba.ar | [Kevin00404](https://github.com/Kevin00404) |

## Tabla de Contenidos

- [Objetivo](#objetivo)
- [Ejecución](#ejecución)
    - [Servidor](#servidor)
    - [Cliente: Upload](#cliente-upload)
    - [Cliente: Download](#cliente-download)
- [Simulación de topología de Red: Mininet](#simulación-de-topología-de-red-mininet)

## Objetivo
 El presente trabajo práctico tiene como objetivo la puesta en práctica de los conceptos y herramientas necesarias para la **implementación de un protocolo RDT** . 
 Para lo cual se desarrollaron las aplicaciones para un sistema de almacenamiento de archivos (upload and download) bajo una arquitectura cliente-servidor.
 Las operaciones de utilidad para clientes del servidor son:
-  **upload**: Transferencia de un archivo del cliente hacia el servidor
-  **download**: Transferencia de un archivo del servidor hacia el cliente
Para la concretización de estas mismas se implementó un protocolo de aplicación básico que especifica los mensajes intercambiados entre los distintos procesos mediante su Reliable Data Transfer (RDT) construido sobre un medio Un-Reliable (protocolo de transporte UDP).

 Además se usaron distintas herramientas para hacer un análisis más abarcativo. Entre estas están:
 - _mininet_, herramienta que nos permite simular redes virtualmente (a nivel capa de Red y capa de Enlace) y distintas condiciones sobre estas con la finalidad de poder proveer garantías sobre la **confiabilidad** que ofrecen los RDTs implementados.
 - _miniedit_, aplicacion con interfaz gráfica que provee mininet para el diseño y configuración de redes virtuales de forma intuitiva.
 - google collab para la generación de gráficos que permitan analizar la salida de los programas (tiempo de transferencia, timeouts, etc) así como el tráfico generado en la red virtual,  y principalmente elo contraste de performance entre selective repeat y stop and wait.
 

## Ejecución

### Servidor

``` bash
start-server.py [-h] [-v | -q] [-H HOST] [-p PORT] [-r {sr,sw}] [-s STORAGE]
```

| Opción | Descripción |
|-|-|
| `-h`, `--help` | show this help message and exit |
| `-v`, `--verbose` | increase output verbosity |
| `-q`, `--quiet` | decrease output verbosity (default) |
| `-H HOST`, `--host HOST` | service IP address |
| `-p PORT`, `--port PORT` | service port |
| `-r {sr,sw}`, `--protocol {sr,sw}` | error recovery protocol: _Stop-And-Wait_ (default) or _Selective-Repeat_ |
| `-s STORAGE`, `--storage STORAGE` | storage dir path |

### Cliente: Upload

``` bash
python upload.py [-h] [-v | -q] [-H HOST] [-p PORT] [-r {sr,sw}] -n FILENAME -s SRC
```

| Opción | Descripción |
|-|-|
| `-h`, `--help` | show this help message and exit |
| `-v`, `--verbose` | increase output verbosity |
| `-q`, `--quiet` | decrease output verbosity (default) |
| `-H HOST`, `--host HOST` | service IP address |
| `-p PORT`, `--port PORT` | service port |
| `-r {sr,sw}`, `--protocol {sr,sw}` | error recovery protocol: _Stop-And-Wait_ (default) or _Selective-Repeat_ |
| `-n FILENAME`, `--name FILENAME` | file name |
| `-s SRC`, `--src SRC` | source file path |

#### Ejemplo

Ejemplo para hacer upload de un archivo `archivo.txt` que se desea guardar como `recibido.txt` en el servidor.

```bash
python3 upload.py -H <host> -p <port_number> -n recibido.txt -s /path/archivo.txt
```

### Cliente: Download

``` bash
python download.py [-h] [-v | -q] [-H HOST] [-p PORT] [-r {sr,sw}] -n FILENAME [-d DST]
```

| Opción | Descripción |
|-|-|
| `-h`, `--help` | show this help message and exit |
| `-v`, `--verbose` | increase output verbosity |
| `-q`, `--quiet` | decrease output verbosity (default) |
| `-H HOST`, `--host HOST` | service IP address |
| `-p PORT`, `--port PORT` | service port |
| `-r {sr,sw}`, `--protocol {sr,sw}` | error recovery protocol: _Stop-And-Wait_ (default) or _Selective-Repeat_ |
| `-n FILENAME`, `--name FILENAME` | file name |
| `-d DST`, `--dst DST` | destination file path |

#### Ejemplo

Ejemplo para hacer download de un archivo `archivo.txt` que se desea guardar como `recibido.txt` en el cliente.

```bash
python3 download.py -H <host> -p <port_number> -n archivo.txt -d /path/recibido.txt
```
## Ejemplo ejecución local
- Servidor
```bash
python3 start-server.py -H 127.0.0.1 -p 12345 -r sr -v
```
- Cliente Upload
```bash
python3 upload.py -H 127.0.0.1 -p 12345 -n resultado_upload.bin -s test_cases/crecimiento_cte/1MB.bin -r sr -v 
```
## Ejemplo de ejecución con red virtual simulada 
- Servidor: Ejecutar en el host 1
```bash
python3 start-server.py -H 10.0.0.1 -p 12345 -r sr -v
```
- Cliente Upload: Ejecutar en el host n
```bash
python3 upload.py -H 127.0.0.1 -p 12345 -n resultado_upload.bin -s test_cases/crecimiento_cte/1MB.bin -r sr -v 
```

## Simulación de topología de Red: Mininet
Para poder testear el reliable data transfer desarrollado en diferentes topologías de red se usó la herramienta _mininet_, para lo cual puede abrir una terminal y ejecutar:
``` bash
sudo apt install mininet
```
Hecho esto dentro del subdirectorio `\File-Transfer-over-UDP\src\topology` se podrán encontrar programas que se encargan de configurarla topología lineal requerida. 

Para probar programas sobre alguna topología virtual se puede usar tanto la interfaz gráfica que miniedit proporciona como comandos de mininet que proporcionan redes prediseñadas y también scripts de python que usen la API de mininet para configurar una red virtual.Una vez levantada la red virtual se podrán abrir terminales de cada host y ejecutar diferentes programas, es en este escenario que se probó nuestro sistema de transferencia de archivos sobre diferentes topologías detalladas en el informe.

## Fuentes

La topología de red para la fragmentación y el packet loss fue tomada del repositorio [LinearEnds topology use](https://github.com/gabrieldiem/linear-ends-topology-with-ip-frag).
