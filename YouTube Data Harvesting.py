from googleapiclient.discovery import build
import pandas as pd
import sqlite3
import streamlit as st
from streamlit_option_menu import option_menu

# API connection
def api_connect():
    api_key = 'API KEY'
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=api_key)
    return youtube

youtube = api_connect()

# Get channel information
def get_channel_info(channel_id):
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id)
    response = request.execute()
    for i in response['items']:
        data = dict(channel_name=i['snippet']['title'],
                    channel_id=i["id"],
                    subscribers=i['statistics'].get('subscriberCount'),
                    views=i["statistics"].get('viewCount'),
                    total_videos=i['statistics'].get('videoCount'),
                    channel_description=i["snippet"]["description"],
                    playlist_id=i["contentDetails"]["relatedPlaylists"]["uploads"])
        return data

# Get video IDs
def get_videos_ids(channel_id):
    video_ids = []
    response = youtube.channels().list(id=channel_id,
                                       part='contentDetails').execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    while True:
        response1 = youtube.playlistItems().list(part='snippet',
                                                 playlistId=playlist_id,
                                                 maxResults=50,
                                                 pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = response1.get('nextPageToken')
        if next_page_token is None:
            break
    return video_ids


# Get video information
def get_video_info(video_ids):
    video_data = []
    for video_id in video_ids:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()
        for item in response["items"]:
            data = dict(channel_name=item['snippet']['channelTitle'],
                        channel_id=item['snippet']['channelId'],
                        video_id=item['id'],
                        title=item['snippet']['title'],
                        tags=item['snippet'].get('tags'),
                        thumbnail=item['snippet']['thumbnails']['default']['url'],
                        description=item['snippet'].get('description'),
                        published_date=pd.to_datetime(item["snippet"]["publishedAt"]),
                        duration=item['contentDetails']['duration'],
                        views=item['statistics'].get('viewCount'),
                        comments=item['statistics'].get('commentCount'),
                        likes=item['statistics'].get('likeCount'),
                        dislikes=item['statistics'].get('dislikeCount'),
                        favorite_count=item['statistics'].get('favoriteCount'),
                        definition=item['contentDetails']['definition'],
                        caption_status=item['contentDetails']['definition'],
                        )
            video_data.append(data)
    return video_data

# Get comment information
def get_comment_info(video_ids):
    comment_data = []
    try:
        for video_id in video_ids:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response = request.execute()
            for item in response['items']:
                data = dict(comment_id=item['snippet']['topLevelComment']['id'],
                            video_id=item['snippet']['topLevelComment']['snippet']['videoId'],
                            channel_id=item['snippet']['channelId'],
                            comment_text=item['snippet']['topLevelComment']['snippet'].get('textDisplay'),
                            comment_author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            comment_publisment=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                comment_data.append(data)
    except:
        pass
    return comment_data

# Get playlist details
def get_playlist_details(channel_id):
    next_page_token = None
    All_data = []
    while True:
        request = youtube.playlists().list(
            part='snippet,contentDetails',
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response['items']:
            data = dict(playlist_id=item['id'],
                        title=item['snippet']['title'],
                        channel_id=item['snippet']['channelId'],
                        channel_name=item['snippet']['channelTitle'],
                        published_at=pd.to_datetime(item["snippet"]["publishedAt"]),
                        video_count=item['contentDetails']['itemCount'])
            All_data.append(data)
        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            break
    return All_data

# SQLite3 database connection
conn = sqlite3.connect('YouTube_Data.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS channels
             (channel_name TEXT, channel_id TEXT PRIMARY KEY, subscribers INTEGER,
              views INTEGER, total_videos INTEGER, channel_description TEXT, playlist_id TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS playlists
             (playlist_id TEXT PRIMARY KEY, title TEXT, channel_id TEXT, channel_name TEXT,
              published_at TEXT, video_count INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS videos
             (channel_name TEXT, channel_id TEXT, video_id TEXT PRIMARY KEY, title TEXT,
              tags TEXT, thumbnail TEXT, description TEXT, published_date TEXT, duration TEXT,
              views INTEGER, comments INTEGER, likes INTEGER, dislikes INTEGER, favorite_count INTEGER,
              definition TEXT, caption_status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS comments
             (comment_id TEXT PRIMARY KEY, video_id TEXT, channel_id TEXT, comment_text TEXT,
              comment_author TEXT, comment_publisment TEXT)''')
conn.commit()

# Function to convert DataFrame columns to match SQLite table data types
def convert_df_to_sql_dtypes(df, table_name):
    # Define data type conversions for each DataFrame
    channel_info_dtype = {
        'subscribers': int,
        'views': int,
        'total_videos': int,
        'playlist_id': str,
        'channel_description': str if 'channel_description' in df.columns else object
    }

    video_data_dtype = {
        'views': int,
        'published_date': str,
        'comments': int,
        'likes': int,
        'dislikes': int,
        'favorite_count': int,
        'definition': str if 'definition' in df.columns else object,
        'caption_status': str if 'caption_status' in df.columns else object,
        'channel_name': str,
        'tags': str,
        'thumbnail': str,
        'description': str,
        'duration': str,
        'channel_id': str,
        'title': str  # Assuming 'title' corresponds to 'video_title'
    }

    comments_dtype = {
        'comment_text': str,
        'comment_author': str,
        'comment_publishment': str if 'comment_publishment' in df.columns else object,
        'video_id': str
    }

    playlist_details_dtype = {
        'title': str,
        'channel_name': str,
        'published_at': str if 'published_at' in df.columns else object,
        'video_count': int,
        'channel_id': str
    }

    # Choose the appropriate dtype mapping based on table_name
    if table_name == 'channels':
        dtype_mapping = channel_info_dtype
    elif table_name == 'videos':
        dtype_mapping = video_data_dtype
    elif table_name == 'comments':
        dtype_mapping = comments_dtype
    elif table_name == 'playlists':
        dtype_mapping = playlist_details_dtype
    else:
        raise ValueError(f"Unsupported table name: {table_name}")

    # Convert each column in the DataFrame to match SQLite data types
    for col, dtype in dtype_mapping.items():
        if col in df.columns:
            if dtype == int:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            elif dtype == float:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
            elif dtype == str:
                df[col] = df[col].astype(str).fillna('')  # Ensure no null values
            elif dtype == object:
                pass
            elif dtype == pd.Timestamp:
                df[col] = pd.to_datetime(df[col], errors='coerce').fillna(pd.Timestamp('1900-01-01'))

    return df

def channel_details(channel_id):
    ch_details = get_channel_info(channel_id)
    pl_details = get_playlist_details(channel_id)
    vi_ids = get_videos_ids(channel_id)
    vi_details = get_video_info(vi_ids)
    com_details = get_comment_info(vi_ids)

    # Convert to DataFrame
    channel_df = pd.DataFrame([ch_details])
    video_df = pd.DataFrame(vi_details)
    comments_df = pd.DataFrame(com_details)
    playlist_df = pd.DataFrame(pl_details)

    # Convert each DataFrame to match SQLite table data types
    ch_details = convert_df_to_sql_dtypes(channel_df, 'channels')
    vi_details = convert_df_to_sql_dtypes(video_df, 'videos')
    com_details = convert_df_to_sql_dtypes(comments_df, 'comments')
    pl_details = convert_df_to_sql_dtypes(playlist_df, 'playlists')

    for _, ch in ch_details.iterrows():
        c.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (ch['channel_name'], ch['channel_id'], ch['subscribers'], ch['views'],
                  ch['total_videos'], ch['channel_description'], ch['playlist_id']))

    for _, pl in pl_details.iterrows():
        c.execute("INSERT INTO playlists VALUES (?, ?, ?, ?, ?, ?)",
                  (pl['playlist_id'], pl['title'], pl['channel_id'], pl['channel_name'],
                   pl['published_at'], pl['video_count']))

    for _, vi in vi_details.iterrows():
        c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (vi['channel_name'], vi['channel_id'], vi['video_id'], vi['title'], vi['tags'],
                   vi['thumbnail'], vi['description'], vi['published_date'], vi['duration'], vi['views'] or 0,
                   vi['comments'] or 0, vi['likes'] or 0, vi['dislikes'] or 0, vi['favorite_count'] or 0, vi['definition'] or '',
                   vi['caption_status'] or ''))

    for _, com in com_details.iterrows():
        c.execute("INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?)",
                  (com['comment_id'], com['video_id'],com['channel_id'], com['comment_text'], com['comment_author'],
                   com['comment_publisment']))

    conn.commit()
    return "Upload completed successfully"

def all_functions(channel_id): #main function which collects the data and stores them in SQLite database
  c.execute("SELECT 1 FROM Channels WHERE channel_id = ?", (channel_id,))
  result = c.fetchone()

  if result:
    message="Data for this channel ID is already stored."
  else:
    all_data_collection = channel_details(channel_id)
    if all_data_collection == "Upload completed successfully":
      message = "Successfully Stored"
    else:
      message = "Data Storing Faild"
  return message


from isodate import parse_duration
def dur(duration_str): #function to avoid time formate problem in video duration
    duration_seconds = parse_duration(duration_str).total_seconds()
    return duration_seconds


# SQL queries to retrieve data from SQLite database
# Table on main page
ch=pd.read_sql_query('''SELECT channel_name as 'channel name',subscribers as 'Subscription Count', channel_description as 'Channel Description' from channels''',conn)
vid=pd.read_sql_query('''SELECT channel_name as 'Channel name',title as 'Video name', views as 'View Count'  from videos''',conn)
com=pd.read_sql_query('''SELECT comment_text as 'Comment text',comment_author as 'Comment author' from comments''',conn)
ply=pd.read_sql_query('''SELECT title as 'playlist name',channel_name as 'channel name' , video_count as 'video_count' from playlists''',conn)
cha = ch.drop_duplicates()


#"1.What are the names of all the videos and their corresponding channels?"
question1=pd.read_sql_query('''SELECT channel_name as "CHANNEL NAME",title as "VIDEOS NAME" from videos''',conn)
#"2.Which channels have the most number of videos and how many videos do they have?",
question2=pd.read_sql_query('''select channel_name as "CHANNEL NAME", count(*) as "NUMBER OF VIDEOS" from videos GROUP BY channel_name ORDER BY count(*) desc''',conn)
#"3.What are the top 10 most viewed videos and their respective channels?"
question3=pd.read_sql_query('''SELECT channel_name as "CHANNEL NAME",title as "VIDEO NAME",views as "No.of VIEWS" from videos ORDER BY views desc LIMIT 10''',conn)
#"4.How many comments were made on each video, and what are their corresponding video names?"
question4=pd.read_sql_query('''SELECT title as "VIDEOS NAME",comments as "No.of COMMENTS" from videos ORDER BY comments DESC ''',conn)
#"5.Which videos have the highest number of likes, and what are their corresponding channel names?"
question5=pd.read_sql_query('''SELECT channel_name as "CHANNEL NAME",title as "VIDEOS NAME",likes as "No.of LIKES" from videos ORDER BY likes desc''',conn)
#"6.What is the total number of likes for each video and what are their corresponding video names?"
question6=pd.read_sql_query('''SELECT title as "VIDEOS NAME",likes as "No.of LIKES", dislikes as "No.of DISLIKES"  from videos ORDER BY likes desc''',conn)
#"7.What is the total number of views for each channel, and what are their corresponding channel names?",
question7=pd.read_sql_query('''SELECT channel_name as "CHANNEL NAME",views as "No.of VIEWS" from Channels ORDER BY views desc''',conn)
#"8.What are the names of all the channels that have published videos in the year 2022?"
question8=pd.read_sql_query('''SELECT channel_name as "CHANNEL NAME",title as "VIDEO NAME",published_date as "Published_Date" from videos WHERE strftime('%Y',published_date) = '2022' ''',conn)
#"9.What is the average duration of all videos in each channel, and what are their corresponding channel names?"
question9=pd.read_sql_query('''SELECT channel_name as "CHANNEL NAME",Duration as "DURATION" from videos''',conn)
question9["dur_alter"]=question9["DURATION"].apply(dur)
question9= question9.drop('DURATION', axis=1)
question9= question9.rename(columns={'dur_alter': 'DURATION in sec'})
q90 = question9.groupby('CHANNEL NAME').mean()
#"10.Which videos have the highest number of comments, and what are their corresponding channel names?"
question10=pd.read_sql_query('''select channel_name as "CHANNEL NAME",title as "VIDEO NAME",comments as "No.of COMMENTS " from videos WHERE comments is not null ORDER BY comments desc''',conn)


def show_channel_table(unique_channel):
    channel_id = unique_channel
    df = pd.read_sql_query(f"SELECT * FROM channels WHERE channel_id = '{channel_id}'", conn)
    st.dataframe(df)
    return df

def show_playlist_table(unique_channel):
    channel_id = unique_channel
    df1 = pd.read_sql_query(f"SELECT * FROM playlists WHERE channel_id = '{channel_id}'", conn)
    st.dataframe(df1)
    return df1

def show_videos_table(unique_channel):
    channel_id = unique_channel
    df2 = pd.read_sql_query(f"SELECT * FROM videos WHERE channel_id = '{channel_id}'", conn)
    st.dataframe(df2)
    return df2

def show_comments_table(unique_channel):
    channel_id = unique_channel
    df3 = pd.read_sql_query(f"SELECT * FROM comments WHERE channel_id = '{channel_id}'", conn)
    st.dataframe(df3)
    return df3

#code for Streamlit Application

st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")

with st.sidebar:
  st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
  st.header("Skill Take Away")
  st.caption("Python Scripting")
  st.caption("Data Collection")
  st.caption("Data Management Using SQLite3")
  st.caption("API Integration")
  selected = option_menu("Main Menu", ["HOME","VIEW", "QUERY"],
      icons=['house', 'search'], menu_icon="cast", default_index=0)

if selected == "HOME":
    st.title("Home Page")
    channel_id = st.text_input("Enter the Youtube Channel Id")
    if st.button(":green[Collect and store in SQL]"):
        ch_ids = []
        cursor = c.execute("SELECT channel_id FROM channels")
        for row in cursor:
            ch_ids.append(row[0])

        if channel_id in ch_ids:
            st.success("Channel Details Of The Given Channel Id Already Exists")
        else:
            insert = all_functions(channel_id)
            st.success(insert)
    with st.expander("CHANNELS"):
        st.write(cha)
    with st.expander("VIDEOS"):
        st.write(vid)
    with st.expander("PLAYLISTS"):
        st.write(ply)
    with st.expander("COMMENTS"):
        st.write(com)

elif selected == "VIEW":
    st.title("View Data")
    all_channels = []
    cursor = c.execute("SELECT channel_name FROM channels")
    for row in cursor:
        all_channels.append(row[0])

    unique_channel_name = st.selectbox("Select the channel", all_channels)
    unique_channel_1 = pd.read_sql_query(f"SELECT channel_id FROM playlists WHERE channel_name = '{unique_channel_name}'", conn)
    unique_channel = unique_channel_1["channel_id"][0]

    show_table = st.radio("SELECT THE TABLE FOR VIEW", ("CHANNELS", "PLAYLISTS", "VIDEOS", "COMMENTS"))

    if show_table == "CHANNELS":
        show_channel_table(unique_channel)
    elif show_table == "PLAYLISTS":
        show_playlist_table(unique_channel)
    elif show_table == "VIDEOS":
        show_videos_table(unique_channel)
    elif show_table == "COMMENTS":
        show_comments_table(unique_channel)

elif selected == "QUERY":
    st.title("Query Data")
    question = st.sidebar.selectbox("Select Questions",
                                    ("1.What are the names of all the videos and their corresponding channels?",
                                     "2.Which channels have the most number of videos and how many videos do they have?",
                                     "3.What are the top 10 most viewed videos and their respective channels?",
                                     "4.How many comments were made on each video, and what are their corresponding video names?",
                                     "5.Which videos have the highest number of likes, and what are their corresponding channel names?",
                                     "6.What is the total number of likes for each video, and what are their corresponding video names?",
                                     "7.What is the total number of views for each channel, and what are their corresponding channel names?",
                                     "8.What are the names of all the channels that have published videos in the year 2022?",
                                     "9.What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                                     "10.Which videos have the highest number of comments, and what are their corresponding channel names?"))

    if question == "1.What are the names of all the videos and their corresponding channels?":
        q1 = pd.DataFrame(question1)
        st.write(q1)
    elif question == "2.Which channels have the most number of videos and how many videos do they have?":
        q2 = pd.DataFrame(question2)
        st.write(q2)
    elif question == "3.What are the top 10 most viewed videos and their respective channels?":
        q3 = pd.DataFrame(question3)
        st.write(q3)
    elif question == "4.How many comments were made on each video, and what are their corresponding video names?":
        q4 = pd.DataFrame(question4)
        st.write(q4)
    elif question == "5.Which videos have the highest number of likes, and what are their corresponding channel names?":
        q5 = pd.DataFrame(question5)
        st.write(q5)
    elif question == "6.What is the total number of likes for each video, and what are their corresponding video names?":
        q6 = pd.DataFrame(question6)
        st.write(q6)
    elif question == "7.What is the total number of views for each channel, and what are their corresponding channel names?":
        q7 = pd.DataFrame(question7)
        st.write(q7)
    elif question == "8.What are the names of all the channels that have published videos in the year 2022?":
        q8 = pd.DataFrame(question8)
        st.write(q8)
    elif question == "9.What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        q9 = pd.DataFrame(q90)
        st.write(q9)
    elif question == "10.Which videos have the highest number of comments, and what are their corresponding channel names?":
        q10 = pd.DataFrame(question10)
        st.write(q10)
