# Guía de Implementación: Operadores y Conexiones Simplificadas

Hemos actualizado el sistema de estructuras para permitir operaciones aritméticas y facilitar la conexión entre componentes mediante una sintaxis más limpia.

## 1. Nuevos Módulos de Operación
Se han implementado en `core/operationModule.py`:
- **SumModule (`+`)**: Suma dos valores de entrada.
- **MultiplyModule (`x`)**: Multiplica dos valores de entrada.

### Lógica de Sincronización (Anti-Bug)
Los operadores son **síncronos**. No realizarán la operación hasta que:
1. Haya un recurso en la **Entrada 1**.
2. Haya un recurso en la **Entrada 2**.
3. Ambos recursos hayan llegado físicamente al **final de la cinta** (`isReady()`).

Esto evita que se generen números infinitos o resultados erróneos antes de que los materiales lleguen al procesador.

## 2. Sistema de Conexión por Propiedades (Setters)
Ahora puedes conectar estructuras usando el operador de asignación `=`, lo que hace el código mucho más legible.

### Ejemplos de uso:

#### Conectar una Mina a una Cinta
```python
mina.output = cinta_1
```

#### Conectar un Operador (Suma/Multiplicación)
```python
sumador.input1 = cinta_A
sumador.input2 = cinta_B
sumador.output = cinta_resultado
```

#### Conectar al Pozo (Well)
```python
cinta_final.output = pozo
```

## 3. Compatibilidad con Guardado y Carga
Se han añadido métodos de interfaz (`connectInput`, `connectOutput`) para que el sistema de reconexión automática del `GameManager` pueda reconstruir los circuitos al cargar una partida desde el archivo JSON sin intervención manual.

## 4. Cómo crear nuevos Operadores
Para añadir una nueva operación (ej. Resta), simplemente hereda de `OperationModule`:

```python
class SubtractModule(OperationModule):
    def get_symbol(self):
        return "-"
    
    def operate(self, a, b):
        return a - b
```

---
*Nota: Los mensajes de depuración en la consola te indicarán cuándo se realizan las conexiones y las operaciones en tiempo real.*
