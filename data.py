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
"""


def blit(cls, ident):
    obj = cls.get(ident)
    if obj is not None:
        obj.delete()


blit(Project, 'mlkshk')
mlkshk = Project(
    'mlkshk',
    name='MLKSHK',
    description='A site for sharing pictures.',
    html_url='http://mlkshk.com/',
    avatar_url='https://mlkshk.com/r/2NOE',
)
mlkshk.save()

blit(Maker, 'markpasc')
me = Maker(
    'markpasc',
    name='Mark Paschal',
    html_url='http://markpasc.org/mark/',
    avatar_url='https://secure.gravatar.com/avatar/30e5bdec1073df6350d27b8145bf0dab?s=140&d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-140.png',
)
me.save()

blit(Maker, 'torrez')
andre = Maker(
    'torrez',
    name='Andre Torrez',
    html_url='http://torrez.org/',
    avatar_url='https://si0.twimg.com/profile_images/1788942159/black-log.gif',
)
andre.save()

blit(Maker, 'amberdawn')
amber = Maker(
    'amber',
    name='Amber Costley',
    html_url='http://ambercostley.com/',
    avatar_url='https://si0.twimg.com/profile_images/1452719858/twit.jpg',
)
amber.save()

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
