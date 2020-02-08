import datetime
import mongoengine

class Owner(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    Department = mongoengine.StringField(required=True)
    publication = mongoengine.ListField()
    grants = mongoengine.ListField()
    awards = mongoengine.ListField()
    teaching = mongoengine.ListField()
    miss = mongoengine.ListField()

    meta = {
        'db_alias': 'chor',
        'collection': 'owners'
    }


# 
# DEANAA
# DEANRA
# DEANSA
# ADEANFA
# ADEANAA
# ADEANRA
# ADEANSA
