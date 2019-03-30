#!/bin/bash -e
# Randomly sets a new preset
# 1st arg is model name. 2nd argument -d to disable.

if [ "$2" = "-d" ]
then
  echo "rgb disabled"
  msi-perkeyrgb -m $1 $2
  exit 0
fi

presets=(
    aqua
    chakra
    default
    disco
    drain
    freeway
    plain
    rainbow-split
    roulette
)

selection=${presets[(( RANDOM % ${#presets[@]}+1 ))]}
