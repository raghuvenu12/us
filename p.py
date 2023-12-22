from google.cloud import storage

storage_client = storage.Client("/Users/raghunandanvenugopal/Downloads/us/molten-complex-408603-13e3b41bd520.json")
print(storage_client)
bucket = storage_client.get_bucket("bsueful_social_profile")
print(bucket)