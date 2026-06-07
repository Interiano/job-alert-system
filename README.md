Job Search Bot

serverless job alert system that runs every morning at 9am. searches
multiple job boards for cloud engineering positions, and sends you both a text
and email when new jobs are found

after 3 days, dynamodb auto expires job record

create an account with rapidapi.com if you havent already
search for jsearch
subscribe

X-RAPIDAPI-Key: 

create table
command:
aws dynamodb create-table `
  --table-name job-alerts `
  --attribute-definitions AttributeName=jobId,AttributeType=S `
  --key-schema AttributeName=jobId,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region us-east-1

enable TTL
command:
aws dynamodb update-time-to-live `
  --table-name job-alerts `
  --time-to-live-specification Enabled=true,AttributeName=ttl `
  --region us-east-1

register under SES. dont use production.
verify email with link in email
command:
aws ses verify-email-identity `
  --email-address YOUR_EMAIL_ADDRESS ` <--your email
  --region us-east-1

also register as sender unless you verified with email
command:
aws ses verify-email-identity `
  --email-address YOUR_EMAIL_ADDRESS ` <-- your email
  --region us-east-1

SNS setup

create SNS topic
command:
aws sns create-topic --name job-alerts-topic --region us-east-1

collect TopicArn: "TopicArn": "arn:aws:sns:us-east-1:343253677879:job-alerts-topic"

subscribe your phone number
command:
aws sns subscribe `
  --topic-arn YOUR_SNS_TOPIC_ARN `
  --protocol sms `
  --notification-endpoint YOUR_PHONE_NUMBER `
  --region us-east-1

test SNS
command:
aws sns publish `
  --topic-arn YOUR_SNS_TOPIC_ARN `
  --message 'Job Alert System connected. You will receive new job notifications here.' `
  --region us-east-1

hit a snap, i have to wait for SNS to validate my phone number. I'm in sandbox mode and
have to request a quota increase. It will take me from sandbox to production mode.
continue with just email. 
will add feature for text later

created the iam role
created it on console
added the trusted policy type: aws service
use case: lambda
added 4 policies:
  AmazonDynamoDBFullAccess
  AmazonSNSFullAccess
  AmazonSESFullAccess
  AWSLambdaBasicExecutionRole

named the role

created the lambda function
selected the iam role

had to verify my email
under lambda and the function specificly
i tested the run and it was successfull

they ended up in spam
had to validate the sender sinces its SES

now to create the method to operate at 9am
eventbridge
set it for 9am
followed the cron expression for 9am

