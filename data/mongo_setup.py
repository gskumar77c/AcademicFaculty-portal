import mongoengine


def global_init():
    mongoengine.register_connection(alias='chor', name='faculty')
