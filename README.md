# File-Transfer-over-UDP
***
Trabajo práctico I: File Transfer (over UDP)
Introducción a los Sistemas Distribuidos (1c-2025)
***
## Integrantes
| Nombre   | Apellido  | Correo FIUBA         | Usuario de Github                                 |
|----------|-----------|----------------------|--------------------------------------------------|
| Jesabel  | Pugliese  | jpugliese@fi.uba.ar |  [jesapugliese](https://github.com/jesapugliese) |
| Josué    | Martel    | nmartel@fi.uba.ar   | [josValentin-fiuba](https://github.com/josValentin-fiuba) |
| Leticia  | Figueroa  | lfigueroar@fi.uba.ar| [leticiafrR](https://github.com/leticiafrR)      |
| Andrea   | Figueroa  | afigueroa@fi.uba.ar | [AndreaFigueroaR](https://github.com/AndreaFigueroaR)      |
| Kevin    | Vallejo   | kvallejop@fi.uba.ar | [Kevin00404](https://github.com/Kevin00404) |

## Objetivo
 El presente trabajo práctico tiene como objetivo la puesta en práctica de los conceptos y herramientas necesarias para la **implementación de un protocolo RDT** . 
 Para lo cual se desarrollaron las aplicaciones para un sistema de almacenamiento de archivos (upload and download) bajo una arquitectura cliente-servidor.
 Las operaciones de utilidad para clientes del servidor son:
-  **upload**: Transferencia de un archivo del cliente hacia el servidor
-  **download**: Transferencia de un archivo del servidor hacia el cliente
Para la concretización de estas mismas se implementó un protocolo de aplicación básico que especifica los mensajes intercambiados entre los distintos procesos así como un Reliable Data Transfer sobre un medio Un-Reliable (protocolo de transporte UDP).

 Además se usó la herramienta _mininet_ para virtualmente simular redes (a nivel capa de Red y capa de Enlace) y distintas condiciones sobre estas con la finalidad de poder proveer garantías sobre la **confiabilidad** de la comunicación.

## Simulación de topología de Red: Mininet
Para poder testear el reliable data transfer desarrollado en diferentes topologías de red se usó la herramienta _mininet_, para lo cual puede abrir una terminal y ejecutar:
``` bash
pip install mininet
```
Hecho esto dentro del subdirectorio `\File-Transfer-over-UDP\src\topology` se podrán encontrar programas que se encargan de configurar diferentes topologías de red con diferentes características cada una. 

Para ejecutar el programa sobre estas topologías virtuales se necesitará primero _levantar_ la red virtual deseada ejecutando su respectivo programa como `sudo`. Por ejemplo, si se quiere probar sobre la topología `basic_lossy_net` (que consiste en una red pequeña con 2 hosts y con pérdida de paquetes del 10%) se deberá ejecutar:
``` bash
sudo python3 basic_lossy_net.py
```
El programa, después de establecer la red virtual abrirá en su terminal la interfaz por linea de comando de mininet que le permitirá interactuar con dicha topología por ejemplo ejecutando commandos y/o programas en los sitemas terminales (hosts). En nuestro caso nos interesa ejecutar en un host l apalicación del servidor y en otro una aplicación de cliente (download o upload):

``` bash
mininet> host_2 python3 ..\start-server.py <args>
```
ejecuta los programas con los flags como indica la documentación de los programas. 
Ten en cuenta que :
- Los hosts que defininste en la red virtual teienen "montado" tu file system local
- Si usas rutas relativas la ruta esolverá desde el directorio raiz (lo mismo que siempre tener que poner rutas absolutas).
Además:
- No uses en dos hosts distintos mismos puertos
