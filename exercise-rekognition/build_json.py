import glob
import boto3
import json

# Generate client
client = boto3.client('rekognition')

combined = []

# Iterate over the images
for filename in glob.glob('public/photos/*.jpeg'):
    with open(filename, 'rb') as fd:
        # Get labels from Rekognition
        response = client.detect_labels(Image={'Bytes': fd.read()})

        # Create entry
        entry = {"Filename": filename.replace("public/", "")}

        # Add labels
        entry["Labels"] = response["Labels"]

        # Add to combined
        combined.append(entry)

print(json.dumps(combined, indent=2))
