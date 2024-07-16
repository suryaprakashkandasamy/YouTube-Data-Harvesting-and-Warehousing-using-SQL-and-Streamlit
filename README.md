# YouTube Data Harvesting and Warehousing Project

## Overview

This project facilitates the comprehensive collection and storage of data from YouTube channels, videos, playlists, and comments using the YouTube Data API. The gathered data is stored efficiently in a SQLite3 database and presented through a user-friendly Streamlit interface for interactive exploration and querying.

## Technologies Used

- **Python**: The primary programming language used for implementing data collection, analysis, and database management.
- **YouTube Data API**: Google's official API utilized to interact with YouTube's platform for retrieving extensive data about channels, videos, playlists, and comments.
- **SQLite3**: A lightweight, serverless database engine chosen for its simplicity and seamless integration with Python, used for storing structured data collected from YouTube.
- **Streamlit**: An open-source app framework employed to create intuitive web applications for visualizing and querying the collected YouTube data stored in SQLite3 databases.

## Usage

### Data Collection

Enter a YouTube channel ID to fetch and store detailed information about the channel, including statistics, videos, playlists, and comments.
Collected data includes channel statistics (subscribers, views, total videos), video details (title, description, views, likes, dislikes), playlist details, and video comments.

### Data Storage

Utilizes SQLite3 database to store structured data:
  - **Channels**: Stores comprehensive information about YouTube channels.
  - **Videos**: Records specific data about each video, such as views, likes, dislikes, and comments.
  - **Playlists**: Stores details of playlists associated with channels.
  - **Comments**: Archives comments retrieved from YouTube videos, including author details and timestamps.

### Visualization and Querying

Offers an intuitive interface through Streamlit for interactive visualization and querying of stored YouTube data:
  - Channel statistics (subscribers, views).
  - Video details (views, likes, dislikes).
  - Playlist details (title, video count).
  - Comment details (text, author).
Supports querying stored data with predefined SQL queries to generate insightful reports:
  - Most viewed videos and channels.
  - Top videos by likes, comments, and views.
  - Average video duration by channel.
  - Channels with videos published in specific years.

## Features

**Comprehensive Data Retrieval**: Retrieves extensive information about YouTube channels, videos, playlists, and comments using the YouTube Data API.
**Efficient Data Storage**: Stores collected data efficiently in a SQLite3 database, ensuring easy retrieval and effective data management.
**Interactive Exploration**: Facilitates interactive exploration of YouTube channel performance and video engagement metrics through a user-friendly Streamlit interface.
**Querying Capabilities**: Supports predefined SQL queries to extract specific insights and generate reports based on stored YouTube data.
**User-Friendly Interface**: Provides a straightforward and intuitive interface via Streamlit for entering channel IDs, visualizing data, and querying stored information.

This README file provides an overview of the YouTube Data Harvesting and Warehousing project, highlighting its objectives, technologies utilized, core functionalities, and usage instructions. Customize as needed to align with specific project requirements and preferences.
