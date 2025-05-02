"""
This module contains login test scripts.
"""
import json
import pytest
from rest_framework.test import APIClient
from secrets_vault.models import User, Role, AuditLog
from datetime import datetime


@pytest.fixture
def create_and_delete_user():
    """
    This method contains fixtures.
    """

    Role.objects.create(name="Super Admin")
    role2=Role.objects.create(name='Non Admin')
    role3=Role.objects.create(name='N/A')

    user1 = User.objects.create(username='jwilson', osi_one_id=9826, ad_username='auser1',
                                first_name='JOHN', last_name='WILSON', role=role2)
    user2 = User.objects.create(username='ksingh', osi_one_id=9831, ad_username='auser3',
                                first_name='KARAN', last_name='SINGH', role=role2)
    user3 = User.objects.create(username='jwatson', osi_one_id=9829, ad_username='auser1',
                                first_name='JAMES', last_name='WATSON', role=role2)
    user4 = User.objects.create(username='rjohnson', osi_one_id=8197, ad_username='auser3',
                                first_name='ROBIN', last_name='JOHNSON', role=role2)
    user5 = User.objects.create(username='naveen', osi_one_id=714, ad_username='auser3',
                                first_name='RAM', last_name='SINGH', role=role2)
    user6 = User.objects.create(username='N/A', ad_username='auser3', first_name='X',
                                last_name='X', role=role3)

    yield {
        'user1':user1,
        'user2':user2,
        'user3':user3,
        'user4':user4,
        'user5':user5,
        'user6':user6
    }

# ==============================================================================
@pytest.mark.django_db
def test_user_login_valid_credentials(create_and_delete_user):
    """
    Test case for login.
    """

    client=APIClient()

    data={
        'userName':'jwilson',
        'password' : '17PT050nLAChuhJzVZ6RqQ=='
    }

    url='/api/v1/login/'

    response=client.post(url, data=json.dumps(data), content_type='application/json')

    assert response.status_code == 200, f'expected status code 200, got \
                                        {response.status_code} status code'

    response_json=response.json()

    user_obj=User.objects.get(id=response_json.get('id'))

    assert 'username' in response_json

    assert user_obj.role.name == 'Non Admin'

    assert AuditLog.objects.get(performed_by_user=user_obj).action_type == 'Login Success'

    assert 'auth_token' in response_json

# ========================================================================================
@pytest.mark.django_db
def test_user_login_username_uppercase(create_and_delete_user):
    """
    Test case for login.
    """

    client=APIClient()

    data={
        'userName':'JWILSON',
        'password' : '17PT050nLAChuhJzVZ6RqQ=='
    }

    url='/api/v1/login/'

    response=client.post(url, data=json.dumps(data), content_type='application/json')

    assert response.status_code == 200, f'expected status code 200, got \
                                            {response.status_code} status code'

    response_json=response.json()

    user_obj=User.objects.get(id=response_json.get('id'))

    assert 'username' in response_json

    assert user_obj.role.name == 'Non Admin'

    assert AuditLog.objects.get(performed_by_user=user_obj).action_type == 'Login Success'

    assert 'auth_token' in response_json

# ========================================================================================
@pytest.mark.django_db
def test_user_login_username_mixedcase(create_and_delete_user):
    """
    Test case for login.
    """

    client=APIClient()

    data={
        'userName':'JwIlSoN',
        'password' : '17PT050nLAChuhJzVZ6RqQ=='
    }

    url='/api/v1/login/'

    response=client.post(url, data=json.dumps(data), content_type='application/json')

    assert response.status_code == 200, f'expected status code 200, got \
                                            {response.status_code} status code'

    response_json=response.json()

    user_obj=User.objects.get(id=response_json.get('id'))

    assert 'username' in response_json

    assert user_obj.role.name == 'Non Admin'

    assert AuditLog.objects.get(performed_by_user=user_obj).action_type == 'Login Success'

    assert 'auth_token' in response_json

# =======================================================================================
@pytest.mark.django_db
def test_user_login_username_blankspaces(create_and_delete_user):
    """
    Test case for login.
    """

    client=APIClient()

    data={
        'userName':' jwilson ',
        'password' : '17PT050nLAChuhJzVZ6RqQ=='
    }

    url='/api/v1/login/'

    response=client.post(url, data=json.dumps(data), content_type='application/json')

    assert response.status_code == 200, f'expected status code 200, got \
                                            {response.status_code} status code'

    response_json=response.json()

    user_obj=User.objects.get(id=response_json.get('id'))

    assert 'username' in response_json

    assert user_obj.role.name == 'Non Admin'

    assert AuditLog.objects.get(performed_by_user=user_obj).action_type == 'Login Success'

    assert 'auth_token' in response_json

# ========================================================================================
@pytest.mark.django_db
def test_user_login_incorrect_username(create_and_delete_user):
    """
    Test case for login.
    """

    client=APIClient()

    data={
        'userName':'incorrect_username',
        'password' : '17PT050nLAChuhJzVZ6RqQ=='
    }

    url='/api/v1/login/'

    response=client.post(url, data=json.dumps(data), content_type='application/json')

    assert response.status_code == 404, f'expected status code 404, got \
                                            {response.status_code} status code'

    response_json=response.json()
    assert response_json.get('errorMessage') == "Account isn't active in OSIONE"
    assert response_json.get('errorCode') == 'ERR_1028'
