from typing import List, Optional
import datetime
import bson
import mongoengine


class Path(mongoengine.Document):
    admin = mongoengine.StringField(required=True)
    path = mongoengine.StringField(required=True)
    meta = {
        'db_alias': 'chor',
        'collection': 'path'
    }

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

active_account: Optional[Owner] = None








def create_account(name, email, background, publications, grants, awards, teaching) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email
    owner.Department = background
    owner.publication = publications
    owner.grants = grants
    owner.awards = awards
    owner.teaching = teaching
    owner.save()
    return owner

def create_account_by_flask(name, email, department, password) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email
    owner.Department = department
    owner.password = password
    owner.save()
    return owner


def savePath(pp):
    path = Path()
    path.admin = 'admin'
    path.path = pp
    path.save()


def deletePublication(emailid, pub):
    Owner.objects(email = emailid).update_one(pull__publication=pub)

def deleteGrants(emailid, pub):
    Owner.objects(email = emailid).update_one(pull__grants=pub)
    
def deleteAwards(emailid, pub):
    Owner.objects(email = emailid).update_one(pull__awards=pub)
    
def deleteTeaching(emailid, pub):
    Owner.objects(email = emailid).update_one(pull__teaching=pub)
    
def deleteMiss(emailid, pub):
    Owner.objects(email = emailid).update_one(pull__miss=pub)
    

def addPublication(emailid, pub):
    Owner.objects(email = emailid).update_one(push__publication=pub)

def addGrants(emailid, pub):
    Owner.objects(email = emailid).update_one(push__grants=pub)

def addAwards(emailid, pub):
    Owner.objects(email = emailid).update_one(push__awards=pub)

def addTeaching(emailid, pub):
    Owner.objects(email = emailid).update_one(push__teaching=pub)

def addMiss(emailid, pub):
    Owner.objects(email = emailid).update_one(push__miss=pub)

def find_account_by_email_and_password(email: str, password: str) -> Owner:
    owner = Owner.objects(email=email, password = password).first()
    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def getInfo(emailid):
    owner = find_account_by_email(emailid)
    info = {
        'name': owner.name,
        'email': owner.email,
        'department': owner.Department,
        'publication': owner.publication,
        'grants': owner.grants,
        'awards': owner.awards,
        'teaching': owner.teaching,
        'miss': owner.miss
    }
    return info

def isPathSet():
    return Path.objects.count()

def getPath():
    path_ = Path.objects(admin='admin').first()
    if(path_ is not None):
        return path_.path
    return 'NULL'
        
def changePath(pp):
    Path.objects(admin = 'admin').update_one(set__path=pp)



def reload_account():
    global active_account
    if not active_account:
        return

    active_account = find_account_by_email(active_account.email)