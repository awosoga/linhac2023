library(tidyverse)
library(skimr)
library(magrittr)
df = read_csv("Linhac_df_keyed_20_games.csv", show_col_types = F)
df %<>% mutate(xadjcoord = xadjcoord+100.1126, 
               yadjcoord = yadjcoord+42.5,
               event_index = row_number()) 

library(xgboost)
puck_protections <- df %>% filter(eventname == "puckprotection") %>%
  mutate(deke = ifelse(type == "deke", 1,0),
         forward = ifelse(playerprimaryposition == "F", 1, 0),
         successful = ifelse(outcome == "successful", 1,0),
         #man_advantage = teamskatersonicecount - opposingteamskatersonicecount,
         powerplay = ifelse(manpowersituation == "powerPlay",1,0),
         shorthanded = ifelse(manpowersituation == "shortHanded",1,0),
         #regular = ifelse(manpowersituation == "evenStrength",1,0)
  )

#Get indices for puck protections for joins to full dataset later
puck_protection_index <- select(puck_protections, event_index)

puck_protection_data <- puck_protections %>% select(
  xadjcoord, yadjcoord, scoredifferential, 
  powerplay, shorthanded,compiledgametime,
  #playerid,
  #regular, 
  forward, deke, successful
)

puck_protection_model_features <- names(puck_protection_data %>% select(-successful))

unlabeled_puck_protection_data <- puck_protection_data %>% select(-successful) %>% data.matrix()

labeled_puck_protection_data <- puck_protection_data %>% select(successful) %>% data.matrix()

#make structured format

training_data <- xgb.DMatrix(data = unlabeled_puck_protection_data, 
                             label = labeled_puck_protection_data)


params <- list(
  eval_metric = "auc", #area under the curve, used to evaluate classification problems
  objective = "binary:logistic"
)

set.seed(1502)
puck_protection_train <- xgb.train(
  data = training_data,
  params = params,
  nrounds = 64,
  verbose = 2
)

importance_matrix <- xgb.importance(names(unlabeled_puck_protection_data),
                                    model = puck_protection_train)

importance_matrix %>%
  ggplot(aes(reorder(Feature, Gain), Gain)) +
  geom_col(fill = "#99D9D9", color = "#001628") +
  coord_flip() +
  theme_bw() +
  labs(x = NULL, y = "Importance", caption = "data from LINHAC",
       title = "Puck Protection Retention probabilty feature importance",
       subtitle = "2020-2021 SHL games")

# prediction time
puck_protection_data_predict <- predict(puck_protection_train, unlabeled_puck_protection_data) %>%
  as_tibble() %>%
  rename(retention_probability = value)

puck_protection_data_predict <- bind_cols(puck_protection_index, puck_protection_data_predict)

pass_cv <- xgb.cv(
  data = training_data,
  params = params,
  nthread = 4,
  nfold = 5,
  nrounds = 64,
  verbose = F,
  early_stopping_rounds = 25
)

print(
  paste0("XGBoost test AUC: ",round(max(pass_cv$evaluation_log$test_auc_mean), 4))
)




# using Logistic Regression

set.seed(1)

puck_protections1 <- df %>% filter(eventname == "puckprotection")
#Use 70% of dataset as training set and remaining 30% as testing set
sample <- sample(c(TRUE, FALSE), nrow(puck_protections1), replace=TRUE, prob=c(0.7,0.3))
train <- puck_protections1[sample, ]
test <- puck_protections1[!sample, ] 

train$outcome = ifelse(train$outcome == "successful", 1,0)
test$outcome = ifelse(test$outcome == "successful", 1,0)

#fit logistic regression model
model <- glm(outcome~xadjcoord + yadjcoord + scoredifferential +
  manpowersituation  + compiledgametime + type
               , family="binomial", data=train)

predicted = predict(model, test, type = "response")

library(pROC)
auc(test$outcome, predicted)
summary(model)
