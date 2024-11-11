import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import FloatType, StringType
from textblob import TextBlob

# Initialize Spark session
spark = SparkSession.builder.appName("RedditDataAnalysis").getOrCreate()

# Fetch data from the API
response = requests.get("http://127.0.0.1:5000/generate_post")
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

# Register the function as a UDF (User Defined Function) in Spark
analyze_sentiment_udf = udf(analyze_sentiment, FloatType())

# Apply the sentiment analysis UDF to create a new column with sentiment scores
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

# Apply categorization UDF to create a new column with sentiment labels
posts_df = posts_df.withColumn("sentiment_label", categorize_sentiment_udf(col("sentiment_score")))

# Show the updated DataFrame structure with sentiment columns
posts_df.show(truncate=False)

# Save the entire DataFrame to a CSV file
output_path = "reddit_posts_with_sentiment.csv"
posts_df.coalesce(1).write.csv(output_path, header=True, mode="overwrite")

print(f"Sentiment analysis data saved to {output_path}")
