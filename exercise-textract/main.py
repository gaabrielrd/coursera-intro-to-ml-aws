import glob
import boto3
import json
import csv
import sys

csv_array = []

client = boto3.client('textract')

for filename in glob.glob('raw_images/*.jpg'):
    csv_row = {}

    print(f"Processing: {filename}")

    with open(filename, 'rb') as fd:
        file_bytes = fd.read()

    response = client.analyze_document(
        Document={'Bytes': file_bytes},
        FeatureTypes=["QUERIES"],
        QueriesConfig={
            'Queries': [
                {'Text': 'What is the response id', 'Alias': 'ResponseId'},
                {'Text': 'What are the notes?', 'Alias': 'Notes'},
            ]
        }
    )

    # uncomment this to see the format of the reponse
    # print(json.dumps(response, indent=2))

    # get the results from queries
    results = list(
        filter(lambda x: x["BlockType"] == "QUERY_RESULT", response["Blocks"]))

    print(results)

    # First query is the response id
    csv_row["ResponseId"] = results[0]["Text"]
    # Second query is the notes
    csv_row["Notes"] = results[1]["Text"]

    # Add the row
    csv_array.append(csv_row)

# Write the CSV
writer = csv.DictWriter(sys.stdout, fieldnames=[
                        "ResponseId", "Notes"], dialect='excel')
writer.writeheader()
for row in csv_array:
    writer.writerow(row)
