import __main__

def rating_check(map_name:str):
    display_text = "Rating Unavailable"
    if __main__.get_map_data(map_name, __main__.gMap_rating_matrix,"id") != None:
        rating_list =__main__.get_map_rating(str(__main__.get_map_data(map_name, __main__.gMap_rating_matrix,"url"))) 
        text_value = float(rating_list[6].strip("()").split("/")[0])
        
        if(text_value >= 5.0):
            display_text = "⭐⭐⭐⭐⭐"

        elif(text_value >= 4.0):
            display_text = "⭐⭐⭐⭐"

        elif(text_value >= 3.0):
            display_text = "⭐⭐⭐"

        elif(text_value >= 2.0):
            display_text = "⭐⭐"

        elif(text_value >= 1.0):
            display_text = "⭐"
        else:
            display_text += "🛑"
    return display_text