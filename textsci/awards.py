
#############################
### First in the door award #
#############################
def award_first_in_door(logdf):
    temp = logdf[(logdf.event == "kill")][["round_order","killer", "victim"]].copy()
    temp = temp.reset_index()
    first_in_the_door = temp[temp["index"].isin(temp.groupby("round_order")["index"].min().values)][["killer", "victim"]]
    return first_in_the_door