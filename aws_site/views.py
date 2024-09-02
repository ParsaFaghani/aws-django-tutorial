from django.shortcuts import render
from django.conf import settings as s
import boto3
import datetime
import os

AWS = {
    'endpoint': s.AWS_S3_ENDPOINT_URL,
    'accesskey': s.AWS_ACCESS_KEY_ID,
    'secretkey': s.AWS_SECRET_ACCESS_KEY,
    'bucket': s.AWS_STORAGE_BUCKET_NAME
}


def home(request,dir='/'):
    s3 = boto3.client('s3',
        endpoint_url=AWS['endpoint'],
        aws_access_key_id=AWS['accesskey'],
        aws_secret_access_key=AWS['secretkey']
    )
    bucket_name = AWS['bucket']
    objects = s3.list_objects(Bucket=bucket_name,Prefix=dir, Delimiter='/')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=dir, Delimiter='/')
    print(request.GET.get('dir', ''))
    folders_list = []
    print(dir)
    
    if 'CommonPrefixes' in response:
        # Loop through the prefixes and print their names (folder names)
        for folder in response['CommonPrefixes']:
            folders_list.append({'name':folder['Prefix'].split('/')[-2],'adress':folder['Prefix']})

    files = []
    if 'Contents' in objects:
        for obj in objects['Contents']:
            files.append({
                'name': obj['Key'].split('/')[-1:][0], # Assuming key name as file name
                'adress': obj['Key'],
                'permanent_link': f"{AWS['endpoint']}/{bucket_name}/{obj['Key']}",
                'temporary_link': s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': obj['Key']},
                    ExpiresIn=3600  # 1 hour expiry
                )
            })
    else:
        files.append({'name': 'no file', 'permanent_link': '', 'temporary_link': ''})
    if dir != '/':
        print(os.path.dirname(dir.rstrip('/')))
        parent = os.path.dirname(dir.rstrip('/'))
    else:
        parent = None
    return render(request,'home.html',{'files': files,'folders_list':folders_list,'objects':objects, 'parent':parent})