library(testit)
# Read: data/codigos-postales/raw/estados_drive/codigos_postales_tabla.txt, 
#       
# Write: refs/catalogos/codigos_drive_(municipios|ciudades|asentamientos).(feather|csv)
# 


checks_codigos <- function (codigos_df) {
  assert("All C_CP are NAs.", 
      all(is.na(codigos_df[["c_CP"]])))
  
  cols_original <- c("d_codigo", "d_asenta", "d_tipo_asenta", "D_mnpio", "d_estado", 
      "d_ciudad", "d_CP", "c_estado", "c_oficina", "c_CP", "c_tipo_asenta", 
      "c_mnpio", "id_asenta_cpcons", "d_zona", "c_cve_ciudad")
  # assert("Columns are the standard ones", 
  #     cols_original == names(codigos_df))

  codigos_1 <- codigos_df %>% 
    select(-c_CP) %>% 
    rename(d_mnpio = D_mnpio)

  return (codigos_1) }



data_dir  <- "../data/codigos-postales/raw/estados_drive"

codigos_0 <- read_delim("codigos_postales_tabla.txt" %>% file.path(data_dir, .), 
    skip=1, delim="|", quote="'", locale=locale(encoding="latin3"), col_types=cols())

codigos_1 <- checks_codigos(codigos_0)


# 32 estados.
estados <- codigos_0 %>% 
  group_by(c_estado, d_estado) %>% 
  summarize(.groups = "drop", 
      min_cp = min(d_codigo), max_cp = max(d_codigo)) 


# 2457 municipios.  
municipios <- codigos_1 %>% 
  group_by(c_estado, c_mnpio, d_mnpio) %>% 
  summarize(.groups = "drop", 
      min_cp = min(d_codigo), max_cp = max(d_codigo)) 


muns_check <-  municipios %>% 
  mutate_at(c("min_cp", "max_cp"), as.numeric) %>% 
  arrange(min_cp) %>% 
  mutate(rank = row_number(), 
      pos_min = lead(min_cp), 
      pre_max = cummax(dplyr::lag(max_cp, default = 0)), 
      separated = (pre_max < min_cp) & (max_cp < pos_min), 
      max_cp  = if_else(separated, lead(min_cp) - 1, max_cp)) %>% 
  mutate_at(c("min_cp", "max_cp"), 
    .f = ~as.character(.) %>% str_pad(5, "left", "0")) %>% 
  select(-c(rank, pos_min, pre_max))


write_feather(municipios, "../refs/catalogs/codigos_drive_municipios.feather")
write_csv(municipios,     "../refs/catalogs/codigos_drive_municipios.csv")

# 664 ciudades
ciudades <- codigos_1 %>% 
  filter(d_ciudad %>% is.na() %>% not()) %>% 
  select(c_estado, c_cve_ciudad, d_ciudad) %>% unique()

write_feather(ciudades, "../refs/catalogs/codigos_drive_ciudades.feather")
write_csv(ciudades, "../refs/catalogs/codigos_drive_ciudades.csv")

# tipos de asentamientos
asentamientos <- codigos_1 %>% 
  filter(d_ciudad %>% is.na() %>% not()) %>% 
  group_by(c_tipo_asenta, d_tipo_asenta) %>% 
  summarize(n_asenta = n(), .groups="keep") %>% 
  arrange(desc(n_asenta))

write_feather(asentamientos, "../refs/catalogs/codigos_drive_asentamientos.feather")
write_csv(asentamientos, "../refs/catalogs/codigos_drive_asentamientos.csv")

codigos_light <- codigos_1 %>% 
  select(d_codigo, d_asenta, d_zona, c_estado, c_mnpio, c_cve_ciudad, c_tipo_asenta)

write_feather(codigos_light, "../refs/catalogs/codigos_drive.feather")
write_csv(codigos_light, "../refs/catalogs/codigos_drive.csv")


# Agregar más checks si acaso. 

