library(feather)
library(testit)
library(tidyverse)
filter <- dplyr::filter


the_year <- year(today())

raw_zip <- "data/codigos-postales/raw/{the_year}_CPdescargatxt.zip" %>% glue()
raw_unzip <- "data/codigos-postales/raw/1-unzip/{the_year}" %>% glue() 
raw_data <- "data/codigos-postales/raw/1-unzip/{the_year}/CPdescarga.txt" %>% glue()

brz_template <- "refs/catalogs/codigos_drive{tabla}.{ext}"


# 0. Descarga manual: 
#   https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
#   > data / codigos-postales / raw / [Año]_CPdescargatxt.zip

# 1. Descomprime y extrae. 

# 2. Validar y Leer

# 3. Separar tablas: estados, ciudades, municipios, asentamientos

# 4. Escribir tablas. 


#####

validar_y_leer <- function (archivo) {
    cols_original <- c("d_codigo", "d_asenta", "d_tipo_asenta", "D_mnpio", "d_estado", 
        "d_ciudad", "d_CP", "c_estado", "c_oficina", "c_CP", "c_tipo_asenta", 
        "c_mnpio", "id_asenta_cpcons", "d_zona", "c_cve_ciudad")
    
    codigos_0 <- read_delim(archivo, delim="|", skip=1, 
        locale=locale(encoding="latin3"), col_types=cols(), quote="'")

    codigos_1 <- codigos_0 %>% 
        select(-c_CP) %>% 
        rename(d_mnpio = D_mnpio)
    
    assert("All C_CP are NAs.", all(is.na(codigos_0[["c_CP"]])))
  
    assert("Columns are the standard ones", cols_original == names(codigos_0))

    return (codigos_1) }


validar_muns <- function (muns_0) {
    muns_1 <- muns_0 %>% 
        ungroup() %>% 
        mutate_at(c("min_cp", "max_cp"), as.numeric) %>% 
        arrange(min_cp) %>% 
        mutate(rank = row_number(), 
            pos_min = lead(min_cp), 
            pre_max = cummax(lag(max_cp, default = 0)), 
            separated = (pre_max < min_cp) & (max_cp < pos_min), 
            max_cp = if_else(separated, lead(min_cp) - 1, max_cp)) %>% 
        mutate_at(c("min_cp", "max_cp"), 
            .f = ~as.character(.) %>% str_pad(5, "left", "0")) %>% 
        select(-c(rank, pos_min, pre_max))

    return (muns_1) }


extraer_grupos <- function (codigos, group_by) {
    el_grupo <- switch(group_by,

    estados = { codigos %>% 
        group_by(c_estado, d_estado) %>% 
        summarize(min_cp = min(d_codigo), max_cp = max(d_codigo)) %>% 
        ungroup()},

    ciudades = { codigos %>% 
        filter(d_ciudad %>% is.na() %>% not()) %>% 
        select(c_estado, c_cve_ciudad, d_ciudad) %>% 
        ungroup() %>% unique()}, 

    municipios = { codigos %>% 
        group_by(c_estado, c_mnpio, d_mnpio) %>% 
        summarize(min_cp = min(d_codigo), max_cp = max(d_codigo)) %>% 
        ungroup() }, 
    
    asentamientos = { codigos %>% 
        filter(d_ciudad %>% is.na() %>% not()) %>% 
        group_by(c_tipo_asenta, d_tipo_asenta) %>% 
        summarize(n_asenta = n()) %>% 
        ungroup() %>% 
        arrange(desc(n_asenta)) } )

    return (el_grupo)}


#####

# 1. Descomprimir
unzip(raw_zip, exdir=raw_unzip)

# 2. Validar y Leer
codigos <- validar_y_leer(raw_data)


# 3. Separar tablas
codigos_light <- codigos %>% 
  select(d_codigo, d_asenta, d_zona, c_estado, c_mnpio, c_cve_ciudad, c_tipo_asenta)

estados <- extraer_grupos(codigos, "estados")
ciudades <- extraer_grupos(codigos, "ciudades")
municipios <- extraer_grupos(codigos, "municipios")
asentamientos <- extraer_grupos(codigos, "asentamientos")


# 4. Escribir tablas
write_csv(codigos_light, brz_template %>% glue(tabla="", ext="csv"))
write_csv(ciudades, brz_template %>% glue(tabla="_ciudades", ext="csv"))
write_csv(municipios, brz_template %>% glue(tabla="_municipios", ext="csv"))
write_csv(asentamientos, brz_template %>% glue(tabla="_asentamientos", ext="csv"))

write_feather(codigos_light, brz_template %>% glue(tabla="", ext="feather"))
write_feather(ciudades, brz_template %>% glue(tabla="_ciudades", ext="feather"))
write_feather(municipios, brz_template %>% glue(tabla="_municipios", ext="feather"))
write_feather(asentamientos, brz_template %>% glue(tabla="_asentamientos", ext="feather"))

