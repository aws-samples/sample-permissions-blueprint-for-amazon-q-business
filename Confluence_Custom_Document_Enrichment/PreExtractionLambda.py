import requests
from requests.auth import HTTPBasicAuth
import os
import boto3
import base64
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFLUENCE_BASE_URL = os.environ['CONFLUENCE_BASE_URL']
CONFLUENCE_USERNAME = os.environ['CONFLUENCE_USERNAME']
CONFLUENCE_API_TOKEN = os.environ['CONFLUENCE_API_TOKEN']
s3 = boto3.client("s3")

def get_attachments_from_page(page_id):
    attachments_url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}/child/attachment"
    headers = {"Accept": "application/json"}

    response = requests.get(
        attachments_url,
        headers=headers,
        auth=HTTPBasicAuth(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN),
        timeout=30
    )
    response.raise_for_status()

    attachments = response.json()
    image_files = [
        attachment for attachment in attachments.get('results', [])
        if 'image' in attachment['metadata']['mediaType']
    ]

    if not image_files:
        raise ValueError("No image files found on the page.")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_image = {executor.submit(download_image, image): image for image in image_files}
        return [future.result() for future in as_completed(future_to_image)]

def download_image(image):
    download_url = f"{CONFLUENCE_BASE_URL}{image['_links']['download']}"
    image_name = image['title']

    response.raise_for_status()

    base64_str = base64.b64encode(response.content).decode('utf-8')
    return image_name, base64_str

def image_to_text(encoded_image):
    client = boto3.client("bedrock-runtime")
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    prompt = """
    You are a document image analysis expert. Please analyze the provided image and:
    1. Provide a title (format: image_title: <result>)
    2. Provide a description (format: image_description: <result>)
    3. Extract all text (format: image_ocr: <result>)
    4. If there's a table, describe its schema and content briefly (format: table: <result>)
    Be truthful and accurate. Do not guess or make assumptions without evidence.
    """

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": 0.6,
        "top_p": 0.9,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": encoded_image,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    try:
        response = client.invoke_model(body=json.dumps(request_body), modelId=model_id)
        model_response = json.loads(response["body"].read())
        return model_response["content"][0]["text"]
    except Exception as e:
        print(f"Error invoking the model: {e}")
        return None

def lambda_handler(event, context):
    s3_bucket = event.get("s3Bucket")

    try:
        base64_images = get_attachments_from_page(page_id)

        for image_file_name, image_base64 in base64_images:
            text_response = image_to_text(image_base64)
            if not text_response:
                print(f"Failed to process image: {image_file_name}")
                continue

            file_name_without_ext, _ = os.path.splitext(image_file_name)
            new_key = f'cde_pre_output/{file_name_without_ext}.txt'

            s3.put_object(Bucket=s3_bucket, Key=new_key, Body=text_response)
            print(f"Processed and stored: {new_key}")

        return {
            "version": "v0",
            "s3ObjectKey": new_key,
            "metadataUpdates": []
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        raise
