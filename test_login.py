"""
This module contains users test scripts.
"""
import pytest
from rest_framework.test import APIClient
from secrets_vault.models import Role, User
from secrets_vault.test_utils import login_as_super_admin, login_as_non_admin

@pytest.fixture
def create_users(db):
    """
    This method contain fixture
    """
    super_admin_role = Role.objects.create(name = 'Super Admin')
    non_admin_role = Role.objects.create(name = 'Non Admin')
    na_role = Role.objects.create(name = 'N/A')

    super_admin_user = User.objects.create(username='jwilson', osi_one_id=9826, ad_username='JOHN',
                                    first_name='JOHN', last_name='WILSON', role=super_admin_role,
                                    email_address='jwilson@osidigital.com')
    non_admin_user = User.objects.create(username='ksingh', ad_username='KARAN', first_name='KARAN',
                                         last_name='SINGH', email_address='ksingh@osidigital.com',
                                         role=non_admin_role)
    na_user = User.objects.create(username='x', ad_username='X', first_name='X', last_name='X',
                                  email_address='x@osidigital.com', role=na_role)
    james = User.objects.create(username='jwatson', ad_username='JAMES', first_name='JAMES',
                                last_name='WATSON', email_address='jwatson@osidigital.com',
                                role=non_admin_role)
    data = {
        'super_admin_role' : super_admin_role,
        'non_admin_role' : non_admin_role,
        'na_role' : na_role,
        'james' : james,
        'super_admin_user' : super_admin_user,
        'non_admin_user' : non_admin_user,
        'na_user' : na_user
        }
    return data






# Login as X
def login_as_na():
    """
    This method for login a N/A user
    """

    client = APIClient()
    url = "/api/v1/login/"
    data = {"userName": "x",
            "password":"dfadfadfasdfsda"}
    response=client.post(url, data=data)
    return response.json()

def login():
    """
    This method for login
    """
    client = APIClient()
    url = "/api/v1/login/"
    data = {"userName": "naveen",
            "password":"dfadfadfasdfsda"}
    response=client.post(url, data=data)

    return response.json()


#TS001
@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.django_db
def test_get_existing_user(create_users):
    """
    This method is to test get existing user.
    """

    client=APIClient()

    session_user=login_as_super_admin()

    data=create_users

    user=data['james']

    url=f'/api/v1/users/{user.id}/'

    headers = {"Authorization": session_user.get("auth_token")}

    response=client.get(url, headers=headers)

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    user=response.json()

    assert 'username' in user

    assert user['roles']['base_role_id'] == 2

#TS002
def test_get_non_existing_user(create_users):
    """
    This method is to test get non existing user.
    """

    client=APIClient()

    session_user=login_as_super_admin()

    user_id = 999999

    url=f'/api/v1/users/{user_id}/'

    headers = {"Authorization": session_user.get("auth_token")}

    response=client.get(url, headers=headers)

    assert response.status_code == 404, f"Expected status code 404 but got {response.status_code}"


#TS003
@pytest.mark.django_db
def test_update_user_with_id(create_users):
    """
    This method is to test update user with id.
    """
    client=APIClient()
    session_user=login_as_super_admin()

    data=create_users

    user=data['james']

    url = f'/api/v1/users/{user.id}/'

    headers = {"Authorization": session_user.get("auth_token")}

    response=client.get(url)

    data = {
        'roles': {
            'base_role_id': user.role.id
        }
    }
    response = client.put(url, data, format='json', headers=headers)

    assert response.status_code == 200

    assert User.objects.get(username='jwatson').pk == 4

#TS004
@pytest.mark.django_db
def test_not_update_active_user_data(create_users):
    """
    This method is to test not update active user data.
    """

    client=APIClient()

    session_user=login_as_super_admin()

    data=create_users

    user=data['james']

    url = f'/api/v1/users/{user.id}/'

    headers = {"Authorization": session_user.get("auth_token")}

    data = {
        'username': 'sgreen',
        'first_name': 'cameron',
        'last_name': 'green',
        'email_address': 'sgreen@osidigitall.com'
    }

    response = client.put(url, data, headers=headers)

    assert response.status_code == 403

    error_response = response.json()

    assert 'error_code' in error_response

    assert 'error_message' in error_response

#TS005
@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.django_db
def test_delete_with_user_id(create_users):
    """
    This method is to test delete with user id.
    """

    client = APIClient()

    session_user=login_as_super_admin()

    data=create_users

    user=data['james']

    url = f'/api/v1/users/{user.id}/'

    headers = {"Authorization": session_user.get("auth_token")}

    response = client.delete(url, headers=headers)

    assert response.status_code == 200
    assert User.objects.get(pk=user.id).deleted_at is not None

#TS006
@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.django_db
def test_update_disabled_user_data(create_users):
    """
    This method is to test update disabled user data.
    """

    client=APIClient()

    session_user=login_as_super_admin()

    data=create_users

    user=data['james']

    url = f'/api/v1/users/{user.id}/'

    headers = {"Authorization": session_user.get("auth_token")}

    user=User.objects.get(username='jwatson')
    user.inactivate()

    data = {
        'username': 'jgill',
        'first_name': 'Jack',
        'last_name': 'Gill',
        'email_address': 'jgill@osidigital.com'
    }

    response = client.put(url, data, format='json', headers=headers)

    assert response.status_code == 403

    error_response = response.json()

    assert error_response['error_code']==1027

    assert error_response['error_message'] == 'Cannot update the disabled user details.'

#TS007
@pytest.mark.django_db
def test_update_disabled_user_to_active(create_users):
    """
    This method is to test update disabled user to active.
    """

    client=APIClient()

    session_user=login_as_super_admin()

    data=create_users

    user=data['james']
    headers = {"Authorization": session_user.get("auth_token")}
    url = f'/api/v1/users/{user.id}/'
    response = client.delete(url)
    data = {
        'deleted_at': None,
        'roles': {
            'base_role_id': user.role.id
        }
    }

    response = client.put(url, data, format='json', headers=headers)

    assert response.status_code == 200

    assert user.deleted_at is None

    assert user.role.pk == 2

#TS008
@pytest.mark.django_db
def test_update_self_superadmin_user_to_nonadmin(create_users):
    """
    This method is to test update self superadmin user to nonadmin.
    """

    client=APIClient()

    session_user=login_as_super_admin()

    data=create_users

    user=data['super_admin_user']
    headers = {"Authorization": session_user.get("auth_token")}

    url = f'/api/v1/users/{user.id}/'

    data = {
         'roles': {
            'base_role_id': 2
        }
    }

    response = client.put(url, data, format='json', headers=headers)

    assert response.status_code == 403

    assert user.role.pk == 1

    error_response = response.json()

    assert 'error_code' in error_response

    assert 'error_message' in error_response

