# coding: utf-8
get_ipython().magic(u'ls ')
import journal
journal.DATABASE_URL
from journal import DATABASE_URL
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
engine = create_engine(DATABASE_URL, echo=True)
engine
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bine=engine)
session = Session()
Session = sessionmaker(bind=engine)
session = Session()
session.bind
from journal import Entry
from__future__ import unicode_literals
from __future__ import unicode_literals
e1 = Entry()
e1.title = "There's something about sqlalchemy"
e1.text = "It's such a wonderful system for interacting with a database"
e1
session.dirty
session.add(e1)
session.new()
session.new
session.commit()
session.query
session.query(Entry)
results = session.query(Entry)
results
dir(results)
results.query
results.sql
str(results)
results = results.all()
results
type(results)
for entry in results:
    print entry.title
    print"\t{}".format(entry.text)
    
for entry in results:
    print entry.title
    print"\t{}".format(entry.text)
results = session.query(Entry).order_by(Entry.title)
results
results = session.query(Entry).order_by(Entry.title).all()
for entry in results:
    print "{}: {}".format(entry.id, entry.title)
    print "\t{}".format(entry.text)
    
results = session.query(Entry).order_by(Entry.id, reverse=True)
results = session.query(Entry).order_by(Entry.created.desc()).all()
for entry in results:
    print "{}: {}".format(entry.id, entry.title)
    print "\t{}".format(entry.text)
    
type(results)
results = session.query(Entry).order_by(Entry.created.desc())
type(results)
str(results)
results.all()
type(results)
results.count()
results = session.query(Entry).get(1)
results
results.id
results = session.query(Entry).get(4)
results
type(results)
results = session.query(Entry)
results
dir(results)
results.one()
results = session.query(Entry)
results = results.filter(Entry.id == 1)
results.one()
str(results)
results.one()
my_entry = _
my_entry
my_entry
my_entry.title = "It's time for number Two!"
my_entry
session.dirty()
session.dirty
session.commit()
get_ipython().magic(u'save sql_exploration.py 1-77')
