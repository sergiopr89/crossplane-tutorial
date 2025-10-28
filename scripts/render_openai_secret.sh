#!/bin/bash

PROJECT_PATH=$(readlink -f $(dirname $(readlink -f $0))/../)
IAP_PATH=$PROJECT_PATH/manifests/IaP

if [[ ! -z $1 ]]; then
    OPENAI_API_KEY=$1
fi

if [[ -z $OPENAI_API_KEY ]]; then
    echo "Open API Key not provided as OPENAI_API_KEY env var nor argument" 1>&2
    exit 1
fi

export OPENAI_API_KEY_B64=$(echo $OPENAI_API_KEY | base64 -w0)

cd $IAP_PATH
cat secret.yaml.tpl | envsubst > secret.yaml
