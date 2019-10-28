#!/bin/bash -e

profs=(aqua chakra default disco drain freeway plain rainbow-split roulette disable)
fn="./.msi-rgb"
touch $fn
prof=$(cat $fn)
if [ -z "$prof" ]; then
    echo "0" > $fn
    vl=0
else
    nv=$(($((prof+1)) > 9 ? 0 : $((prof+1))))
    echo $nv > $fn
    vl=$nv
fi
if [ "${profs[$vl]}" = "disable" ]; then
    msi-perkeyrgb -m GS65 -d
else
    msi-perkeyrgb -m GS65 -p "${profs[$vl]}"
fi

exit 0