import os
import shutil
import zipfile
from PIL import Image # Requiere: pip install Pillow

# --- CONFIGURACIÓN ---

SOURCE_DIR = "source_images"
# Cambiamos el nombre de la carpeta de salida para evitar confusiones
OUTPUT_DIR = "output_banners_png_standard"

# Archivos fuente (siguen siendo tus WebP de alta resolución)
SRC_NORMAL = os.path.join(SOURCE_DIR, "normal_highres.webp")
SRC_THERMAL = os.path.join(SOURCE_DIR, "thermal_highres.webp")
SRC_CAMERA = os.path.join(SOURCE_DIR, "camara.webp")

# Configuraciones de tamaño (320x480 y 480x320)
BANNER_CONFIGS = [
    {"w": 320, "h": 480, "cw": 180, "ch": 135, "sw": 108, "sh": 78}, # Portrait
    {"w": 480, "h": 320, "cw": 180, "ch": 135, "sw": 108, "sh": 78}, # Landscape
]

# --- PLANTILLA HTML ESTÁNDAR (Regresamos a clickTag y ahora usa .png) ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="ad.size" content="width=__WIDTH__,height=__HEIGHT__">
    <title>Visor Térmico FLIR</title>
    
    <!-- VOLVEMOS AL CLICKTAG ESTÁNDAR -->
    <script type="text/javascript">
        var clickTag = "https://www.colvinycia.cl"; 
    </script>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            width: __WIDTH__px; height: __HEIGHT__px;
            margin: 0; padding: 0; overflow: hidden;
            background: #000;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex; justify-content: center; align-items: center;
        }
        #ad-container {
            position: relative;
            width: __WIDTH__px; height: __HEIGHT__px;
            overflow: hidden; background: #000;
            cursor: none;
            touch-action: none; -webkit-touch-callout: none; -webkit-user-select: none; user-select: none;
        }
        .layer {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; pointer-events: none; will-change: opacity;
        }
        #normal-layer { z-index: 1; }
        #thermal-layer {
            z-index: 2; opacity: 0; transition: opacity 0.2s ease-out;
            -webkit-mask-image: linear-gradient(black, black); mask-image: linear-gradient(black, black);
            -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
            -webkit-mask-position: -1000px -1000px; mask-position: -1000px -1000px;
        }
        #thermal-layer.active { opacity: 1; }
        #custom-cursor {
            position: absolute; top: 50%; left: 50%;
            width: __CURSOR_W__px; height: __CURSOR_H__px;
            transform: translate(-50%, -50%); z-index: 10; pointer-events: none;
            /* AHORA APUNTA AL ARCHIVO PNG */
            background-image: url('./camara.png'); 
            background-size: contain; background-position: center; background-repeat: no-repeat;
            opacity: 0; transition: opacity 0.2s ease-out; will-change: top, left;
        }
        #custom-cursor.active { opacity: 1; }
        #overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 20;
            pointer-events: none; display: flex; flex-direction: column; justify-content: flex-end; padding: 15px;
        }
        #cta-button {
            align-self: center; background: rgba(0, 0, 0, 0.8); color: #fff;
            padding: 10px 20px; border-radius: 4px; font-size: 13px; font-weight: 700;
            text-transform: uppercase; border: 1px solid rgba(255, 255, 255, 0.3);
            pointer-events: auto; cursor: pointer; transition: all 0.3s ease;
        }
        #cta-button:hover { background: #c51618; border-color: #c51618; }
    </style>
</head>
<body>
    <div id="ad-container">
        <!-- AHORA APUNTAN A LOS ARCHIVOS PNG -->
        <img src="./normal.png" alt="" class="layer" id="normal-layer">
        <img src="./thermal.png" alt="" class="layer" id="thermal-layer">
        <div id="custom-cursor"></div>
        <div id="overlay">
            <div id="cta-button">Ver Cámaras FLIR</div>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const container = document.getElementById('ad-container');
            const thermalLayer = document.getElementById('thermal-layer');
            const customCursor = document.getElementById('custom-cursor');
            const ctaButton = document.getElementById('cta-button');
            
            const screenW = __SCREEN_W__;
            const screenH = __SCREEN_H__;
            const offsetX = 0; 
            const offsetY = 2;

            const maskSizeValue = `${screenW}px ${screenH}px`;
            thermalLayer.style.webkitMaskSize = maskSizeValue;
            thermalLayer.style.maskSize = maskSizeValue;

            let mouseX = 0, mouseY = 0;
            let isInteracting = false;
            let animationFrameId = null;

            function render() {
                if (!isInteracting) return;
                customCursor.style.left = mouseX + 'px';
                customCursor.style.top = mouseY + 'px';

                const maskPosX = (mouseX - (screenW / 2)) + offsetX;
                const maskPosY = (mouseY - (screenH / 2)) + offsetY;
                const maskPosValue = `${maskPosX}px ${maskPosY}px`;

                thermalLayer.style.webkitMaskPosition = maskPosValue;
                thermalLayer.style.maskPosition = maskPosValue;
                animationFrameId = requestAnimationFrame(render);
            }

            function updatePosition(x, y) {
                mouseX = x; mouseY = y;
                if (!isInteracting) {
                    isInteracting = true;
                    thermalLayer.classList.add('active');
                    customCursor.classList.add('active');
                    if (animationFrameId === null) animationFrameId = requestAnimationFrame(render);
                }
            }

            function stopInteraction() {
                isInteracting = false;
                thermalLayer.classList.remove('active');
                customCursor.classList.remove('active');
                if (animationFrameId !== null) {
                    cancelAnimationFrame(animationFrameId);
                    animationFrameId = null;
                }
            }

            container.addEventListener('mousemove', (e) => {
                const rect = container.getBoundingClientRect();
                updatePosition(e.clientX - rect.left, e.clientY - rect.top);
            });
            container.addEventListener('mouseleave', stopInteraction);
            container.addEventListener('touchstart', (e) => {
                const rect = container.getBoundingClientRect();
                updatePosition(e.touches[0].clientX - rect.left, e.touches[0].clientY - rect.top);
            }, { passive: true });
            container.addEventListener('touchmove', (e) => {
                const rect = container.getBoundingClientRect();
                updatePosition(e.touches[0].clientX - rect.left, e.touches[0].clientY - rect.top);
            }, { passive: true });
            container.addEventListener('touchend', stopInteraction);
            container.addEventListener('touchcancel', stopInteraction);
            
            // VOLVEMOS AL CLICKTAG ESTÁNDAR
            ctaButton.addEventListener('click', () => window.open(window.clickTag, '_blank'));
        });
    </script>
</body>
</html>
"""

# --- FUNCIONES AUXILIARES ACTUALIZADAS PARA PNG ---

def resize_and_convert_to_png(input_path, output_path, target_size):
    """Redimensiona WebP y guarda como PNG."""
    try:
        with Image.open(input_path) as img:
            # Asegurar modo RGBA para transparencia si es necesario
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
            # Guardar como PNG (sin pérdida, no necesita parámetro quality)
            resized_img.save(output_path, 'PNG') 
    except Exception as e:
        print(f"Error procesando {input_path}: {e}")
        exit()

def convert_camera_to_png(input_path, output_path):
    """Solo convierte la cámara WebP a PNG manteniendo transparencia."""
    try:
        with Image.open(input_path) as img:
             if img.mode != 'RGBA':
                img = img.convert('RGBA')
             img.save(output_path, 'PNG')
    except Exception as e:
        print(f"Error convirtiendo cámara {input_path}: {e}")
        exit()

def create_zip(source_dir, output_zip_path):
    try:
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.basename(file_path))
    except Exception as e:
        print(f"Error creando ZIP {output_zip_path}: {e}")
        exit()

# --- PROCESO PRINCIPAL ---

def main():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Falta '{SOURCE_DIR}'.")
        return
    
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    print(f"Generando banners PNG estándar en '{OUTPUT_DIR}'...")

    for config in BANNER_CONFIGS:
        width = config["w"]
        height = config["h"]
        size_name = f"{width}x{height}"
        print(f"Procesando: {size_name}...")

        temp_dir = os.path.join(OUTPUT_DIR, f"temp_{size_name}")
        os.makedirs(temp_dir, exist_ok=True)

        # A. Procesar Imágenes (Convertir a PNG)
        # Notar que los archivos de salida ahora terminan en .png
        resize_and_convert_to_png(SRC_NORMAL, os.path.join(temp_dir, "normal.png"), (width, height))
        resize_and_convert_to_png(SRC_THERMAL, os.path.join(temp_dir, "thermal.png"), (width, height))
        convert_camera_to_png(SRC_CAMERA, os.path.join(temp_dir, "camara.png"))

        # B. Generar HTML
        html_content = HTML_TEMPLATE.replace("__WIDTH__", str(width)) \
                                    .replace("__HEIGHT__", str(height)) \
                                    .replace("__CURSOR_W__", str(config["cw"])) \
                                    .replace("__CURSOR_H__", str(config["ch"])) \
                                    .replace("__SCREEN_W__", str(config["sw"])) \
                                    .replace("__SCREEN_H__", str(config["sh"]))
        
        with open(os.path.join(temp_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        # C. Crear ZIP final
        zip_name = f"FLIR_Standard_PNG_{size_name}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_name)
        create_zip(temp_dir, zip_path)
        print(f"  -> Generado: {zip_name}")

        shutil.rmtree(temp_dir)

    print("\n¡Proceso completado! Revisa la carpeta de salida.")

if __name__ == "__main__":
    main()