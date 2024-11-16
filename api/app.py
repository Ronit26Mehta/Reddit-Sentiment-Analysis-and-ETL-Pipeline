from flask import Flask, jsonify
from faker import Faker
import random
import threading
import time
import csv
from datetime import datetime

app = Flask(__name__)
fake = Faker()

# CSV file setup
csv_file = "reddit_posts.csv"

# Lists of positive and negative emojis
positive_emojis = ["😀", "🔥", "💡", "😂", "🚀", "🎉", "🌟", "🎯", "📚"]
negative_emojis = ["💔", "😢", "😡", "💀", "👎", "😭", "🤬", "⚡", "❌", "🚨"]

# Function to initialize CSV with headers
def initialize_csv():
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "id", "title", "score", "num_comments", "author",
            "created_utc", "url", "over_18", "edited", "spoiler", "stickied"
        ])

# Function to generate a title with a 20% probability for emojis
def generate_title_with_emojis():
    title = fake.sentence(nb_words=6)
    if random.random() < 0.2:  # 20% probability to add emojis
        # Choose whether to add positive or negative emojis
        if random.random() < 0.5:  # 50% chance for positive or negative
            emojis = positive_emojis
        else:
            emojis = negative_emojis
        emoji_count = random.randint(1, 3)  # Add 1 to 3 emojis
        emoji_list = random.choices(emojis, k=emoji_count)
        title += " " + " ".join(emoji_list)
    return title

# Function to generate a single post
def generate_reddit_post():
    return {
        "id": fake.lexify("????????"),  # Generates a random 8-character string
        "title": generate_title_with_emojis(),
        "score": random.randint(0, 100),
        "num_comments": random.randint(0, 50),
        "author": fake.user_name(),
        "created_utc": fake.date_time_this_year().strftime('%Y-%m-%d %H:%M:%S'),
        "url": fake.url(),
        "over_18": random.choice([True, False]),
        "edited": random.choice([True, False]),
        "spoiler": random.choice([True, False]),
        "stickied": random.choice([True, False])
    }

# Background task to append generated data to CSV every 5 seconds
def generate_data_continuously():
    while True:
        post = generate_reddit_post()
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(post.values())
        time.sleep(5)

# API route to get recent data from CSV
@app.route('/generate_post', methods=['GET'])
def generate_post():
    posts = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            posts.append(row)
    return jsonify(posts[-10:])  # Return last 10 posts

if __name__ == '__main__':
    # Initialize CSV and start background data generation
    initialize_csv()
    threading.Thread(target=generate_data_continuously, daemon=True).start()
    app.run(port=5000)