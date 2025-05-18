#!/bin/bash

# Színes szöveg
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigáljunk a script könyvtárába
cd "$(dirname "$0")"

# Ellenőrizzük, hogy fut-e már a szerver
if lsof -i :5051 | grep LISTEN > /dev/null; then
    echo -e "${RED}A szerver már fut a 5051-es porton!${NC}"
    echo -e "${BLUE}Nyisd meg a böngészőben: http://127.0.0.1:5051${NC}"
    echo -e "${GREEN}Nyomj ENTER-t a kilépéshez...${NC}"
    read
    exit 1
fi

# Indítsuk el a szervert
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Indítom a Teszt Szervert...${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Nyisd meg a böngészőben:${NC}"
echo -e "${BLUE}http://127.0.0.1:5051${NC}"
echo -e "${RED}A szerver leállításához zárd be ezt az ablakot (Ctrl+C)${NC}"
echo -e "${BLUE}========================================${NC}"

# Indítsuk el a Python szervert
python3 app.py

# Ha a szerver leáll, várjunk egy kicsit
echo -e "${RED}A szerver leállt.${NC}"
echo -e "${GREEN}Nyomj ENTER-t a kilépéshez...${NC}"
read 