# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

from webtest.app import AppError

from storyboard.db.models import User
from storyboard.tests import base


class TestProjects(base.FunctionalTest):

    def setUp(self):
        super(TestProjects, self).setUp()

        self.resource = '/projects'

        self.project_01 = {
            'name': 'test-project',
            'description': 'some description'
        }

        self.load_data([
            User(id=1,
                 username='superuser',
                 email='superuser@example.com',
                 full_name='Super User',
                 is_superuser=True)
        ])
        su_token = self.build_access_token(1)
        self.default_headers['Authorization'] = 'Bearer %s' % (
            su_token.access_token)

    def test_projects_endpoint(self):
        response = self.get_json(path=self.resource)
        self.assertEqual([], response)

    def test_create(self):

        response = self.post_json(self.resource, self.project_01)
        project = json.loads(response.body)

        self.assertEqual(self.project_01['name'], project['name'])
        self.assertEqual(self.project_01['description'],
                         project['description'])

    def test_create_invalid(self):

        invalid_project = self.project_01.copy()
        invalid_project["name"] = "name with spaces"

        self.assertRaises(AppError, self.post_json, self.resource,
                          invalid_project)

    def test_update(self):
        response = self.post_json(self.resource, self.project_01)
        original = json.loads(response.body)

        delta = {
            'id': original['id'],
            'name': 'new-name',
            'description': 'new description'
        }

        url = "/projects/%d" % original['id']
        response = self.put_json(url, delta)
        updated = json.loads(response.body)

        self.assertEqual(original['id'], updated['id'])

        self.assertNotEqual(original['name'], updated['name'])
        self.assertNotEqual(original['description'],
                            updated['description'])

    def test_update_invalid(self):
        response = self.post_json(self.resource, self.project_01)
        original = json.loads(response.body)

        delta = {
            'id': original['id'],
            'name': 'new-name is invalid!',
        }

        url = "/projects/%d" % original['id']

        # check for invalid characters like space and '!'
        self.assertRaises(AppError, self.put_json, url, delta)

        delta["name"] = "a"

        # check for a too short name
        self.assertRaises(AppError, self.put_json, url, delta)
