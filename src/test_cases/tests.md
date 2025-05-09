# Tests
## test_cases
Para testear los resultados obtenidos de un programa, por ejemplo `upload.py`
1. Ejecutar el programa del `server.py`. Por ejemplo como:
```bash
python3 start_server.py -H 127.0.0.1 -p 9000 -r sw -v
```
2. Ejecutar el programa `upload.py` indicando un archivo de los sets de pruebas en el subdirectorio test_cases. Por ejemplo:
```bash
python3 upload.py -H 127.0.0.1 -p 9000 -s test_cases/1000_bytes_unos.bin -n upload_1000_bytes_unos.bin
```
3. Comparar la salida obtenida con el archivo de prueba. Por ejemplo
```bash
cmp -l test_cases/1000_bytes_unos.bin upload_1000_bytes_unos.bin
```
## Generación de archivos de prueba

### Escritura de bloques de 1024 bytes de ceros 
Desde la terminal
```bash
dd if=/dev/zero of=nombre-arch.bin bs=1 count=1024
```
en este caso, solo se escirbe 1 bloque

### Escritura de bloques de n bytes (donde todos los bits son 1)
```bash
yes $'\xFF' | head -c 1024 > archivo_lleno_de_unos.bin
```

### ADICIONAL: visualización del contenido binario

Desde la terminal
```bash
xxd nombre-arch.bin
```