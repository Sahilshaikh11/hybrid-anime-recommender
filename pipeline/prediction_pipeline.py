from config.paths_config import *
from utils.helpers import *

def hybrid_recommendation(user_id, user_weight=0.4, content_weight=0.6):
    
    #### User Recommendation
    
    similar_users = find_similar_users(int(user_id), USER_WEIGHTS_PATH, USER2USER_ENCODED, USER2USER_DECODED)
    user_pref = get_user_preferences(int(user_id), RATING_DF, DF)
    user_recommended_animes = get_user_recommendations(similar_users,user_pref, DF, SYNOPSIS_DF, RATING_DF)

    user_recommended_animes_list = user_recommended_animes["anime_names"].tolist()
    # print(f"User {user_id} recommended animes: {user_recommended_animes_list}")
    
    ###### Content Recommendation

    content_recommended_animes = []

    for anime in user_recommended_animes_list:
        similar_animes = find_similar_animes(anime,ANIME_WEIGHTS_PATH,ANIME2ANIME_ENCODED,ANIME2ANIME_DECODED,DF,SYNOPSIS_DF,n=2)

        if similar_animes is not None and not similar_animes.empty:
            content_recommended_animes.extend(similar_animes["name"].tolist())
        else:
            print(f"No similar animes found for {anime}.")  

    combined_socres = {}

    for anime in user_recommended_animes_list:
        combined_socres[anime] = combined_socres.get(anime, 0) + user_weight

    for anime in content_recommended_animes:
        combined_socres[anime] = combined_socres.get(anime, 0) + content_weight

    sorted_animes = sorted(combined_socres.items(), key=lambda x: x[1], reverse=True)

    return [anime for anime, score in sorted_animes[:10]]

