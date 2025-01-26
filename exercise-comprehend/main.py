import boto3
import csv

# read the movies CSV and populate the all_notes array with all the of notes
with open("movies.csv", 'r') as fd:
    reader = csv.DictReader(
        fd, fieldnames=["ResponseId", "Notes"], dialect='excel')
    all_notes = [row["Notes"] for row in reader]

# Generate client
client = boto3.client('comprehend')

# Request sentiment from array data
response = client.batch_detect_sentiment(
    TextList=all_notes,
    LanguageCode='en'
)

# Print results
for result in response["ResultList"]:
    index = result["Index"]
    sentiment = result["Sentiment"]

    print(sentiment, all_notes[index])
