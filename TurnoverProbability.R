library(tidyverse)
library(magrittr)
library(mlr)
library(parallel)
library(parallelMap)

# This file creates an xgboost model for turnover probability on events that 
# advance a play and do not result in an automatic end of possession

# Read in file
df = read_csv("Linhac_df_keyed_20_games.csv", show_col_types = F) %>% 
  mutate(event_index = row_number()-1) # minus one to account for Python indexing

# Deciding which continuous events to filter out

offensive_blocks <- df %>% mutate(temp = teaminpossession == teamid) %>%
  filter(eventname == "block", temp) %>%
  select(event_index) %>% pull() #16

offensive_checks <- df %>% mutate(temp = teaminpossession == teamid) %>%
  filter(eventname == "check", temp) %>%
  select(event_index) %>% pull() #1

defensive_puck_protections <- df %>% 
  mutate(temp = teaminpossession != teamid) %>%
  filter(eventname == "puckprotection", temp) %>%
  select(event_index) %>% pull() #15

defensive_carries <- df %>% mutate(temp = teaminpossession != teamid) %>%
  filter(eventname == "carry", temp) %>%
  select(event_index) %>% pull() #0

defensive_dumpin <- df %>% mutate(temp = teaminpossession != teamid) %>%
  filter(eventname == "dumpin", temp) %>%
  select(event_index) %>% pull() #0

defensive_dumpout <- df %>% mutate(temp = teaminpossession != teamid) %>%
  filter(eventname == "dumpout", temp) %>%
  select(event_index) %>% pull() # 2

defensive_pass <- df %>% mutate(temp = teaminpossession != teamid) %>%
  filter(eventname == "pass", temp) %>%
  select(event_index) %>% pull() # 4

defensive_reception <- df %>% mutate(temp = teaminpossession != teamid) %>%
  filter(eventname == "reception", temp) %>%
  select(event_index) %>% pull() # 0

offensive_controlled_entry_against <- df %>% 
  mutate(temp = teaminpossession == teamid) %>%
  filter(eventname == "controlledentryagainst", temp) %>%
  select(event_index) %>% pull() # 0

defensive_lpr <- df %>% mutate(temp = teaminpossession != teamid) %>%
  filter(eventname == "lpr", temp) %>%
  select(event_index) %>% pull() # 2681

filters <- c(offensive_blocks, offensive_controlled_entry_against, 
             offensive_checks,defensive_carries, defensive_dumpin, 
             defensive_dumpout, defensive_pass, defensive_reception, 
             defensive_lpr, defensive_puck_protections)

automatic_possession_enders <- c("dumpin", "dumpout", "shot", "penalty", 
                                 "penaltydrawn", "offside","icing")
poss_df <- df %>% 
  filter(!is.na(teaminpossession), # remove plays where no team is in possession
         !str_detect(eventname, "^so"), # remove plays from a shootout
         !eventname %in% c("assist", "goal"), # remove events that describe other events
         outcome != "undetermined", #remove events with an undetermined outcome?
  ) %>%
  group_by(gameid, period) %>%
  mutate(
    next_event = lead(eventname,1),
    kept_poss = ifelse(
      teaminpossession == lead(teaminpossession,2)
      , 1,0)) %>%
  ungroup() %>% filter(
    !(next_event  %in% automatic_possession_enders),
    (!eventname %in% automatic_possession_enders),
    !is.na(next_event), #I thought this would fix end of games
    !is.na(kept_poss) # For second last event of the period
  )

# Make a Model for turnover probability
possession_df <- poss_df %>% 
  mutate(
    time_remaining_in_period = 20*60*period - compiledgametime,
    forward = ifelse(playerprimaryposition == "F", 1,0),
    across(c("type", "eventname", "kept_poss"), as.factor)
  ) %>% 
  select(
    period,
    time_remaining_in_period,
    teamskatersonicecount,
    opposingteamskatersonicecount,
    ishomegame,
    scoredifferential,
    xadjcoord,
    yadjcoord,
    forward,
    eventname,
    type,
    kept_poss
  ) 


#load data into train and test
set.seed(2022)
sample <- sample(c(TRUE, FALSE), nrow(possession_df), replace=TRUE, prob=c(0.7,0.3))
train <- possession_df[sample, ]
test <- possession_df[!sample, ] 

#create tasks
traintask <- makeClassifTask(data = as.data.frame(train), target = "kept_poss")
testtask <- makeClassifTask(data = as.data.frame(test), target = "kept_poss")

# do one hot encoding
traintask <- createDummyFeatures(obj = traintask)
testtask <- createDummyFeatures(obj = testtask)

#create learner
lrn <- makeLearner("classif.xgboost", predict.type = "prob")
lrn$par.vals <- list(objective = "binary:logistic", eval_metric = "auc",
                     nrounds = 100L, eta = 0.1)

#set parameter space
params <- makeParamSet(
  makeDiscreteParam("booster", values = c("gbtree", "gblinear")),
  makeIntegerParam("max_depth", lower = 3L, upper = 10L),
  makeNumericParam("min_child_weight", lower = 1L, upper = 10L),
  makeNumericParam("subsample", lower = 0.5, upper = 1),
  makeNumericParam("colsample_bytree", lower = 0.5, upper = 1)
  )

#set resampling strategy
rdesc <- makeResampleDesc("CV", stratify = T, iters = 5L)

#search strategy
ctrl <- makeTuneControlRandom(maxit = 10L)

#set parallel backend
parallelStartSocket(cpus = detectCores())


#parameter tuning
mytune <- tuneParams(learner = lrn, task = traintask, resampling = rdesc,
                     measures = auc, par.set = params, control = ctrl, show.info = T)

mytune$y #0.795

#set hyperparameters
lrn_tune <- setHyperPars(lrn, par.vals = mytune$x)

#train model
xgmodel <- train(learner= lrn_tune, task = traintask)

#predict model
xgpred <- predict(xgmodel, testtask)

#stop parallelism
parallelStop()

roc_test <- roc(xgpred$data$truth, xgpred$data$prob.1, algorithm = 2)
plot(roc_test)
auc(roc_test) #0.7875

# recalculate results on full dataset
fulltask <- makeClassifTask(data = as.data.frame(possession_df), target = "kept_poss")
fulltask <- createDummyFeatures(obj = fulltask)

#train full model
xgmodel_full <- train(learner= lrn_tune, task = fulltask)

#predict model
xgpred_full <- predict(xgmodel_full, fulltask)

# append probabilities to dataset
poss_df %<>% mutate(
  turnover_probability = xgpred_full$data$prob.0
)

# get some averages
poss_df %>% group_by(eventname) %>% 
  summarise(average_turnover_probability = mean(turnover_probability))

# Do final join with original data
df %<>% left_join(
  poss_df %>% select(event_index, kept_poss, turnover_probability), by = "event_index")


