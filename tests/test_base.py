# coding: utf-8

from zerqu.versions import API_VERSION
from zerqu.models import db, User
from ._base import TestCase


class TestAPI(TestCase):
    def test_get_api_index(self):
        rv = self.client.get('/api/')
        assert API_VERSION in rv.data


class TestModel(TestCase):
    def test_model_events(self):
        user = User(username='hello', email='hello@gmail.com')
        db.session.add(user)
        db.session.commit()

        # get from database
        assert user == User.cache.get(user.id)
        # get from cache
        cached_user = User.cache.get(user.id)
        assert user != cached_user
        assert user.id == cached_user.id

        # update cache
        user.username = 'jinja'
        db.session.add(user)
        db.session.commit()
        assert User.cache.get(user.id).username == 'jinja'

        # delete cache
        db.session.delete(user)
        db.session.commit()
        assert User.cache.get(user.id) is None

    def test_get_many_dict(self):
        assert User.cache.get_dict([]) == {}

        for i in range(10):
            user = User(username='foo-%d' % i, email='foo-%d@gmail.com' % i)
            db.session.add(user)
        db.session.commit()

        first_id = User.cache.filter_first(username='foo-0').id
        idents = [first_id + i for i in range(10)]
        missed = User.cache.get_dict(idents)
        assert len(missed.keys()) == 10

        cached = User.cache.get_dict(idents)
        assert missed.keys().sort() == cached.keys().sort()

        missed_names = [o.username for o in missed.values()]
        cached_names = [o.username for o in User.cache.get_many(idents)]
        assert missed_names.sort() == cached_names.sort()