# Diego Villamil, EPIC
# CDMX, 13 de diciembre de 2021

# Este script asume que los archivos se descargaron de la página del INEGI.
# Esta primera parte es altamente manual, y poco automatizable. 

# Además contamos con el layout de columnas que otorgó el Buró de Crédito. 
# "C:/Users/DiegoVillamil/Bineo/Data Arch - Documents/Catalogos/Inegi/Layout PRM Buro HRC.xlsx"

explore <- FALSE


library(readxl)
library(readr)
readRenviron(".Renviron")

filter <- dplyr::filter
env <- Sys.getenv


#%%  Preparación de archivos. 

if (explore) {
  base_layout <- "%s/Layout PRM Buro HRC.xlsx" %>% sprintf(env("ONEDRIVE_INEGI"))
  inegi_0 <- read_excel(base_layout, sheet="Layout PRM", range="B2:F218")
  # inegi_0 <- read_excel("../refs/catalogs/cols_buro_prm.xlsx.lnk")
  cols_2_pre <- inegi_0$Variable %>% str_subset("(mean|std|cv|max)_") %>% 
      str_replace("(mean|std|cv)_", "") %>% unique()
  
  # Son 24 columnas, que tienen prefijo MEAN, STD, CV
  # Pero 22 las que aparecen en la muestra: 
  # Las que no: PLAN_MEN2, PLAN_MOT2
} else {
  # COLS_1 se toman directo a nivel municipio. 
  cols_1 <- c("P_60YMAS", "PCDISC_MOT2", "PCDISC_MEN", "PCLIM_MOT2", "PCLIM_RE_CO", 
    "P3A5_NOA_F", "P12A14NOAF", "P15PRI_INM", "P15SEC_INF", "GRAPROES_F", "GRAPROES_M", 
    "PDESOCUP_F", "PSINDER", "PDER_ISTE", "PDER_ISTEE", "PDER_SEGP", "POTRAS_REL", "PSIN_RELIG", "VPH_PISOTI", "VPH_1CUART", "VPH_2CUART", "VPH_AGUAFV")

  # COLS_2 se toman a nivel (manzana|ageb|localidad) y se agregan a nivel municipio. 
  
  cols_2 <- c("GRAPROES_F", "GRAPROES_M", "P12A14NOAF", "P15PRI_INM", "P15SEC_INF", 
    "P3A5_NOA_F", "PCDISC_MEN", "PCDISC_MOT2", "PCLIM_MOT2", "PCLIM_RE_CO", "PDER_ISTE", 
    "PDER_ISTEE", "PDER_SEGP", "PDESOCUP_F", "POTRAS_REL", "PSINDER", "PSIN_RELIG", 
    "P_60YMAS", "VPH_1CUART", "VPH_2CUART", "VPH_AGUAFV", "VPH_PISOTI")

  # PLAN_MOT2, PLAN_MEN2 se ajustan manualmente debido a cambios en la fuente censal. 
  cols_3 <- c("plan_mot2", "plan_men2")
  
  mutacion_3 <- quos(
      plan_mot2 = PCDISC_MOT2 + PCLIM_MOT2, 
      plan_men2 = PCDISC_MEN + PCLIM_RE_CO)
  
  stats <- list(mean = mean, std = sd, max = max, 
      cv = ~(sd(.x, na.rm=TRUE)/mean(.x, na.rm=TRUE)))
}


#%% Ahora sí:  "Ah-... Correr-el-código."

# I. Download Files ... manually first, and then extract. 

zip_base <- "../data/censo-inegi/raw/2020_datos-abiertos/%d_ageb_mza_urbana_%.2d_cpv2020_csv"

for (ii in seq(32)) {
  the_zip <- sprintf(zip_base, ii, ii) %>% str_c(".zip")
  ext_dir <- sprintf(zip_base, ii, ii)
  if (ext_dir %>% file.exists() %>% not()) unzip(the_zip, exdir = ext_dir)
}

# II. Read by state, and merge dataframe. 

raw_base <- "../data/censo-inegi/raw/2020_datos-abiertos/%d_ageb_mza_urbana_%.2d_cpv2020_csv/ageb_mza_urbana_%.2d_cpv2020/conjunto_de_datos/conjunto_de_datos_ageb_urbana_%.2d_cpv2020.csv"

censo_municipio <- function (ii, obs_base="MZA") {
  # Simplifica procesamiento de lectura:  
  # ID (1..32) -> path_archivo -> Dataframe

  raw_path <- sprintf(raw_base, ii, ii, ii, ii) 
  raw_df   <- read_csv(raw_path, col_types = cols())
  
  mun_df_1 <- raw_df %>% 
    filter(MUN != "000", LOC == "0000") %>% 
    select(ENTIDAD, MUN, one_of(cols_1))

  if (obs_base == "MZA") {
    el_filtro <- quos(MZA != "000")
  } else if (obs_base == "LOC") {
    el_filtro <- quos(LOC != "0000", MZA == "000")
  }

  mun_df_2 <- raw_df %>% 
      mutate_at(cols_2, as.numeric) %>% 
      mutate(!!!mutacion_3) %>% 
      filter(!!!el_filtro) %>% 
      group_by(ENTIDAD, MUN) %>% 
      summarize_at(cols_2 %>% c(cols_3), stats, na.rm=TRUE) %>% 
      set_names(names(.) %>% 
          str_replace("(.*)_((mean|std|cv|max))", "\\2_\\1"))

  mun_df <- full_join(mun_df_1, mun_df_2, by = c("ENTIDAD", "MUN")) %>% 
    mutate(MUN = as.character(MUN)     %>% str_pad(3, "left", "0"),
       ENTIDAD = as.character(ENTIDAD) %>% str_pad(2, "left", "0"))

  return (mun_df)
}


empty_0 <- c("ENTIDAD", "MUN") %>% map_dfc(~tibble(!!.x := character())) 
empty_1 <- c("mean", "std", "cv", "max") %>% 
    cross2(unique(c(cols_1,  cols_2))) %>% 
    map_chr(~str_c(.[1], .[2], sep="_")) %>% 
    map_dfc(~tibble(!!.x := numeric()))

muns_df <- bind_cols(empty_0, empty_1)

for (ii in seq(32)) {
  print("Trabaja la entidad %d de %d" %>% sprintf(ii, 32))
  new_muns <- censo_municipio(ii, "MZA")
  muns_df  <- bind_rows(muns_df, new_muns)
}

#%% Escribir el Dataframe Resultante. 

write_feather(muns_df, "../data/censo-inegi/bronze/censo-municipio.feather")
write_csv(muns_df,     "../data/censo-inegi/bronze/censo-municipio.csv")

