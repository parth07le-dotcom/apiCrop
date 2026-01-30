import vercel_blob
print("Checking for create_upload_url...")
if 'create_upload_url' in dir(vercel_blob):
    print("YES: create_upload_url exists")
else:
    print("NO: create_upload_url missing")
    print(f"Available: {dir(vercel_blob)}")
