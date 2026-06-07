import boto3
import json
import urllib.request
import urllib.parse
import hashlib
import time
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('job-alerts')
ses = boto3.client('ses', region_name='us-east-1')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:343253677879:job-alerts-topic'
ALERT_EMAIL = 'interiano88.julio@gmail.com'
RAPIDAPI_KEY = 'b02efff75emshccc8ee47e6bdbb8p1a5b27jsn32c91ff94a65'
SEARCH_TERMS = ['cloud engineer', 'aws cloud support', 'cloud support engineer']
TTL_DAYS = 3

def generate_job_id(title, company):
    raw = f"{title.lower().strip()}-{company.lower().strip()}"
    return hashlib.md5(raw.encode()).hexdigest()

def job_already_seen(job_id):
    try:
        response = table.get_item(Key={'jobId': job_id})
        return 'Item' in response
    except Exception as e:
        print(f'DynamoDB check error: {e}')
        return False

def save_job(job_id, title, company, url):
    expiry = int(time.time()) + (TTL_DAYS * 24 * 60 * 60)
    table.put_item(Item={
        'jobId': job_id,
        'title': title,
        'company': company,
        'url': url,
        'alertedAt': datetime.utcnow().isoformat(),
        'ttl': expiry
    })

def send_email(title, company, location, url):
    ses.send_email(
        Source=ALERT_EMAIL,
        Destination={'ToAddresses': [ALERT_EMAIL]},
        Message={
            'Subject': {'Data': f'New Job Alert: {title} at {company}'},
            'Body': {
                'Text': {'Data': f'Role: {title}\nCompany: {company}\nLocation: {location}\n\nApply: {url}'},
                'Html': {'Data': f'<h2>{title}</h2><p><b>{company}</b> — {location}</p><p><a href="{url}">Apply Now</a></p>'}
            }
        }
    )

def search_jobs(search_term):
    encoded_term = urllib.parse.quote(search_term)
    url = f"https://jsearch.p.rapidapi.com/search?query={encoded_term}&page=1&num_pages=1&date_posted=today"
    req = urllib.request.Request(url, headers={
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            return data.get('data', [])
    except Exception as e:
        print(f'JSearch error for {search_term}: {e}')
        return []

def lambda_handler(event, context):
    new_jobs_found = 0
    print(f'Job scan started: {datetime.utcnow().isoformat()}')

    for search_term in SEARCH_TERMS:
        print(f'Searching: {search_term}')
        jobs = search_jobs(search_term)
        print(f'Found {len(jobs)} results for: {search_term}')

        for job in jobs[:5]:
            title = job.get('job_title', 'Unknown Title')
            company = job.get('employer_name', 'Unknown Company')
            location = job.get('job_city', '') + ', ' + job.get('job_state', '')
            url = job.get('job_apply_link', 'https://www.indeed.com')

            job_id = generate_job_id(title, company)

            if not job_already_seen(job_id):
                # send_text(title, company, location, url)
                send_email(title, company, location, url)
                save_job(job_id, title, company, url)
                new_jobs_found += 1
                print(f'Alert sent: {title} at {company}')
            else:
                print(f'Already seen: {title} at {company}')

    if new_jobs_found == 0:
        print('No new jobs found. No notifications sent.')
    else:
        print(f'Scan complete. {new_jobs_found} new alerts sent.')

    return {'statusCode': 200, 'body': json.dumps({'newJobs': new_jobs_found})}