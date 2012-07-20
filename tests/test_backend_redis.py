# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC
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

import uuid
from datetime import datetime

from keystone import exception
from keystone import test
from keystone.token.backends import redis as redis_token

import test_backend


class FakeRedis(object):
    """Fake Redis minimal implamentation"""

    def __init__(self, *args, **kwargs):
        self.redis = {}

    def set(self, id, data):
        self.redis[id] = data
        return True

    def get(self, id):
        try:
            token = self.redis[id]
            if token['expires'] < datetime.now():
                raise exception.TokenNotFound(token_id=id)
            return token
        except KeyError:
            raise exception.TokenNotFound(token_id=id)

    def delete(self, id):
        try:
            self.redis.pop(id)
            return True
        except KeyError:
            raise exception.TokenNotFound(token_id=id)

    def expire(self, id, expire):
        self.redis[id].update({'expires': expire})


class RedisToken(test.TestCase, test_backend.TokenTests):

    def setUp(self):
        super(RedisToken, self).setUp()
        fake_redis = FakeRedis()
        self.token_api = redis_token.Token(client=fake_redis)

    def test_get_unicode(self):
        token_id = unicode(uuid.uuid4().hex)
        data = {'id': token_id, 'a': 'b'}
        self.token_api.create_token(token_id, data)
        self.token_api.get_token(token_id)