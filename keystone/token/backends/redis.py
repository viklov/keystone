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

import redis

from keystone import config
from keystone import exception
from keystone import token

CONF = config.CONF
config.register_str('host', group='redis', default='localhost:6379')
config.register_str('db', group='redis', default='0')


class Token(token.Driver):

    def __init__(self, client=None):
        self.host, self.port = CONF.redis.host.split(':')
        self.r_client = client or redis.StrictRedis(self.host, self.port, CONF.redis.db)

    def get_token(self, token_id):
        token = self.r_client.get(token_id)
        if not token:
            raise exception.TokenNotFound(token_id=token_id)
        return token

    def create_token(self, token_id, data):
        expires = data.get('expires') or self._get_default_expire_time()
        try:
            self.r_client.set(token_id, data)
            self.r_client.expire(token_id, expires)
        except Exception:
            return None
        return data

    def delete_token(self, token_id):
        if not self.r_client.delete(token_id):
            raise exception.TokenNotFound(token_id=token_id)

    def list_tokens(self, user_id):
        tokens_lst = []
        for key in self.r_client.keys():
            if user_id == self.r_client.get(key)['user']:
                tokens_lst.append(self.r_client.get(key))
        return tokens_lst
