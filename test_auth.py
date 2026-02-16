import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.auth import _hash_password, _verify_password, get_user, authenticate_user

print("=" * 50)
print("Testing Auth Module")
print("=" * 50)

# Test password hashing
password = "test123"
hashed = _hash_password(password)
print(f"\n1. Password Hashing Test")
print(f"   Password: {password}")
print(f"   Hashed: {hashed[:50]}...")

# Test password verification
result = _verify_password(password, hashed)
print(f"\n2. Password Verification Test")
print(f"   Verify correct password: {result}")

result_wrong = _verify_password("wrongpassword", hashed)
print(f"   Verify wrong password: {result_wrong}")

# Test user retrieval
print(f"\n3. User Retrieval Test")
user = get_user("admin")
print(f"   User found: {user is not None}")
if user:
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")

# Test authentication
print(f"\n4. Authentication Test")
auth_user = authenticate_user("admin", "admin123")
print(f"   Auth with correct password: {auth_user is not None}")

auth_user_wrong = authenticate_user("admin", "wrongpassword")
print(f"   Auth with wrong password: {auth_user_wrong is not None}")

print("\n" + "=" * 50)
print("All tests completed!")
print("=" * 50)
