import boto3
import urllib3
# Define URL
url = 'https://coronavirus.utah.gov/latest/'
# Set up http request maker thing
http = urllib3.PoolManager()
# S3 object to store the last call
bucket_name = 'scohard-covid19'
file_name = 'current_webpage.txt'
object_s3 = boto3.resource('s3') \
                 .Bucket(bucket_name) \
                 .Object(file_name)
# List of phone numbers to send to
phone_numbers = ['+17032589744']
# Connect to AWS Simple Notification Service
sns_client = boto3.client('sns')
def lambda_handler(event, context):
    
    # Ping website
    resp = http.request('POST',url)
    new_page = resp.data
    
    # read in old results
    old_page = object_s3.get().get('Body').read()
    
    if new_page == old_page:
        print("No new updates.")
    else:
        print("-- New Update --")
        
        # Loop through phone numbers
        for cell_phone_number in phone_numbers:
            try:
                # Try to send a text message
                sns_client.publish(
                    PhoneNumber=cell_phone_number,
                    Message= f'Utah COVID19 Update: {url}',
                )
                print(f"Successfuly sent to {cell_phone_number}")
            except:
                print(f"FAILED TO SEND TO {cell_phone_number}")
        
        # Write new data to S3
        object_s3.put(Body = new_page)
        print("Successfully wrote new data to S3")
        
    print("done")
    return None