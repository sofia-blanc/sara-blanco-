# Subsistema de Memoria y Almacenamiento de AutoOS

## 1. Descripción general

Este documento describe el subsistema de memoria y almacenamiento de
AutoOS, un prototipo funcional de sistema operativo especializado para
un vehículo inteligente.

El subsistema fue diseñado para representar de forma simulada los
principales conceptos de gestión de memoria y almacenamiento de un
sistema operativo.

Las funcionalidades implementadas son:

- Gestión de memoria RAM.
- Asignación y liberación de memoria.
- Detección de memoria insuficiente.
- Simulación de memoria virtual.
- Gestión de almacenamiento.
- Sistema virtual de archivos.
- Registro de eventos relacionados con memoria y almacenamiento.
- Pruebas unitarias de los componentes desarrollados.

## 2. Objetivo

El objetivo del subsistema es administrar los recursos de memoria y
almacenamiento utilizados por los procesos de un vehículo inteligente.

Entre los procesos que pueden requerir estos recursos se encuentran:

- GPS.
- Cámara.
- Sensores.
- Navegación.
- Multimedia.
- Comunicación.
- Procesos críticos del vehículo.

La implementación no representa físicamente una memoria RAM o un disco
real. Se trata de una abstracción funcional que permite visualizar,
probar y demostrar el comportamiento de estos recursos.

## 3. Arquitectura

El subsistema se encuentra en la siguiente carpeta:

```text
src/memory/
├── __init__.py
├── memory.py
├── virtual_memory.py
├── storage_manager.py
├── file_system.py
└── memory_log.py
```

Las pruebas unitarias se encuentran en:

```text
tests/
├── test_memory.py
├── test_virtual_memory.py
├── test_storage_manager.py
├── test_file_system.py
└── test_memory_log.py
```

## 4. Gestor de memoria RAM

### Archivo

```text
src/memory/memory.py
```

### Clase principal

```python
MemoryManager
```

### Responsabilidad

`MemoryManager` representa la memoria RAM disponible en AutoOS.

La clase mantiene los siguientes valores:

- Memoria total.
- Memoria utilizada.
- Memoria libre.

La memoria se expresa en megabytes.

### Capacidad configurada

Por defecto, AutoOS dispone de:

```text
4096 MB de RAM
```

### Operaciones

#### Asignar memoria

El método:

```python
allocate(size)
```

intenta reservar una cantidad determinada de memoria.

La operación retorna `True` cuando existe memoria suficiente y la
asignación se completa correctamente.

La operación retorna `False` cuando:

- El tamaño solicitado es menor o igual a cero.
- El tamaño solicitado supera la memoria disponible.

#### Liberar memoria

El método:

```python
release(size)
```

libera una cantidad de memoria previamente utilizada.

La implementación evita que la memoria utilizada tenga un valor
negativo.

#### Consultar disponibilidad

El método:

```python
has_enough_memory(required_memory)
```

permite determinar si existe memoria suficiente para una solicitud.

#### Serialización

El método:

```python
to_dict()
```

genera una estructura compatible con JSON para su uso posterior en:

- Dashboard.
- API.
- Supabase.
- Logs.
- Servicios de integración.

## 5. Memoria virtual

### Archivo

```text
src/memory/virtual_memory.py
```

### Clase principal

```python
VirtualMemory
```

### Responsabilidad

`VirtualMemory` simula un área de intercambio o SWAP.

Esta área puede utilizarse cuando la memoria RAM no dispone de espacio
suficiente para satisfacer una solicitud.

### Capacidad configurada

Por defecto, AutoOS dispone de:

```text
8192 MB de memoria virtual
```

### Operaciones

La clase permite:

- Asignar espacio en SWAP.
- Liberar espacio en SWAP.
- Consultar espacio utilizado.
- Consultar espacio disponible.
- Verificar si existe espacio suficiente.
- Detectar solicitudes que superen el límite.

La memoria virtual es una simulación académica. No modifica el archivo
de paginación de Windows ni utiliza directamente el disco físico del
equipo.

## 6. Gestor de almacenamiento

### Archivo

```text
src/memory/storage_manager.py
```

### Clase principal

```python
StorageManager
```

### Responsabilidad

`StorageManager` representa el almacenamiento persistente disponible
para AutoOS.

La clase controla:

- Capacidad total.
- Espacio utilizado.
- Espacio libre.

### Capacidad configurada

Por defecto, AutoOS dispone de:

```text
50000 MB de almacenamiento
```

### Operaciones

El gestor permite:

- Reservar espacio.
- Liberar espacio.
- Consultar el espacio utilizado.
- Consultar el espacio disponible.
- Detectar capacidad insuficiente.
- Generar un diccionario serializable.

## 7. Sistema de archivos

### Archivo

```text
src/memory/file_system.py
```

### Clase principal

```python
FileSystem
```

### Responsabilidad

`FileSystem` representa el sistema virtual de archivos de AutoOS.

La estructura inicial es:

```text
/
├── system
├── apps
├── users
├── drivers
├── config
└── logs
```

### Descripción de las carpetas

- `system`: archivos internos del sistema operativo.
- `apps`: aplicaciones utilizadas por el vehículo.
- `users`: archivos asociados con los usuarios.
- `drivers`: controladores de GPS, cámara y sensores.
- `config`: archivos de configuración.
- `logs`: registros generados por AutoOS.

### Operaciones disponibles

#### Crear archivos

```python
create_file(folder, filename, size)
```

Crea un archivo dentro de una carpeta existente.

#### Consultar archivos

```python
file_exists(folder, filename)
```

Comprueba si un archivo existe.

#### Modificar archivos

```python
update_file(folder, filename, new_size)
```

Modifica el tamaño de un archivo existente.

#### Eliminar archivos

```python
delete_file(folder, filename)
```

Elimina un archivo de una carpeta.

#### Listar archivos

```python
list_files(folder)
```

Retorna los archivos almacenados en una carpeta.

#### Consultar estructura

```python
to_dict()
```

Retorna toda la estructura del sistema de archivos.

## 8. Logs de memoria y almacenamiento

### Archivo

```text
src/memory/memory_log.py
```

### Clase principal

```python
MemoryLog
```

### Responsabilidad

`MemoryLog` registra eventos relacionados con el subsistema de memoria
y almacenamiento.

Cada registro contiene:

- Fecha y hora.
- Nivel.
- Mensaje.

### Niveles utilizados

- `INFO`: operación completada correctamente.
- `WARNING`: situación que requiere atención.
- `ERROR`: operación fallida o recurso insuficiente.

### Ejemplos de eventos

```text
[INFO] GPS asignó 300 MB de memoria
[WARNING] Memoria virtual activada
[ERROR] Memoria insuficiente
```

### Operaciones disponibles

La clase permite:

- Agregar registros.
- Consultar registros.
- Eliminar todos los registros.
- Consultar la cantidad total de registros.
- Obtener una representación serializable.

## 9. Pruebas unitarias

Cada componente cuenta con pruebas unitarias implementadas con la
biblioteca estándar `unittest`.

Las pruebas validan:

- Estado inicial.
- Asignación de recursos.
- Liberación de recursos.
- Límites de capacidad.
- Memoria insuficiente.
- Operaciones sobre archivos.
- Registro de eventos.
- Conversión a estructuras serializables.

### Ejecución

Desde la raíz del proyecto:

```powershell
python -m unittest discover tests
```

### Resultado validado

```text
Ran 86 tests
OK
```

Este resultado incluye las pruebas del subsistema de memoria y las
pruebas existentes de los demás componentes de AutoOS.

## 10. Error detectado y corrección aplicada

Durante la ejecución de las pruebas se presentó el siguiente error:

```text
NameError: name 'Process' is not defined
```

### Archivo afectado

```text
src/services/auto_os_service.py
```

### Causa

El método:

```python
register_process(self, process: Process)
```

utilizaba la clase `Process` como anotación de tipo, pero la clase no
había sido importada en el módulo.

### Corrección

Se agregó:

```python
from src.core.process import Process
```

### Validación

Después de aplicar la corrección se ejecutó nuevamente la suite
completa:

```text
Ran 86 tests
OK
```

La corrección permitió importar correctamente los servicios sin
afectar el funcionamiento de los demás componentes.

## 11. Limitaciones actuales

La versión actual corresponde al MVP del proyecto.

Actualmente:

- La memoria se administra de forma global.
- Las asignaciones todavía no se relacionan directamente con un PID.
- La memoria virtual se simula como capacidad SWAP.
- Los archivos se mantienen en memoria durante la ejecución.
- Los datos todavía no se persisten en Supabase.
- El gestor de archivos todavía no descuenta automáticamente el tamaño
  de los archivos del almacenamiento.
- Los logs todavía no se almacenan en una base de datos.

Estas características podrán incorporarse durante las siguientes
entregas.

## 12. Próximas mejoras

Para la evolución de AutoOS se plantea:

- Relacionar asignaciones de memoria con procesos específicos.
- Liberar automáticamente la memoria cuando un proceso termine.
- Conectar el sistema de archivos con `StorageManager`.
- Registrar automáticamente las operaciones.
- Persistir bloques de memoria en Supabase.
- Persistir archivos y logs.
- Mostrar memoria y almacenamiento en el dashboard.
- Crear una simulación visual de bloques de memoria.
- Integrar alertas por memoria insuficiente.
- Implementar escenarios de fallo.

## 13. Conclusión

El subsistema desarrollado proporciona una abstracción funcional de la
memoria RAM, memoria virtual, almacenamiento, sistema de archivos y
logs de AutoOS.

La implementación permite demostrar los conceptos principales exigidos
para un sistema operativo especializado y proporciona una base
modular para su integración con procesos, servicios, Supabase y el
dashboard del vehículo inteligente.