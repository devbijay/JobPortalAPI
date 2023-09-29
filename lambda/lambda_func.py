import json
from io import BytesIO
import boto3
from fpdf import FPDF

S3_BUCKET_NAME = "your-s3-bucket-name"
s3 = boto3.client('s3')


def generate_pdf_resume(candidate):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Name: {candidate['name']}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {candidate['email']}", ln=True)
    pdf.cell(200, 10, txt=f"Phone: {candidate['phone']}", ln=True)
    pdf.cell(200, 10, txt=f"City: {candidate['city']}", ln=True)
    pdf.cell(200, 10, txt=f"Full Address: {candidate['full_address']}", ln=True)
    pdf.cell(200, 10, txt=f"Skills: {candidate['skills']}", ln=True)

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    return pdf_buffer.getvalue()


def upload_to_s3_with_tag(payload, file_name, tags):
    s3.put_object(Bucket=S3_BUCKET_NAME,
                  Key=f"resume/{file_name}",
                  Body=payload,
                  Tagging="&".join([f"{tag['Key']}={tag['Value']}" for tag in tags]),
                  Metadata={"TagSet": json.dumps(tags)}
                  )


def lambda_handler(event, context):
    for record in event["Records"]:
        sqs_payload = json.loads(record["body"])

        for candidate in sqs_payload:
            resume = generate_pdf_resume(candidate)
            skill_tags = [{"Key": "Skill", "Value": skill} for skill in candidate['Skills']]
            upload_to_s3_with_tag(payload=resume, file_name=f"{candidate['name']}-candidate['id'].pdf", tags=skill_tags)
