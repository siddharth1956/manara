from app.services.copernicus_service import get_access_token

print("=" * 50)
print("Testing Copernicus Login")
print("=" * 50)

token = get_access_token()

print("\nLogin Successful!")
print("Access Token Length:", len(token))
print("\nFirst 30 characters:")
print(token[:30] + "...")
