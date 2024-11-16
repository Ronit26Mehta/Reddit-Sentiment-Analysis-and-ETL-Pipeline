import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_daq as daq
import boto3
from io import StringIO
import json

# Initialize Spark session
try:
    spark = SparkSession.builder.appName("RedditDataAnalysis").getOrCreate()
    print("Spark session initialized successfully.")
except Exception as e:
    print(f"Error initializing Spark session: {e}")
    exit()

# Initialize Dash app
app = dash.Dash(__name__)

# AWS S3 Configuration
s3 = boto3.client("s3", region_name="eu-north-1")
S3_BUCKET_NAME = "airscholar-reddit-engineering-bde"  # Replace with your S3 bucket name

# Fetch and process data
def fetch_and_process_data():
    try:
        response = requests.get("http://127.0.0.1:5000/generate_post")
        response.raise_for_status()
        posts_data = response.json()

        # Save raw data to S3 in JSON format
        save_to_s3(json.dumps(posts_data), "reddit_raw_data.json", "application/json")

        # Load data into a Spark DataFrame
        posts_df = spark.createDataFrame(posts_data)

        # Cast columns to appropriate types
        posts_df = posts_df.withColumn("score", col("score").cast("int"))
        posts_df = posts_df.withColumn("num_comments", col("num_comments").cast("int"))

        # Convert to Pandas DataFrame
        posts_pd = posts_df.toPandas()

        # Save processed data to S3 in CSV format
        save_to_s3(posts_pd.to_csv(index=False), "reddit_processed_data.csv", "text/csv")

        return posts_pd
    except Exception as e:
        print(f"Error fetching or processing data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of failure

# Save data to S3
def save_to_s3(data, file_name, content_type):
    try:
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=data,
            ContentType=content_type
        )
        print(f"Data successfully saved to S3 bucket '{S3_BUCKET_NAME}' as '{file_name}'")
    except Exception as e:
        print(f"Error saving data to S3: {e}")

# Fetch initial data
posts_pd = fetch_and_process_data()

# Dashboard layout
app.layout = html.Div([
    html.H1("Reddit Data Dashboard", style={'text-align': 'center'}),

    # Real-time metrics using Dash Daq
    html.Div([
        daq.LEDDisplay(
            id='avg-score-display',
            label="Average Post Score",
            value="0",
            color="blue",
            style={'display': 'inline-block', 'margin-right': '30px'}
        ),
        daq.LEDDisplay(
            id='avg-comments-display',
            label="Average Comments",
            value="0",
            color="orange",
            style={'display': 'inline-block'}
        ),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Refresh button
    html.Div([
        html.Button("Refresh Data", id="refresh-button", n_clicks=0),
        html.P("Click the button to fetch new data from the API.", style={'text-align': 'center'}),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Plots
    dcc.Graph(id='score-bar-plot'),
    dcc.Graph(id='comments-bar-plot'),
    dcc.Graph(id='posts-distribution-plot'),
    dcc.Graph(id='score-histogram'),
    dcc.Graph(id='author-activity-plot'),

    # Dynamic slider for filtering top authors
    html.Div([
        html.Label("Filter Top Authors by Post Count:", style={'margin-bottom': '10px'}),
        dcc.Slider(
            id='author-slider',
            min=1,
            max=20,
            step=1,
            value=10,
            marks={i: str(i) for i in range(1, 21)},
        )
    ], style={'margin-top': '20px'}),
])

# Update plots and real-time metrics when refresh button is clicked
@app.callback(
    [
        Output('avg-score-display', 'value'),
        Output('avg-comments-display', 'value'),
        Output('score-bar-plot', 'figure'),
        Output('comments-bar-plot', 'figure'),
        Output('posts-distribution-plot', 'figure'),
        Output('score-histogram', 'figure'),
        Output('author-activity-plot', 'figure'),
    ],
    [Input('refresh-button', 'n_clicks'),
     Input('author-slider', 'value')]
)
def update_dashboard(n_clicks, top_authors_count):
    # Fetch and process data
    posts_pd = fetch_and_process_data()

    if posts_pd.empty:
        return "N/A", "N/A", {}, {}, {}, {}, {}

    # Calculate average score and comments for real-time metrics
    avg_score = posts_pd["score"].mean()
    avg_comments = posts_pd["num_comments"].mean()

    # Plot 1: Average score by over_18 status
    avg_score_df = posts_pd.groupby('over_18')['score'].mean().reset_index()
    score_fig = px.bar(
        avg_score_df,
        x="over_18",
        y="score",
        color="over_18",
        title="Average Score by Over_18 Status",
        labels={"over_18": "Over 18", "score": "Average Score"}
    )
    score_fig.update_layout(template="plotly_dark")

    # Plot 2: Average number of comments by over_18 status
    avg_comments_df = posts_pd.groupby('over_18')['num_comments'].mean().reset_index()
    comments_fig = px.bar(
        avg_comments_df,
        x="over_18",
        y="num_comments",
        color="over_18",
        title="Average Comments by Over_18 Status",
        labels={"over_18": "Over 18", "num_comments": "Average Comments"}
    )
    comments_fig.update_layout(template="plotly_dark")

    # Plot 3: Distribution of posts by over_18 status
    distribution_fig = px.pie(
        posts_pd,
        names="over_18",
        title="Post Distribution by Over_18 Status",
        hole=0.3,
    )
    distribution_fig.update_layout(template="plotly_dark")

    # Plot 4: Histogram of scores
    score_hist_fig = px.histogram(
        posts_pd,
        x="score",
        title="Distribution of Post Scores",
        nbins=20,
        labels={"score": "Score"}
    )
    score_hist_fig.update_layout(template="plotly_dark")

    # Plot 5: Author activity (number of posts per author)
    author_activity = posts_pd.groupby('author').size().reset_index(name='post_count').sort_values('post_count', ascending=False).head(top_authors_count)
    author_fig = px.bar(
        author_activity,
        x="author",
        y="post_count",
        title=f"Top {top_authors_count} Active Authors",
        labels={"author": "Author", "post_count": "Number of Posts"}
    )
    author_fig.update_layout(template="plotly_dark")

    return f"{avg_score:.2f}", f"{avg_comments:.2f}", score_fig, comments_fig, distribution_fig, score_hist_fig, author_fig

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)