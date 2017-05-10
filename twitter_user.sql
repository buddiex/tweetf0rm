create or replace view twitter_user as
select 
    j.jd.id_str twt_user_id,
    j.jd.screen_name twt_handle,
    j.jd.name user_name,
    j.jd.created_at day_joined,
    j.jd.statuses_count total_tweets_count ,
    j.jd.friends_count following_count ,
    j.jd.followers_count  ,
    j.jd.favourites_count  ,
    j.jd.listed_count,
    j.jd.description,
    j.jd.entities.description.urls.expanded_url,
    j.jd.protected ,
    j.jd.location ,
    j.jd.geo_enabled,
    j.jd.lang ,
    j.jd.verified ,
    j.jd.utc_offset ,
    j.jd.url 
from twitter_followers j;
