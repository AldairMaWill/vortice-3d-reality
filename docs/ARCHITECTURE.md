# Arquitectura

## Visión general

```
main.py
  └── src.core.orchestrator.PrometeoOctacoreWindow   (QMainWindow)
        ├── src.core.multiprocessing.ProcessSimulator
        ├── src.render.renderer.HolographicWidget    (QGLWidget)
        │     ├── src.render.camera.CameraController
        │     ├── src.core.tree_manager.CubeTreeManager
        │     │     └── src.core.cube_node.CubeNode (N instancias)
        │     ├── src.render.gradients.GradientBackground
        │     └── src.vision.filters.ImageProcessor
        └── QTreeWidget (vista del árbol en la UI)
```

## Flujo de datos

1. `CubeTreeManager` es la única fuente de verdad del árbol de cubos
   (posiciones, jerarquía, selección). Tanto el `HolographicWidget`
   (para renderizar) como `PrometeoOctacoreWindow` (para los botones y
   el `QTreeWidget`) leen y escriben sobre la misma instancia.
2. `CameraController` mantiene el estado de la cámara (rotación, zoom,
   paneo) y expone señales Qt (`rotationChanged`, `zoomChanged`,
   `positionChanged`) que el widget reenvía tal cual hacía el monolito
   original.
3. `ImageProcessor` (en `vision/filters.py`) aplica los filtros OpenCV
   antes de que una imagen se pegue a una cara de un cubo.
4. `GradientBackground` genera arrays NumPy que luego se suben como
   textura OpenGL de fondo.

## "Procesamiento paralelo" (las 8 barras de cerebros)

El monolito original nunca lanzaba procesos ni hilos reales: un
`QTimer` de 100ms incrementaba 8 barras de progreso con valores
aleatorios, puramente decorativo. `ProcessSimulator`
(`src/core/multiprocessing.py`) reproduce exactamente ese cálculo. Si
en el futuro quieres reemplazarlo por un `multiprocessing.Pool` real
(por ejemplo, para paralelizar el filtrado de imágenes entre varios
procesos), ese es el único archivo que necesitas tocar — el resto de
la app no depende de si el número viene de un proceso real o simulado.

## Tracking de gestos

No implementado en el original. Ver `docs/GESTURE_CONTROLS.md` y
`src/vision/tracker.py` para el punto de extensión.
