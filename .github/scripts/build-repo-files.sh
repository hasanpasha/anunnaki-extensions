#!/bin/bash

set -e

REPO="repo"
REPO_ZIP="${REPO}/zip"
REPO_ICON="${REPO}/icon"

INDEX="${REPO}/index.json"
INDEX_MIN="${REPO}/index.min.json"

mkdir -p $REPO_ZIP
mkdir -p $REPO_ICON

PKGS=( src/*/* )

for PKGPATH in ${PKGS[@]}; do
    ICON="${PKGPATH}/icon.png"
    
    METADATAFILE="${PKGPATH}/metadata.json"
    NAME=$(jq '.name' < $METADATAFILE | tr -d "\"")
    PKG=$(jq '.pkg' < $METADATAFILE | tr -d "\"")
    LANG=$(jq '.lang' < $METADATAFILE | tr -d "\"")    
    VERSION=$(jq '.version' < $METADATAFILE | tr -d "\"")
    BASE_URL=$(jq '.base_url' < $METADATAFILE | tr -d "\"")
    ID=$(jq '.id' < $METADATAFILE | tr -d "\"")


    OUTPUTNAME="${LANG}_${PKG}_v${VERSION}"
    ZIPOUTPUT="${OUTPUTNAME}.zip"
    ZIPDEST="${REPO_ZIP}/${ZIPOUTPUT}"
    ICONDEST="${REPO_ICON}/${OUTPUTNAME}.png"

    zip -jr $ZIPOUTPUT $PKGPATH > /dev/null
    mv $ZIPOUTPUT $ZIPDEST > /dev/null
    
    cp $ICON $ICONDEST

    # --arg zip $ZIPOUTPUT \
    jq -n \
        --arg name "$NAME" \
        --arg pkg "$PKG" \
        --arg lang "$LANG" \
        --arg version "$VERSION" \
        --argjson id $ID \
        --arg base_url "$BASE_URL" \
        '{name:$name, pkg:$pkg, lang:$lang, version:$version, id:$id, base_url:$base_url}'

done | jq -sr '[.[]]' > $INDEX

# Alternate minified copy
jq -c '.' < $INDEX > $INDEX_MIN