# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cryptacular.bcrypt import BCRYPTPasswordManager
import journal
import os
from pyramid import testing
import pytest
from sqlalchemy.exc import IntegrityError

# all the global variables
os.environ['TESTING'] = "True"
INPUT_BTN = '<input type="submit" value="Share" name="Share"/>'


# all the fixtures

@pytest.fixture(scope='function')
def auth_req(request):
    manager = BCRYPTPasswordManager()
    settings = {
        'auth.username': 'admin',
        'auth.password': manager.encode('secret'),
    }
    testing.setUp(settings=settings)
    req = testing.DummyRequest()

    def cleanup():
        testing.tearDown()

    request.addfinalizer(cleanup)

    return req


@pytest.fixture()
def entry(db_session):
    entry = journal.Entry.write(
        title='Test Title',
        text='Test Entry Text',
        session=db_session
    )
    db_session.flush()
    return entry


# all the tests using the app fixture


def test_permalink_exists(db_session, app):
    """Tests that a new view is generated when a new entry is
    added and that the new view has a permalink based on the
    title of the new entry.
    """
    data = {'text': 'test text', 'title': "Title"}
    journal.Entry.write(session=db_session, **data)
    db_session.flush()
    response = app.get('/1/Title')
    actual = response.body
    expected = 'test text'
    assert expected in actual


def test_markdown(db_session, app):
    """Tests that a new view is generated when a new entry is
    added and that the new view has a permalink based on the
    title of the new entry.
    """
    data = {'text': '#test text\n**bold**', 'title': "Title"}
    journal.Entry.write(session=db_session, **data)
    db_session.flush()
    response = app.get('/')
    actual = response.body
    expected = '<h1>test text</h1>'
    bold = '<strong>bold</strong>'
    assert expected in actual
    assert bold in actual


# def test_editing(db_session, app):
#     """Tests that an existing entry can be edited"""
#     import pdb; pdb.set_trace()
#     journal.Entry.write(session=db_session, text=u'test text', title='title')
#     # journal.Entry.edit(session=db_session, id=2)
#     # db_session.flush()
#     response = app.get('/')
#     actual = response.body
#     expected = u"test text"
#     assert expected not in actual


def test_add_no_params(app):
    try:
        response = app.post('/add', status=500)
    except Exception as e:
        return e
    assert 'IntegrityError' in response.body


def test_empty_listing(app):
    response = app.get('/')
    assert response.status_code == 200
    actual = response.body
    expected = 'No entries here so far'
    assert expected in actual


def test_listing(app, entry):
    response = app.get('/')
    assert response.status_code == 200
    actual = response.body
    for field in ['title', 'text']:
        expected = getattr(entry, field, 'absent')
        assert expected in actual


def login_helper(username, password, app):
    """encapsulate app login for reuse in tests

    Accept all status codes so that we can make assertions in tests
    """
    login_data = {'username': username, 'password': password}
    return app.post('/login', params=login_data, status='*')


def test_login_success(app):
    username, password = ('admin', 'secret')
    redirect = login_helper(username, password, app)
    assert redirect.status_code == 302
    response = redirect.follow()
    assert response.status_code == 200


def test_login_fails(app):
    username, password = ('admin', 'wrong')
    response = login_helper(username, password, app)
    assert response.status_code == 200
    actual = response.body
    assert "Login Failed" in actual
    assert INPUT_BTN not in actual


def test_logout(app):
    # re-use existing code to ensure we are logged in when we begin
    test_login_success(app)
    redirect = app.get('/logout', status="3*")
    response = redirect.follow()
    assert response.status_code == 200


def test_post_to_add_view(app):
    entry_data = {
        'title': 'Hello there',
        'text': 'This is a post',
    }
    response = app.post('/add', params=entry_data, status='3*')
    redirected = response.follow()
    actual = redirected.body
    for expected in entry_data.values():
        assert expected in actual


def test_start_as_anonymous(app):
    response = app.get('/', status=200)
    actual = response.body
    assert INPUT_BTN not in actual

# I made this!


def test_add_exists(app):
    test_login_success(app)
    response = app.get('/add')
    actual = response.body
    assert INPUT_BTN in actual


# all the auth_required tests


def test_do_login_bad_user(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'bad', 'password': 'secret'}
    assert not do_login(auth_req)


def test_do_login_bad_pass(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'admin', 'password': 'wrong'}
    assert not do_login(auth_req)


def test_do_login_missing_params(auth_req):
    from journal import do_login
    for params in ({'username': 'admin'}, {'password': 'secret'}):
        auth_req.params = params
        with pytest.raises(ValueError):
            do_login(auth_req)


def test_do_login_success(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'admin', 'password': 'secret'}
    assert do_login(auth_req)


# all db_session tests


def test_entry_no_title_fails(db_session):
    bad_data = {'text': 'test text'}
    journal.Entry.write(session=db_session, **bad_data)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_read_entries_empty(db_session):
    entries = journal.Entry.all()
    assert len(entries) == 0


def test_read_entries_one(db_session):
    title_template = "Title {}"
    text_template = "Entry Text {}"
    # write three entries, with order clear in the title and text
    for x in range(3):
        journal.Entry.write(
            title=title_template.format(x),
            text=text_template.format(x),
            session=db_session)
        db_session.flush()
    entries = journal.Entry.all()
    assert len(entries) == 3
    assert entries[0].title > entries[1].title > entries[2].title
    for entry in entries:
        assert isinstance(entry, journal.Entry)


def test_write_entry(db_session):
    kwargs = {'title': "Test Title", 'text': "Test entry text"}
    kwargs['session'] = db_session
    # first, assert that there are no entries in the database:
    assert db_session.query(journal.Entry).count() == 0
    # now, create an entry using the 'write' class method
    entry = journal.Entry.write(**kwargs)
    # the entry we get back ought to be an instance of Entry
    assert isinstance(entry, journal.Entry)
    # id and created are generated automatically, but only on writing to
    # the database
    auto_fields = ['id', 'created']
    for field in auto_fields:
        assert getattr(entry, field, None) is None

    # flush the session to "write" the data to the database
    db_session.flush()
    # now, we should have one entry:
    assert db_session.query(journal.Entry).count() == 1

    for field in kwargs:
        if field != 'session' and field != 'text':
            assert getattr(entry, field, '') == kwargs[field]
    # id and created should be set automatically upon writing to db:
    for auto in ['id', 'created']:
        assert getattr(entry, auto, None) is not None
