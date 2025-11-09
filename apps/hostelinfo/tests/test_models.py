import pytest
from hostelinfo.models import User

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create(
        full_name="Test User",
        gender="male",
        phone="+911234567890",
        email="test@example.com",
        password="password",
        role="owner"
    )
    assert user.email == "test@example.com"
