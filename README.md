

Project Name: Reddit Sentiment Analysis and ETL Pipeline

Table of Contents

	•	Overview
	•	Features
	•	Folder Structure
	•	Installation
	•	Usage
	•	Technologies Used
	•	Contributing
	•	License

Overview

This project implements a Reddit sentiment analysis system integrated with an ETL pipeline. Using Spark for data processing and a custom API for fetching Reddit data, the project processes posts, analyzes sentiments, and generates insights enriched with emojis.

Features

	•	Data Collection: Fetches Reddit posts using API integration.
	•	Sentiment Analysis: Classifies posts as positive, negative, or neutral using a trained sentiment model.
	•	Data Enrichment: Adds emojis to sentiment labels for enhanced user interpretation.
	•	ETL Pipeline: A scalable Spark-based pipeline for efficient data transformation and loading.
	•	API Integration: Supports fetching and serving processed data.

Folder Structure

bdeextra copy/  
├── spark pipeline/  
│   └── spark_app.py       # Spark-based ETL pipeline script  
├── sentiment model/  
│   └── sentimental.py     # Sentiment analysis model script  
├── api/  
│   └── app.py             # API integration script  
├── reddit_data/  
│   ├── reddit_posts.csv   # Raw Reddit data  
│   ├── reddit_posts copy.csv  
│   └── reddit_posts 2.csv  
├── reddit_posts_with_sentiment_and_emojis.csv  # Processed Reddit data with emojis  
├── reddit_posts_with_sentiment.csv            # Processed Reddit data with sentiment labels  

Installation

	1.	Clone the repository:

git clone <repository-url>  
cd <repository-folder>  


	2.	Install dependencies:
	•	Ensure Python 3.x and pip are installed.
	•	Install required Python libraries:

pip install -r requirements.txt  


	3.	Set up API credentials:
	•	Create a .env file in the api folder with Reddit API credentials:

CLIENT_ID=<your_client_id>  
CLIENT_SECRET=<your_client_secret>  
USER_AGENT=<your_user_agent>  

Usage

	1.	Run the API:
Navigate to the api folder and start the server:

python app.py  


	2.	Execute the Spark pipeline:
Navigate to the spark pipeline folder:

python spark_app.py  


	3.	Perform sentiment analysis:
Navigate to the sentiment model folder:

python sentimental.py  

Technologies Used

	•	Python: Primary programming language.
	•	Apache Spark: For ETL and data transformation.
	•	Reddit API: For data collection.
	•	Natural Language Toolkit (NLTK): For sentiment analysis.

Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any suggested improvements.

License

This project is licensed under the MIT License.

Let me know if you’d like to add custom details or modify this template. ￼
