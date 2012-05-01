from datetime import datetime, timedelta

import makerbase
from makerbase.models import *


"""
user: {
    'id':
    'name':
    'avatar_url':
    'html_url':
    <link to person?>
}

maker: {
    'name':
    'avatar_url':
    'html_url':
}

project: {
    'name':
    'description':
    'avatar_url':
    'html_url':
}

participation: {
    <link to person>
    <link to project>
    'role': "140 char description"
    'start_year': 2012
    'start_month': 0
    'end_year': 2012
    'end_year': 1
}

history: {
    <link to user>
    'action': '[create edit]'
    'reason': "140 char description"
    'when': <iso8601 timestamp>
    'new': { obj data? }
}
"""


def blit(cls, ident):
    obj = cls.get(ident)
    if obj is not None:
        obj.delete()


def empty_bucket(cls):
    keys = cls.get_bucket().get_keys()
    for key in keys:
        blit(cls, key)


for cls in (Project, Maker, Participation, History):
    empty_bucket(cls)


def now():
    somewhen = datetime(2012, 4, 11, 13, 0, 0)
    while True:
        yield somewhen.isoformat()
        somewhen += timedelta(minutes=1)

now = now()



editor = User(
    'github:markpasc',
    name='Mark Paschal',
    avatar_url='https://secure.gravatar.com/avatar/30e5bdec1073df6350d27b8145bf0dab?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-140.png',
    html_url='https://github.com/markpasc',
)
editor.save()

mlkshk = Project(
    'mlkshk',
    name='MLKSHK',
    description='A site for sharing pictures.',
    html_url='http://mlkshk.com/',
    avatar_url='https://mlkshk.com/r/2NOE',
)
mlkshk.save()

h = History(
    action='addproject',
    reason='new project',
    when=now.next(),
    old_data={},
    new_data=mlkshk.get_entity_data(),
).add_link(editor, tag='user').add_link(mlkshk, tag='project')
h.save()

mlkshk.add_link(h, tag='history').save()

me = Maker(
    'markpasc',
    name='Mark Paschal',
    html_url='http://markpasc.org/mark/',
    avatar_url='https://secure.gravatar.com/avatar/30e5bdec1073df6350d27b8145bf0dab?s=140&d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-140.png',
)
me.save()

h = History(
    action='addmaker',
    reason='new maker',
    when=now.next(),
    old_data={},
    new_data=me.get_entity_data(),
).add_link(editor, tag='user').add_link(me, tag='maker')
h.save()

me.add_link(h, tag='history').save()

andre = Maker(
    'torrez',
    name='Andre Torrez',
    html_url='http://torrez.org/',
    avatar_url='https://si0.twimg.com/profile_images/1788942159/black-log.gif',
)
andre.save()

h = History(
    action='addmaker',
    reason='new maker',
    when=now.next(),
    old_data={},
    new_data=andre.get_entity_data(),
).add_link(editor, tag='user').add_link(andre, tag='maker')
h.save()

andre.add_link(h, tag='history').save()

amber = Maker(
    'amber',
    name='Amber Costley',
    html_url='http://ambercostley.com/',
    avatar_url='https://si0.twimg.com/profile_images/1452719858/twit.jpg',
)
amber.save()

h = History(
    action='addmaker',
    reason='new maker',
    when=now.next(),
    old_data={},
    new_data=amber.get_entity_data(),
).add_link(editor, tag='user').add_link(amber, tag='maker')
h.save()

amber.add_link(h, tag='history').save()

party = Participation(
    role='Creator and programmer',
    start_month=11,
    start_year=2010,
)
party.save()
party.add_link(mlkshk, tag='project')
party.add_link(andre, tag='maker')
party.save()

andre.add_link(party, tag='participation')
andre.save()

mlkshk.add_link(party, tag='participation')
mlkshk.save()

h = History(
    action='addparty',
    reason='worked with andre on that',
    when=now.next(),
    old_data={},
    new_data=party.get_entity_data(),
).add_link(editor, tag='user').add_link(andre, tag='maker').add_link(mlkshk, tag='project')
h.save()

andre.add_link(h, tag='history').save()
mlkshk.add_link(h, tag='history').save()

party = Participation(
    role='Creator and designer',
    start_month=11,
    start_year=2010,
)
party.save()
party.add_link(mlkshk, tag='project')
party.add_link(amber, tag='maker')
party.save()

amber.add_link(party, tag='participation')
amber.save()

mlkshk.add_link(party, tag='participation')
mlkshk.save()

h = History(
    action='addparty',
    reason='worked with amber on that',
    when=now.next(),
    old_data={},
    new_data=party.get_entity_data(),
).add_link(editor, tag='user').add_link(amber, tag='maker').add_link(mlkshk, tag='project')
h.save()

amber.add_link(h, tag='history').save()
mlkshk.add_link(h, tag='history').save()

party = Participation(
    role='Contract API programmer & test writer',
    start_month=4,
    start_year=2011,
    end_month=5,
    end_year=2011,
)
party.save()
party.add_link(me, tag='maker')
party.add_link(mlkshk, tag='project')
party.save()

me.add_link(party, tag='participation')
me.save()

mlkshk.add_link(party, tag='participation')
mlkshk.save()

h = History(
    action='addparty',
    reason='i worked on that',
    when=now.next(),
    old_data={},
    new_data=party.get_entity_data(),
).add_link(editor, tag='user').add_link(me, tag='maker').add_link(mlkshk, tag='project')
h.save()

me.add_link(h, tag='history').save()
mlkshk.add_link(h, tag='history').save()

anildash = Maker(
    'anildash',
    name='Anil Dash',
    html_url='http://dashes.com/anil/about.html',
    avatar_url='https://si0.twimg.com/profile_images/1364557668/image_reasonably_small.jpg',
)
anildash.save()

h = History(
    action='addmaker',
    reason='new maker',
    when=now.next(),
    old_data={},
    new_data=anildash.get_entity_data(),
).add_link(editor, tag='user').add_link(anildash, tag='maker')
h.save()

anildash.add_link(h, tag='history').save()
