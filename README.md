# Gestor de Memoria y Procesos

Este es un simulador simple de un sistema operativo mini que gestiona memoria y procesos con simulación de CPU.

## Algoritmo de Memoria: Buddy System (Sistema de Colegas)
La gestión de memoria utiliza ahora el algoritmo **Buddy System**. 
- La memoria se divide en bloques de tamaño potencia de 2 ($2^k$).
- Cuando se solicita memoria, el sistema busca el bloque libre más pequeño que sea potencia de 2 suficiente para alojar la solicitud.
- Si el bloque encontrado es muy grande, se divide por la mitad repetidamente hasta obtener el tamaño adecuado.
- Al liberar memoria, se intenta fusionar el bloque con su "colega" (buddy) si este también está libre, reconstruyendo bloques más grandes.

## Comandos Disponibles

### Gestión de Procesos (Nuevo)
- **`create <size> <burst>`**
  - Crea un nuevo proceso que requiere `<size>` de memoria y una ráfaga de CPU de `<burst>` ciclos.
  - Ejemplo: `create 10 5` (Tamaño 10, 5 ciclos de CPU).
- **`tick`**
  - Avanza un ciclo de reloj en la CPU. Ejecuta el proceso actual y reduce su ráfaga restante.
  - Si el proceso termina, libera su memoria automáticamente.
- **`ps`**
  - Muestra la lista de procesos activos (PID, tamaño, estado, ráfaga restante).
 - Algoritmo: Round-Robin con quantum configurable (por defecto 2).
 - Sincronización: Semáforo implícito por dispositivo de E/S (cola por dispositivo).

### Gestión de Memoria
- **`alloc <size>`**
  - Asignación manual de memoria. Redondea `size` a la siguiente potencia de 2.
- **`free <pid>`**
  - Libera la memoria ocupada por el PID especificado y fusiona bloques libres (buddies).
- **`lock <start> <size>`**
  - Bloquea los bloques de memoria que solapan con la región indicada.
- **`compact`**
  - En el Buddy System, esto ejecuta una fusión manual de bloques libres adyacentes (coalescencia), ya que no existe compactación tradicional.
- **`show`**
  - Visualización gráfica de la memoria.

### Gestión de Archivos
- **`fs`** entra al modo de archivos:
  - `mkfile <nombre> <size>` crea un archivo en el directorio raíz.
  - `open <nombre>` abre un archivo.
  - `close <nombre>` cierra un archivo.
  - `ls` lista los FCB del directorio raíz.

### Gestión de E/S
- **`devices`** lista los dispositivos simulados (`teclado`, `disco`).
- **`io <pid> <dispositivo> <ticks>`** solicita E/S. El proceso pasa a estado `WAITING`. Al completar, se simula la interrupción y el proceso vuelve a `READY`.

## Ejecución

```bash
python main.py
```

## Requisitos de Visualización
- `pip install matplotlib`
- Colores:
  - Verde: libres
  - Azul: asignados a PID
  - Rojo: bloqueados

## Extensión C++ (Opcional)
- El módulo `mini_os_cpp` acelera la fusión de bloques libres (Buddy System) usando C++.
- El simulador usa automáticamente este módulo si está disponible.

### Compilación en Windows
- Requisitos: `pip install pybind11` y tener un compilador de C++ (MSVC/Build Tools).
- Compilar en el proyecto:
```bash
python setup.py build_ext --inplace
```
- Verificar:
```bash
python -c "import mini_os_cpp; print('OK')"
```

## Aceleración Nativa
- C++ con `pybind11` (`mini_os_cpp`) puede acelerar la coalescencia del Buddy System y se usa automáticamente si está disponible.

## Algoritmos Utilizados
- Planificación: Round-Robin (cola de listos, cambio de contexto por quantum).
- Memoria: Buddy System (asignación por potencias de 2, coalescencia).
- Sincronización: Semáforo por dispositivo mediante colas FIFO.
- E/S: Dispositivos con solicitudes y atención por ticks; interrupción que retorna el proceso a `READY`.

## Integración de Módulos
- Procesos pueden solicitar E/S; al completar, la interrupción notifica al planificador y el proceso regresa a la cola de listos.
- El sistema de archivos simula FCB y operaciones básicas integradas en el ciclo del simulador.

## Pruebas Rápidas

### Escenario Manual (Windows PowerShell)
Puedes alimentar comandos automáticamente:
```powershell
@(
  "create 8 3",
  "create 16 3",
  "ps",
  "tick",
  "io 1 disco 2",
  "tick",
  "tick",
  "ps",
  "exit"
) | python main.py
```
Observa:
- Round Robin con quantum 2 y cambios de contexto.
- `io` bloquea el proceso y la interrupción lo devuelve a `READY`.

### Prueba Automatizada
```bash
python tests/test_scenario.py
```
Valida:
- Creación y finalización de procesos.
- Bloqueo por E/S y retorno por interrupción.
- Operaciones de FS (`mkfile/open/close/ls`).
- Asignación/liberación/compactación de memoria.
