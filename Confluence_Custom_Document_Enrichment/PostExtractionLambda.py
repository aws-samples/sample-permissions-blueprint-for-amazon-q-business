import boto3
import logging
import time
import urllib
import json
import re
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def metadata_to_text(meta):
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime")

    # Set the model ID, e.g., Claude 3 Haiku.
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    # Define the prompt for the model.
    prompt = "Describe the following in narrative natural language\n\n" + json.dumps(meta)
    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.3,
        "top_p": 0.9,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    # Invoke the model with the request.
    response = client.invoke_model(modelId=model_id, body=request)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["content"][0]["text"]
    print(response_text)

    cats = [dt["value"]["stringValue"] for dt in meta.get("attributes") if dt["name"] == "_category"]
    if len(cats) > 0:
        category = cats[0] + " : "
    else:
        category = ""
    titles = [dt["value"]["stringValue"] for dt in meta.get("attributes") if dt["name"] == "_document_title"]
    if len(titles) > 0:
        title = titles[0]
    else:
        title = ""
    return category + title + "\n\n" + response_text

def lambda_handler(event, context):
    logger.info("Received event: %s" % json.dumps(event))
    s3Bucket = event.get("s3Bucket")
    s3ObjectKey = event.get("s3ObjectKey")
    metadata = event.get("metadata")
    logger.info("Metadata: %s" % json.dumps(metadata))
    text_data = metadata_to_text(metadata)
    qbusiness_document_object = s3.get_object(Bucket = s3Bucket, Key = s3ObjectKey)
    qbusiness_document_string = qbusiness_document_object['Body'].read().decode('utf-8',errors='ignore')
    qbusiness_document = json.loads(qbusiness_document_string)
    logger.info("Got document body: %s" % json.dumps(qbusiness_document))
    afterCDE_text = text_data + "\n\n" + qbusiness_document["textContent"]["documentBodyText"]
    qbusiness_document["textContent"]["documentBodyText"] = afterCDE_text
    logger.info("Written document body: %s" % json.dumps(qbusiness_document))
    # Extract the document name and file type from the s3ObjectKey
    file_name = os.path.basename(s3ObjectKey)
    file_name_without_ext, _ = os.path.splitext(file_name)
    new_key = f'cde_post_output/{file_name_without_ext}.txt'
    s3.put_object(Bucket = s3Bucket, Key = new_key, Body=json.dumps(qbusiness_document))
    return {
        "version" : "v0",
        "s3ObjectKey": new_key,
        "metadataUpdates": []
    }
