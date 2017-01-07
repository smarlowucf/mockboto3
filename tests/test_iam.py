#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3

from mockboto3.core.exceptions import MockBoto3ClientError
from mockboto3.iam.endpoints import MockIam, mock_iam

from nose.tools import assert_equal, assert_is_not_none, assert_true


class TestIam:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')

    def test_unmocked_operation(self):
        """Test operation not mocked error is returned."""
        msg = 'An error occurred (NoSuchMethod) when calling the ' \
              'CreateGecko operation: Operation not mocked.'

        try:
            mocker = MockIam()
            mocker.mock_make_api_call('CreateGecko',
                                      {'Name': 'gecko'})

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))


class TestUserGroup:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.user = 'John'
        cls.group = 'Admins'

    @mock_iam
    def test_get_user_exception(self):
        """Test get non existent user raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the GetUser' \
              ' operation: The user with name John cannot be found.'

        try:
            # Assert get non existing user exception
            self.client.get_user(UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_list_user_groups_exception(self):
        """Test list non existent user groups raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'ListGroupsForUser operation: The user with name ' \
              'John cannot be found.'

        try:
            # Assert list non existent user groups exception
            self.client.list_groups_for_user(UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_add_user_group_exception(self):
        """Test add user to non existent group raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'AddUserToGroup operation: The user with name John ' \
              'cannot be found.'

        try:
            # Assert add user to non existing group exception
            self.client.add_user_to_group(GroupName=self.group,
                                          UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_delete_user_exception(self):
        """Test delete non existent user raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the' \
              ' DeleteUser operation: The user with name John cannot' \
              ' be found.'

        try:
            # Assert delete non existent user exception
            self.client.delete_user(UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_delete_group_exception(self):
        """Test delete non existent group raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the' \
              ' DeleteGroup operation: The group with name Admins' \
              ' cannot be found.'

        try:
            # Assert delete non existent user exception
            self.client.delete_group(GroupName=self.group)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_remove_user_group_exception(self):
        """Test remove non existent user from group raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the' \
              ' RemoveUserFromGroup operation: The user with name' \
              ' John cannot be found.'

        try:
            # Assert remove non existent user from group exception
            self.client.remove_user_from_group(
                GroupName=self.group,
                UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_user_group(self):
        """Test user and group endpoints."""
        # Create user and attempt to add user to group
        self.client.create_user(UserName=self.user)

        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'AddUserToGroup operation: The group with name ' \
              'Admins cannot be found.'

        try:
            self.client.add_user_to_group(GroupName=self.group,
                                          UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

        # Create group and add user to group
        self.client.create_group(GroupName=self.group)
        self.client.add_user_to_group(GroupName=self.group,
                                      UserName=self.user)

        # Assert user and group exist and assert user in group
        assert_equal(self.client.list_users()['Users'][0]['UserName'],
                     self.user)
        assert_equal(self.client.list_groups()['Groups'][0]['GroupName'],
                     self.group)
        assert_equal(self.group,
                     self.client.list_groups_for_user(
                         UserName=self.user
                     )['Groups'][0]['GroupName'])

        msg = 'An error occurred (EntityAlreadyExists) when calling the ' \
              'CreateGroup operation: Group with name Admins already exists.'

        try:
            # Assert create group exists raises exception
            self.client.create_group(GroupName=self.group)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

        msg = 'An error occurred (EntityAlreadyExists) when calling the ' \
              'CreateUser operation: User with name John already exists.'

        try:
            # Assert create user exists raises exception
            self.client.create_user(UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

        # Get user response
        response = self.client.get_user(UserName=self.user)
        assert_equal(response['User']['UserName'], self.user)

        # List groups for user response
        response = self.client.list_groups_for_user(
            GroupName=self.group,
            UserName=self.user)

        assert_equal(response['Groups'][0]['GroupName'],
                     self.group)
        assert_equal(1, len(response['Groups']))

        # Remove user from group
        self.client.remove_user_from_group(GroupName=self.group,
                                           UserName=self.user)
        assert_equal(0,
                     len(self.client.list_groups_for_user(
                         UserName=self.user)['Groups']))

        # Delete group
        self.client.delete_group(GroupName=self.group)
        assert_equal(0, len(self.client.list_groups()['Groups']))

        # Delete user
        self.client.delete_user(UserName=self.user)
        assert_equal(0, len(self.client.list_users()['Users']))


class TestAccessKey:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.user = 'John'

    @mock_iam
    def test_create_access_key_exception(self):
        """Test create access key for non existent user raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'CreateAccessKey operation: The user with name John' \
              ' cannot be found.'

        try:
            # Assert create access key for non existent user exception
            self.client.create_access_key(UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_delete_access_key_exception(self):
        """Test delete non existent access key raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'DeleteAccessKey operation: The Access Key with id' \
              ' key1234567891234 cannot be found.'

        try:
            # Assert delete non existent access key exception
            self.client.delete_access_key(AccessKeyId='key1234567891234')

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_list_access_key_exception(self):
        """Test list access keys for non existent user raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'ListAccessKeys operation: The user with name John' \
              ' cannot be found.'

        try:
            # Assert list access keys for non existent user exception
            self.client.list_access_keys(UserName=self.user)

        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_access_key(self):
        """Test access key endpoints."""
        self.client.create_user(UserName=self.user)
        response = self.client.create_access_key(
            UserName=self.user
        )

        # Get created key id
        key_id = response['AccessKey']['AccessKeyId']

        # Get user access keys
        response = self.client.list_access_keys(UserName=self.user)

        # Assert id's are equal and keys length is 1
        assert_equal(1, len(response['AccessKeyMetadata']))
        assert_equal(key_id,
                     response['AccessKeyMetadata'][0]['AccessKeyId'])

        # Test GetAccessKeyLastUsed
        last_used = self.client.get_access_key_last_used(
            AccessKeyId=key_id
        )['AccessKeyLastUsed']
        assert_equal('us-west-1', last_used['Region'])
        assert_equal('iam', last_used['ServiceName'])
        assert_is_not_none(last_used['LastUsedDate'])

        # Test UpdateAccessKey
        self.client.update_access_key(AccessKeyId=key_id, Status='Inactive')
        response = self.client.list_access_keys(UserName=self.user)

        assert_equal('Inactive',
                     response['AccessKeyMetadata'][0]['Status'])

        # Delete access key
        self.client.delete_access_key(AccessKeyId=key_id)

        # Confirm deletion
        response = self.client.list_access_keys(UserName=self.user)
        assert_equal(0, len(response['AccessKeyMetadata']))

    def test_test(self):
        """TODO remove for writing tests..."""
        mocker = MockIam()
        mocker.mock_make_api_call('CreateUser',
                                  {'UserName': self.user})
        key_id = mocker.mock_make_api_call(
            'CreateAccessKey',
            {'UserName': self.user}
        )['AccessKey']['AccessKeyId']

        mocker.mock_make_api_call('GetAccessKeyLastUsed',
                                  {'AccessKeyId': key_id})


class TestLoginProfile:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.user = 'John'

    @mock_iam
    def test_create_login_profile_exception(self):
        """Test create login profile already exists raises exception."""
        msg = 'An error occurred (EntityAlreadyExists) when calling the ' \
              'CreateLoginProfile operation: LoginProfile for user with ' \
              'name John already exists.'

        self.client.create_user(UserName=self.user)

        # Create login profile
        self.client.create_login_profile(UserName=self.user,
                                         Password='Password')

        try:
            # Assert create login profile already exists exception
            self.client.create_login_profile(UserName=self.user,
                                             Password='Password')
        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_delete_login_profile_exception(self):
        """Test delete non existent login profile raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'DeleteLoginProfile operation: LoginProfile for user' \
              ' with name John cannot be found.'

        self.client.create_user(UserName=self.user)

        try:
            # Assert delete non existent login profile exception
            self.client.delete_login_profile(UserName=self.user)
        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))

    @mock_iam
    def test_login_profile(self):
        """Test login profile endpoints."""
        self.client.create_user(UserName=self.user)

        # Create login profile
        response = self.client.create_login_profile(UserName=self.user,
                                                    Password='Password')

        assert_equal(self.user,
                     response['LoginProfile']['UserName'])

        # Get login profile
        response = self.client.get_login_profile(UserName=self.user)
        assert_is_not_none(response['LoginProfile']['CreateDate'])

        # Update login profile
        self.client.update_login_profile(UserName=self.user,
                                         PasswordResetRequired=True)

        # Delete profile
        self.client.delete_login_profile(UserName=self.user)

        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'GetLoginProfile operation: LoginProfile for user ' \
              'with name John cannot be found.'

        try:
            self.client.get_login_profile(UserName=self.user)
        except MockBoto3ClientError as e:
            assert_equal(msg, str(e))
