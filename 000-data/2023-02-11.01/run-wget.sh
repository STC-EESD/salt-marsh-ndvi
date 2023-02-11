#!/bin/bash

### 2021 Census – Boundary files
### https://www.census.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21

ZIP_URLs=( \
    # Type: Digital Boundary Files (DBF), Administrative boundaries: Provinces/territories, Format: Shapefile (.shp)
    "https://www.census.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/files-fichiers/lpr_000a21a_e.zip"
    )

### ~~~~~~~~~~ ###
for tempurl in "${ZIP_URLs[@]}"
do

    echo;echo downloading: ${tempurl}
    wget ${tempurl}
    sleep 5

    tempstem=`basename ${tempurl} .zip`
    tempzip=${tempstem}.zip

    echo unzipping: ${tempzip}
    unzip ${tempzip} -d ${tempstem}

done
echo

### ~~~~~~~~~~ ###
echo; echo done; echo
