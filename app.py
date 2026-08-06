import streamlit as st
import pandas as pd
import plotly.express as px

from youtube_api import (
    get_channel_id,
    get_channel_stats,
    get_upload_playlist,
    get_recent_videos,
    get_video_statistics
)

st.set_page_config(
    page_title="YouTube Creator Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 YouTube Creator Analytics Dashboard")

channel_input = st.text_input(
    "Channel Username",
    "@SandeepSwadia"
)

if st.button("Analyze Channel"):

    with st.spinner("Fetching YouTube data..."):

        try:

            #########################################
            # Channel
            #########################################

            channel_id = get_channel_id(channel_input)

            channel = get_channel_stats(channel_id)

            snippet = channel["snippet"]
            stats = channel["statistics"]

            uploads_playlist = get_upload_playlist(channel)

            #########################################
            # Videos
            #########################################

            video_ids = get_recent_videos(uploads_playlist)

            videos = get_video_statistics(video_ids)

            #########################################
            # DataFrame
            #########################################

            rows = []

            for video in videos:

                statistics = video.get("statistics", {})
                snippet = video.get("snippet", {})

                rows.append({

                    "Title":
                        snippet.get("title"),

                    "Published":
                        snippet.get("publishedAt")[:10],

                    "Views":
                        int(statistics.get("viewCount", 0)),

                    "Likes":
                        int(statistics.get("likeCount", 0)),

                    "Comments":
                        int(statistics.get("commentCount", 0))

                })

            df = pd.DataFrame(rows)

            df["Published"] = pd.to_datetime(df["Published"])

            df = df.sort_values("Published")

            df["Days Since Upload"] = (
                pd.Timestamp.today().normalize()
                - df["Published"]
            ).dt.days

            df["Views Per Day"] = (
                df["Views"] /
                df["Days Since Upload"].clip(lower=1)
            )

            df["Like Rate"] = (
                df["Likes"] /
                df["Views"].replace(0, 1)
            ) * 100

            df["Comment Rate"] = (
                df["Comments"] /
                df["Views"].replace(0, 1)
            ) * 100

            if len(df) == 0:
                st.warning("No videos found.")
                st.stop()

            #########################################
            # Metrics
            #########################################

            subscribers = int(stats.get("subscriberCount", 0))
            total_views = int(stats.get("viewCount", 0))
            total_videos = int(stats.get("videoCount", 0))

            average_views = int(df["Views"].mean())

            total_recent_views = int(df["Views"].sum())

            top_video = df.sort_values(
                "Views",
                ascending=False
            ).iloc[0]

            #########################################
            # Channel Header
            #########################################

            st.header(channel["snippet"]["title"])

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Subscribers",
                f"{subscribers:,}"
            )

            c2.metric(
                "Channel Views",
                f"{total_views:,}"
            )

            c3.metric(
                "Total Videos",
                f"{total_videos:,}"
            )

            c4.metric(
                "Average Views",
                f"{average_views:,}"
            )

            st.divider()

            #########################################
            # Recent Metrics
            #########################################

            c1, c2 = st.columns(2)

            c1.metric(
                "Recent Videos Views",
                f"{total_recent_views:,}"
            )

            c2.metric(
                "Top Video Views",
                f"{top_video['Views']:,}"
            )

            st.write("### 🏆 Best Performing Video")

            st.success(top_video["Title"])

            #########################################
            # Chart
            #########################################

            st.subheader("Top Videos")

            top10 = (
                df
                .sort_values("Views", ascending=False)
                .head(10)
            )

            fig = px.bar(
                top10,
                x="Views",
                y="Title",
                orientation="h",
                text="Views"
            )

            fig.update_layout(
                yaxis=dict(
                    autorange="reversed"
                ),
                height=650
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            #########################################
            # Upload Timeline
            #########################################

            st.subheader("Channel Growth Timeline")

            fig2 = px.line(
                df,
                x="Published",
                y="Views",
                markers=True,
                hover_data=[
                    "Title",
                    "Likes",
                    "Comments"
                ]
            )

            fig2.update_layout(
                xaxis_title="Upload Date",
                yaxis_title="Views"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            #########################################
            # Likes vs Views
            #########################################

            st.subheader("Likes vs Views")

            fig3 = px.scatter(
                df,
                x="Views",
                y="Likes",
                hover_name="Title",
                size="Comments"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )




            st.subheader("Fastest Growing Videos")

            fast = (
                df
                .sort_values(
                    "Views Per Day",
                    ascending=False
                )
                .head(10)
            )

            st.dataframe(
                fast[
                    [
                        "Title",
                        "Views",
                        "Views Per Day",
                        "Published"
                    ]
                ],
                use_container_width=True
            )

            #########################################
            # Table
            #########################################

            st.subheader("Recent Videos")

            st.dataframe(
                df.sort_values(
                    "Published",
                    ascending=False
                ),
                use_container_width=True
            )

        except Exception as e:

            st.error(str(e))


        