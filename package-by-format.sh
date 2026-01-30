#!/bin/bash

# Script para empaquetar ads FLIR por formato
# Uso: ./package-by-format.sh

set -e

echo "📦 Empaquetando FLIR Ads por Formato"
echo "====================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fecha para nombres de archivo
DATE=$(date +%Y%m%d)

# Crear directorios temporales
mkdir -p temp/300x250
mkdir -p temp/728x90

echo "📋 Copiando archivos..."
echo ""

# Medium Rectangle (300x250)
echo "  → 300x250 (Medium Rectangle)"
cp flir-thermal-ad.html temp/300x250/
cp flir-thermal-ad-amp.html temp/300x250/
cp flir-ad-lite.html temp/300x250/
cp normal.webp temp/300x250/
cp thermal.webp temp/300x250/
cp camara.webp temp/300x250/

# Leaderboard (728x90)
echo "  → 728x90 (Leaderboard)"
cp flir-leaderboard-728x90.html temp/728x90/
cp flir-leaderboard-728x90-amp.html temp/728x90/
cp normal.webp temp/728x90/
cp thermal.webp temp/728x90/
cp camara.webp temp/728x90/

echo ""
echo "📦 Creando paquetes ZIP..."
echo ""

# Paquete para Google Ads (solo AMP)
echo "  → flir-ads-google-${DATE}.zip (versiones AMP)"
zip -q -j "flir-ads-google-${DATE}.zip" \
    temp/300x250/flir-thermal-ad-amp.html \
    temp/728x90/flir-leaderboard-728x90-amp.html \
    temp/300x250/*.webp

# Paquete completo 300x250
echo "  → flir-300x250-${DATE}.zip"
cd temp/300x250
zip -q "../../flir-300x250-${DATE}.zip" *
cd ../..

# Paquete completo 728x90
echo "  → flir-728x90-${DATE}.zip"
cd temp/728x90
zip -q "../../flir-728x90-${DATE}.zip" *
cd ../..

# Paquete completo (todos los formatos)
echo "  → flir-ads-completo-${DATE}.zip"
cd temp
zip -q -r "../flir-ads-completo-${DATE}.zip" .
cd ..

# Limpiar
rm -rf temp

echo ""
echo "✅ Paquetes creados exitosamente:"
echo ""

ls -lh flir-*-${DATE}.zip | awk '{print "   " $5 "\t" $9}'

echo ""
echo "====================================="
echo "📦 Paquetes Disponibles:"
echo ""
echo "1. flir-ads-google-${DATE}.zip"
echo "   → Solo versiones AMP para Google Ads"
echo "   → Incluye ambos formatos (300x250 y 728x90)"
echo ""
echo "2. flir-300x250-${DATE}.zip"
echo "   → Formato Medium Rectangle completo"
echo "   → HTML5 estándar + AMP + lite"
echo ""
echo "3. flir-728x90-${DATE}.zip"
echo "   → Formato Leaderboard completo"
echo "   → HTML5 estándar + AMP"
echo ""
echo "4. flir-ads-completo-${DATE}.zip"
echo "   → Todos los formatos y versiones"
echo "   → Paquete completo del proyecto"
echo ""
echo "✨ ¡Listo para implementar!"
