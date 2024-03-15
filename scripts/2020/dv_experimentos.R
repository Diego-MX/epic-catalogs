

codigos_reps <- codigos %>% 
  group_by(d_codigo) %>% 
  mutate(n = n()) %>% 
  filter(n > 1) 

codigos_reps_2  <- codigos_reps %>% 
  summarize(edo_eq = all_equal(d_ciudad)) %>% 
  filter(not(edo_eq))