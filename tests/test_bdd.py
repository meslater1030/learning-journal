# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pytest_bdd import scenario, given, when, then
from cryptacular.bcrypt import BCRYPTPasswordManager
import journal
import os
from pyramid import testing

os.environ['TESTING'] = "True"


@scenario('features/edit.feature', 'Editing')
def test_detail():
    pass


@scenario('features/homepage.feature',
          'The Homepage lists entries for anonymous users')
def test_home_listing_as_anon():
    pass


@given('an anonymous user')
def an_anonymous_user(app):
    pass


@given('a list of 3 entries')
def create_entries(db_session):
    title_template = "Title {}"
    text_template = "Entry Text{}"
    for x in range(3):
        journal.Entry.write(
            title=title_template.format(x),
            text=text_template.format(x),
            session=db_session)
        db_session.flush()


@when('the user vists the homepage')
def go_to_homepage(homepage):
    pass


@then('they see a list of 3 entries')
def check_entry_list(homepage):
    html = homepage.html
    entries = html.find_all('article', class_='entry')
    assert len(entries) == 3


@scenario('features/homepage.feature', 'Markdown')
def test_markdown():
    pass


@scenario('features/homepage.feature', 'Colorized Code')
def test_color():
    pass


@given('an author')
def check_authorization(homepage, request):
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


@when('the user adds an entry')
def test_entry(db_session):
    data = {u'text': u'#test text\n**bold**```print "Hello World"'
            '```', u'title': u"Title"}
    journal.Entry.write(session=db_session, **data)
    db_session.flush()


@then('that entry fomats with markdown')
def format_markdown(db_session, app):
    response = app.get('/')
    actual = response.body
    expected = u'<h1>test text</h1>'
    bold = u'<strong>bold</strong>'
    assert expected in actual
    assert bold in actual


@then('that entry shows color in the code')
def format_code(db_session, app):
    response = app.get('/')
    actual = response.body
    pygments = (u'<div class="highlight"><pre><span class="k">print</span> '
                u'<span class="s">&quot;Hello World&quot;</span>\n</pre>'
                u'</div>\n\n')
    assert pygments in actual


@then('that entry can be edited')
def edit_code(db_session, app):
    journal.Entry.edit(session=db_session, text=u'better text',
                       title=u'title', id='1')
    db_session.flush()
    response = app.get('/')
    actual = response.body
    expected = u"better text"
    assert expected in actual
