
# Iniciar la app con FastAPI, antes Flask.
python -m src.app.start
python ./src/app/start.py


uvicorn start:app --port 80 --host 0.0.0.0

# Para el Docker
docker build --build-arg SERVER_TYPE=docker --build-arg ENV_TYPE=dev -f .\dockerfile.ci -t prod-catalogs-webapp:latest .
docker run -p 80:80 --rm prod-catalogs-webapp
docker ps -a 
PS1> ... <la_instancia>

docker stop {la_instancia}


# Para el Testing 
python -m tests.test_rfc

# Para correr R en Radian
radian --r-binary=$home/AppData/Local/R/R-4.1.2/bin/R.exe

&"$home\AppData\local\R\R-4.1.2\bin\RScript.exe" .\1b_download-censo.R


# Activar .venv
./.venv/Scripts/activate.ps1
python -m pip install -U {un-paquete}
deactivate .venv


