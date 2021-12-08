# MARCO GEOESTADÍSTICO:
# https://www.inegi.org.mx/temas/mg/#

# CORREOS DE MEXICO 
# https://datos.gob.mx/busca/dataset/ubicacion-de-codigos-postales-en-mexico
# https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/imagenes/btnDescarga.jpg
#
# 7-oct-21| https://datos.gob.mx/busca/dataset/informacion-geografica-de-los-codigos-postales-asentamientos-humanos-y-colonias-de-cada-estado- 
#

# (Google Drive)
# https://drive.google.com/u/0/open?id=0B-4W2dww7ELNQlRSTGVmT295REU

# US-NOAA
# https://www.weather.gov/gis/USStates


url_fuentes <- list(
  drive = "https://drive.google.com/u/0/uc?export=download&confirm=Q1Ks&id=0B-4W2dww7ELNQlRSTGVmT295REU",
  gobmx = c("https://www.correosdemexico.gob.mx/datosabiertos/poligonos/cp_%s.zip", 
            "http://www.correosdemexico.gob.mx/datosabiertos/cp/cpdescarga.txt"), 
  marco_geo = "https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/889463807469/889463807469_s.zip"
) 


descarga_y_descomprime <- function (fuente, directorio) {
  estados <- read_csv("../refs/catalogs/estados_claves.csv", col_types=cols())
  switch(fuente, 

  drive = { # data/codigos-postales/raw
    dir_1 <- file.path(directorio, "estados_drive")
    zip_1 <- file.path(directorio, "códigos_postales.zip")
    
    if (dir.exists(dir_1) %>% not()) dir.create(dir_1, recursive=TRUE)
    
    if (zip_1 %>% file.exists() %>% not()) {
      download.file(url_fuentes[["drive"]], zip_1, mode="wb") }
    unzip(zip_1, exdir=directorio)
    
    edo_abr <- estados[["drive"]][3]
    for (edo_abr in estados[["drive"]]) {
      edo_zip <- sprintf("CP_%s.zip", edo_abr) %>% 
        file.path(directorio, "c¢digos_postales", "shapes_cps", .)
      edo_unz <- sprintf("CP_%s", edo_abr) %>% file.path(dir_1, .)
      if (edo_unz %>% file.exists() %>% not()) unzip(edo_zip, exdir=edo_unz)
    }
    tabla_old <- file.path(directorio, "c¢digos_postales", 
        "Tabla de C¢digos Postales y asentamientos humanos.txt")
    tabla_new <- file.path(dir_1, "codigos_postales_tabla.txt")
    file.copy(tabla_old, tabla_new)
  }, 

  gobmx = { # data/codigos-postales/raw
    for (edo in estados[["gobmx"]]) {
      dir_1 <- file.path(directorio, "estados_gobmx")
      if (dir.exists(dir_1) %>% not()) dir.create(dir_1, recursive=TRUE)
      
      edo_url = sprintf(url_fuentes[["gobmx"]][0], edo)
      edo_zip = sprintf("cp_%s.zip", edo) %>% file.path(dir_1, .)
      edo_unz = sprintf("cp_%s", edo) %>% file.path(dir_1, .)
      
      download.file(edo_url, edo_file, cacheOK=FALSE) 
      unzip(edo_file, exdir=edo_unz, overwrite=TRUE)
      file.remove(edo_file)
    }
    tabla_file <- file.path(dir_1, "codigos_postales_tabla.txt")
    download.file(url_fuentes[["gobmx"]][1], tabla_file)
  }, 

  marco_geo = { # data/codigos-postales/raw
    dir_1 <- file.path(directorio, "estados_marcogeo")
    zip_1 <- file.path(directorio, "estados_marcogeo.zip")
    
    if (dir.exists(dir_1) %>% not()) dir.create(dir_1, recursive=TRUE)
    
    if (zip_1 %>% file.exists() %>% not()) {
      download.file(url_fuentes[["marco_geo"]], zip_1, mode="wb")}
    
    unzip(zip_1, exdir=dir_1)
  })
}


# Action!  ----------------------------------------------------------------

directorio <- "../data/codigos-postales/raw"
dir_inegi  <- "../data/marco-geo/raw"

descarga_y_descomprime(dir_codigos, "drive")
descarga_y_descomprime(dir_codigos, "gobmx")
descarga_y_descomprime(dir_inegi,   "marco_geo")
