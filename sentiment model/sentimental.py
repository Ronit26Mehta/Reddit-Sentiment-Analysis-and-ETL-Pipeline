from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import FloatType, StringType
from textblob import TextBlob
import requests
import time

# Initialize Spark session
spark = SparkSession.builder.appName("RedditDataAnalysisWithEmoji").getOrCreate()

# Define the lists of positive and negative emojis
positive_emojis = ["😊", "😁", "😄", "😍", "👍", "🥳", "🎉", "😇", "❤️"]
negative_emojis = ["😢", "😠", "😡", "💔", "😞", "👎", "🤬", "⚡", "❌"]

# Fetch and process posts continuously
def fetch_and_process_posts():
    while True:
        try:
            # Fetch data from the API
            response = requests.get("http://127.0.0.1:5000/generate_post")
            response.raise_for_status()  # Check for HTTP request errors
            posts_data = response.json()

            # Load data into a Spark DataFrame
            posts_df = spark.createDataFrame(posts_data)

            # Cast `score` and `num_comments` columns to integer types
            posts_df = posts_df.withColumn("score", col("score").cast("int"))
            posts_df = posts_df.withColumn("num_comments", col("num_comments").cast("int"))

            # Define a sentiment analysis function
            def analyze_sentiment(text):
                blob = TextBlob(text)
                return blob.sentiment.polarity

            # Register the function as a UDF
            analyze_sentiment_udf = udf(analyze_sentiment, FloatType())

            # Apply the sentiment analysis UDF
            posts_df = posts_df.withColumn("sentiment_score", analyze_sentiment_udf(col("title")))

            # Define a function to categorize sentiment
            def categorize_sentiment(score):
                if score > 0:
                    return "positive"
                elif score < 0:
                    return "negative"
                else:
                    return "neutral"

            # Register the categorization function as a UDF
            categorize_sentiment_udf = udf(categorize_sentiment, StringType())

            # Apply categorization UDF
            posts_df = posts_df.withColumn("sentiment_label", categorize_sentiment_udf(col("sentiment_score")))

            # Define a function to classify based on emoji presence
            def classify_by_emoji(text):
                if any(emoji in text for emoji in positive_emojis):
                    return "positive"
                elif any(emoji in text for emoji in negative_emojis):
                    return "negative"
                else:
                    return "neutral"

            # Register the emoji classification function as a UDF
            classify_by_emoji_udf = udf(classify_by_emoji, StringType())

            # Apply the emoji classification UDF
            posts_df = posts_df.withColumn("emoji_sentiment", classify_by_emoji_udf(col("title")))

            # Show the updated DataFrame
            posts_df.show(truncate=False)

            # Save the entire DataFrame to a CSV file
            output_path = "reddit_posts_with_sentiment_and_emojis.csv"
            posts_df.coalesce(1).write.csv(output_path, header=True, mode="append")

            print(f"Sentiment analysis data with emoji classification saved to {output_path}")

        except Exception as e:
            print(f"An error occurred: {e}")

        # Sleep for a defined interval before fetching the next set of posts
        time.sleep(10)  # Sleep for 10 seconds before fetching new posts

# Run the function continuously
fetch_and_process_posts()