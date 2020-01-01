#!/bin/bash
echo "Metadata provider starting"
cd ./MetadataProvider
python3 metadata_provider.py &
cd ..
sleep 5s

echo "Front panel starting"
cd ./DisplaysButtonsEtc
python3 control.py &
cd ..

echo "Webapp starting"
cd ./webapp
export FLASK_APP=app
flask run &
cd ..
