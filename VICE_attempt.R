library(tidyverse)
df = read_csv("Linhac_df_keyed_20_games.csv", show_col_types = F) %>% 
  mutate(xadjcoord = xadjcoord+100.1126, 
         yadjcoord = yadjcoord+42.5,
         event_index = row_number()) 

#Filter out events where neither team is in possession
#Filter out shootout events
filtered_df <- df %>% 
  mutate(xg = replace_na(xg,0)) %>% #set events with an NA value to 0 
filter(!is.na(teaminpossession), !str_detect(eventname, "^so"))

#find the row numbers of the compiled time that are less than or equal to
# 25 seconds past the row number of interest

max_xg_poss <- double() #list to store max xg of team in possession (poss)
max_xg_opp <- double() #list to store max xg of team not in possession (opp)
vice <- double() #list to store vice calculations

for(i in 1:nrow(filtered_df)) {
  time_of_event = filtered_df$compiledgametime[i]
  game = filtered_df$gameid[i]
  team_in_possession = filtered_df$teaminpossession[i]
  time_window = time_of_event + 25
  
  events = which(filtered_df$compiledgametime > time_of_event & 
                   filtered_df$compiledgametime <= time_window & 
                   filtered_df$gameid == game) #which events fall within the time window
  
  #split up events into which ones were for the team in possession and 
  # which ones were for the opposition
  pos_team_events = events[which(filtered_df$teaminpossession[events] == team_in_possession)]
  opp_team_events = events[which(filtered_df$teaminpossession[events] != team_in_possession)]
  
  #find the max xg for events in the next 25 seconds for the team in possession 
  # and add it to the list
  if(length(pos_team_events)>0) {
    temp_poss = max(filtered_df$xg[pos_team_events])
  } else {
    temp_poss = 0
  }
  max_xg_poss = append(max_xg_poss, temp_poss) #R's version of list.append(value)
  
  #find the max xg for events in the next 25 seconds for the other team
  # and add it to the list
  if(length(opp_team_events) >0) {
    temp_opp = max(filtered_df$xg[opp_team_events])
  } else {
    temp_opp = 0
  }
  max_xg_opp = append(max_xg_opp, temp_opp)
  
  #finally, calculate vice and add it to its list
  vice = append(vice, temp_poss - temp_opp) 
}

filtered_df <- cbind(filtered_df, max_xg_poss, max_xg_opp, vice) %>% 
  mutate(
    vice_added = vice - lag(vice,1) #Does vice_n - vice_n-1
  )

filtered_df %>% filter(vice != 0) %>% #should I keep the filter?
  select(eventname, vice_added, vice, max_xg_poss, max_xg_opp)
