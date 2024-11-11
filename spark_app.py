import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import matplotlib.pyplot as plt

# Initialize Spark session
spark = SparkSession.builder.appName("RedditDataAnalysis").getOrCreate()

# Fetch data from the API
for i in range(50000) :
    response = requests.get("http://127.0.0.1:5000/generate_post")
    posts_data = response.json()

    # Load data into a Spark DataFrame
    posts_df = spark.createDataFrame(posts_data)

    # Cast `score` and `num_comments` columns to integer types
    posts_df = posts_df.withColumn("score", col("score").cast("int"))
    posts_df = posts_df.withColumn("num_comments", col("num_comments").cast("int"))

    # Show the data structure
    posts_df.show()

    # Process data: e.g., calculate average score and number of comments
    avg_data = posts_df.groupBy("over_18").avg("score", "num_comments").collect()

    # Convert results to a Pandas DataFrame for plotting
    avg_data_pandas = {
        "over_18": [row["over_18"] for row in avg_data],
        "avg_score": [row["avg(score)"] for row in avg_data],
        "avg_comments": [row["avg(num_comments)"] for row in avg_data],
    }

# Step 3: Visualization
# Plotting average score and comments
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].bar(avg_data_pandas["over_18"], avg_data_pandas["avg_score"], color=['blue', 'orange'])
ax[0].set_title("Average Score by Over_18 Status")
ax[0].set_xlabel("Over 18")
ax[0].set_ylabel("Average Score")

ax[1].bar(avg_data_pandas["over_18"], avg_data_pandas["avg_comments"], color=['blue', 'orange'])
ax[1].set_title("Average Comments by Over_18 Status")
ax[1].set_xlabel("Over 18")
ax[1].set_ylabel("Average Number of Comments")

plt.tight_layout()
plt.show()
