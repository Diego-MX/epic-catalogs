

- Quitar catálogos de Refs y conectar a Datalake.  

- Automatizar variables para `start-fastapi`.  
  - Los _tags_ de la versión se cambian dos veces en el _script_ inciador, y una en el _workflow_. 
  - El `main` tiene otra variación dependiendo de si es local para desbichar, o en el servidor: 
  `uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)`
  `uvicorn.run(app, port=80, host="0.0.0.0")`
  La automatización consiste en codificar esos cambios. 

- Automatizar tags par `test`, los tests se corren de dos formas: 
  - `%run tests/test_{module}.py {ambiente}` si se corren en `ipython` con 
  `module`en `[banks, zipcodes]` las diferentes pruebas, y `ambiente` en 
  `[local-flask, local-fastapi, staging, qa]` algunos ambientes de prueba. 
  - `python -m tests.test_{module} {ambiente}` si se corre desde terminal. 
  La automatización consiste en habilitar el ambiente y 