

# Introducción

Este repositorio contiene código para hacer uso de algunos catálogos de datos.  

- Población de manzanas.  
- Asentamientos y códigos postales.  
- Bancos, por CLABE y bines de números de cuenta.  

# Población de manzanas  

- La información censal la proporciona el INEGI en [este sitio][censo-inegi].  
    Por el diseño de la página, no es fácil programar su descarga.  

1. En la sección de `Datos Abiertos`, ir a `[Descargar todos los archivos]` y después
dar click en `[Descargar]`.  
    a) Guardar el archivo como `data/censo-inegi/setup/2020-Datos-Abiertos.zip` 
    (66 archivo ~ 320 Mb).   
    b) Descomprimir y ejecutar `DescargaMasivaApp.exe`.   
    c) Guardar el resultante en `data/censo-inegi/raw/2020/microdatos`   

2. El resto del procesamiento se ejecuta en el _script_ `1b_download-censo.R`.   



# Autenticación y recursos

Para hacer la lectura de archivos en el Datalake (Storage Container) hay varios métodos.  
- Obtener el _connection string_ y guardarlo en una variable de ambiente.  
    Es muy rudimentario, sólo para realizar pedidos rápidos.  

- Crear un Servicio principado en el _Active Directory_.  Por ejemplo: `prod_catalogs_app`.  
    Sirve para cuestiones de desarrollo, y staging.  
    
- Dar permisos al app para los servicios o recursos.  
    E.g. Acceder al _Storage_ de Lake Hylia.  


# Runbook  

Los recursos que se necesitan para esta webapp son:   
- Excel (fuente oficial malamente, favor de migrar a SQL)     

- Base de datos SQL (por definir)   

- _Webapp_: `wap-prod-catalogs-{ENV}`  
    - `zipcode-neighborhoods/{zipcode}` GET  
    - `national-banks` GET  
    - `national-banks/parse-clabe/{clabe}` GET  
    - `national-banks/card-number/{number}` GET  
    - `national-banks/acquiring/{acq_code}` GET   
    Variables: 
    - `ENV_TYPE = dev,qas,stg,prd,drp`
    - `SERVER_TYPE = wap`  
    Especificaciones [aquí][docs]  


- Contenedor: 
    - _Registry_: `ProdCatalogsRegistry`  
    - Instancia/Repositorio: `prod-catalogs-webapp`  

- Ambiente de Github:  (`dev`, `qas`, `stg`, `prd`, `drp`)  
    - `ACR_HOST`  
    - `ACR_USER`  
    - `ACR_PASS`  
    - `WAP_PUBLISH`  





## _Links_ de referencia: 

- [Autenticar en Azure SDK][azure-sdk]. 

[azure-sdk]: https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate
[local-env]: https://docs.microsoft.com/en-us/azure/developer/python/configure-local-development-environment?tabs=cmd
[censo-inegi]: https://www.inegi.org.mx/programas/ccpv/2020/default.html#DatosAbiertos
[docs]: https://apim-crosschannel-tech-dev.azure-api.net/data/docs/v1/catalogs
