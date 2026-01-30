#!/bin/bash

# Script de validación y empaquetado para FLIR Thermal Ad
# Uso: ./validate-and-package.sh

set -e

echo "🔍 FLIR Thermal Ad - Validación y Empaquetado"
echo "=============================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar archivos
check_file() {
    if [ -f "$1" ]; then
        size=$(du -h "$1" | cut -f1)
        echo -e "${GREEN}✓${NC} $1 (${size})"
        return 0
    else
        echo -e "${RED}✗${NC} $1 - NO ENCONTRADO"
        return 1
    fi
}

# 1. Verificar que todos los archivos existan
echo "📁 Verificando archivos del proyecto..."
echo ""

all_files_exist=true

check_file "flir-thermal-ad.html" || all_files_exist=false
check_file "flir-thermal-ad-amp.html" || all_files_exist=false
check_file "normal.webp" || all_files_exist=false
check_file "thermal.webp" || all_files_exist=false
check_file "camara.webp" || all_files_exist=false

echo ""

if [ "$all_files_exist" = false ]; then
    echo -e "${RED}❌ Faltan archivos requeridos${NC}"
    exit 1
fi

# 2. Verificar tamaño total
echo "📊 Verificando tamaño del proyecto..."
echo ""

total_size=$(du -ch flir-thermal-ad-amp.html *.webp 2>/dev/null | grep total | cut -f1)
total_kb=$(du -ck flir-thermal-ad-amp.html *.webp 2>/dev/null | grep total | cut -f1)

echo "Tamaño total: ${total_size} (${total_kb}KB)"

if [ "$total_kb" -gt 150 ]; then
    echo -e "${RED}⚠️  ADVERTENCIA: El proyecto supera los 150KB${NC}"
    echo "   Considera optimizar más las imágenes"
else
    echo -e "${GREEN}✓${NC} Tamaño OK (límite: 150KB)"
fi

echo ""

# 3. Verificar que las imágenes WebP sean válidas
echo "🖼️  Verificando imágenes WebP..."
echo ""

for img in *.webp; do
    if file "$img" | grep -q "WebP"; then
        echo -e "${GREEN}✓${NC} $img es un archivo WebP válido"
    else
        echo -e "${RED}✗${NC} $img NO es un archivo WebP válido"
    fi
done

echo ""

# 4. Verificar referencias en HTML
echo "🔗 Verificando referencias de imágenes en HTML..."
echo ""

check_references() {
    local file=$1
    local errors=0
    
    # Verificar que las referencias a imágenes existan
    for img in normal.webp thermal.webp camara.webp; do
        if grep -q "$img" "$file"; then
            if [ -f "$img" ]; then
                echo -e "${GREEN}✓${NC} $file → $img"
            else
                echo -e "${RED}✗${NC} $file referencia $img pero el archivo no existe"
                errors=$((errors + 1))
            fi
        fi
    done
    
    return $errors
}

check_references "flir-thermal-ad.html"
check_references "flir-thermal-ad-amp.html"

echo ""

# 5. Verificar estructura AMPHTML
echo "⚡ Verificando estructura AMPHTML..."
echo ""

if grep -q "⚡4ads" flir-thermal-ad-amp.html; then
    echo -e "${GREEN}✓${NC} Declaración AMP4ADS presente"
else
    echo -e "${RED}✗${NC} Falta declaración AMP4ADS"
fi

if grep -q "amp4ads-v0.js" flir-thermal-ad-amp.html; then
    echo -e "${GREEN}✓${NC} Script AMP4ADS incluido"
else
    echo -e "${RED}✗${NC} Falta script AMP4ADS"
fi

if grep -q "amp-custom" flir-thermal-ad-amp.html; then
    echo -e "${GREEN}✓${NC} Estilos AMP custom presentes"
else
    echo -e "${RED}✗${NC} Faltan estilos AMP custom"
fi

if grep -q "amp-img" flir-thermal-ad-amp.html; then
    echo -e "${GREEN}✓${NC} Usando amp-img para imágenes"
else
    echo -e "${YELLOW}⚠${NC}  No se encontró amp-img (puede ser intencional)"
fi

echo ""

# 6. Verificar URL del CTA
echo "🔗 Verificando URL del CTA..."
echo ""

cta_url="https://www.colvinycia.cl/collections/camaras-termicas-flir"

if grep -q "$cta_url" flir-thermal-ad.html && grep -q "$cta_url" flir-thermal-ad-amp.html; then
    echo -e "${GREEN}✓${NC} URL del CTA correcta en ambos archivos"
    echo "   → $cta_url"
else
    echo -e "${YELLOW}⚠${NC}  Verifica la URL del CTA manualmente"
fi

echo ""

# 7. Crear paquete ZIP
echo "📦 Creando paquete para distribución..."
echo ""

zip_name="flir-thermal-ad-$(date +%Y%m%d).zip"

zip -q "$zip_name" \
    flir-thermal-ad.html \
    flir-thermal-ad-amp.html \
    normal.webp \
    thermal.webp \
    camara.webp \
    README-FLIR-AD.md 2>/dev/null || true

if [ -f "$zip_name" ]; then
    zip_size=$(du -h "$zip_name" | cut -f1)
    echo -e "${GREEN}✓${NC} Paquete creado: $zip_name (${zip_size})"
else
    echo -e "${YELLOW}⚠${NC}  No se pudo crear el ZIP (zip no disponible)"
fi

echo ""

# 8. Resumen final
echo "=============================================="
echo "✅ VALIDACIÓN COMPLETADA"
echo "=============================================="
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Valida el archivo AMP en:"
echo "   https://validator.ampproject.org/"
echo ""
echo "2. Prueba localmente abriendo:"
echo "   - flir-thermal-ad.html (versión estándar)"
echo "   - flir-thermal-ad-amp.html (versión AMP)"
echo ""
echo "3. Sube a Google Ads usando:"
echo "   - flir-thermal-ad-amp.html"
echo "   - Todas las imágenes .webp"
echo ""
echo "4. Configura el tracking con tu ID de Google Analytics"
echo ""

if [ -f "$zip_name" ]; then
    echo "📦 Paquete listo para distribución: $zip_name"
    echo ""
fi

echo "¡Listo para implementar! 🚀"
