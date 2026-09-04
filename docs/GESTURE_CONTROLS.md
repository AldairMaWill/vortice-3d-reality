# Controles

## Controles actuales (implementados, idénticos al proyecto original)

| Entrada | Efecto |
|---|---|
| Click izquierdo + arrastrar | Rota la cámara alrededor de la escena |
| Click central (rueda) + arrastrar | Traslada la cámara (paneo) |
| Click derecho | Selecciona el siguiente cubo del árbol |
| Rueda del mouse | Zoom in/out |
| Tecla `Espacio` | Selecciona el siguiente cubo |
| Tecla `R` | Resetea rotación, zoom y posición de cámara |
| Tecla `G` | Muestra/oculta el grid del suelo |
| Tecla `A` | Muestra/oculta los ejes X/Y/Z |
| Tecla `E` | Muestra/oculta los bordes de los cubos |
| Flechas ↑↓←→ | Paneo de cámara con teclado |

Toda esta lógica vive en `src/render/camera.py` (estado y matemática)
y se conecta en `src/render/renderer.py` (eventos Qt).

## Controles por gestos (MediaPipe) — NO implementados

El proyecto original que compartiste no incluía tracking de manos ni
gestos: no había ninguna cámara web, ni `mediapipe`, ni lógica de
landmarks en el código. Este documento existe porque la estructura de
carpetas que pediste lo contemplaba, pero es importante no fingir una
funcionalidad que no estaba en tu código fuente.

Si quieres añadir gestos reales en el futuro, el punto de extensión es
`src/vision/tracker.py` (`GestureTracker`). Una integración típica
seguiría este mapeo sugerido (a implementar):

| Gesto propuesto | Acción equivalente en `CameraController` |
|---|---|
| Mano abierta moviéndose | `on_mouse_move` (rotación) |
| Pellizco (pinch) acercando/alejando | `on_wheel` (zoom) |
| Puño cerrado + arrastre | Paneo (`pos_x`, `pos_y`) |
| Índice apuntando + "tap" en el aire | Seleccionar cubo (`tree.select_next_cube`) |

Activa el flag `VORTICE_ENABLE_GESTURES=true` en tu `.env` y añade
`mediapipe` a `requirements.txt` antes de implementar la lógica.
