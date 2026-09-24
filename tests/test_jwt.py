import uuid

from doc_processor.core.jwt import create_access_token

user_id = uuid.uuid4()

token = create_access_token(user_id)

print("User ID:", user_id)
print("Token:", token)