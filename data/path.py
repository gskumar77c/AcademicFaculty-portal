import datetime
import mongoengine

class Path(mongoengine.Document):
    admin = mongoengine.StringField(required=True)
    path = mongoengine.StringField(required=True)
    meta = {
        'db_alias': 'chor',
        'collection': 'path'
    }
