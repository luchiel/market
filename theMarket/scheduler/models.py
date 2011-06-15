from django.db import models
from django.db.models import signals
from django.dispatch import Signal
from datetime import datetime, timedelta
from mq import MessageQueue
import time

SIGNALS = {}

def connect(signal, receiver, *args, **kwargs):
    if not isinstance(signal, Signal):
        signal = SIGNALS.setdefault(signal, Signal())
    signal.connect(receiver, *args, **kwargs)

def message_handler(message):
    event = message['event']
    signal = event.signal
    if not isinstance(signal, Signal):
        signal = SIGNALS.setdefault(signal, Signal())
    signal.send(sender=event.__class__, instance=event)

message_queue = MessageQueue(message_handler)

def enqueue(sender, instance, **kwargs):
    if instance.is_pending:
        timestamp = time.mktime(instance.timestamp.timetuple())
        message_id = (sender, instance.pk)
        message = {'timestamp': timestamp, 'event': instance, 'id': message_id}
        message_queue.cancel(message_id)
        message_queue.enqueue(message)

def cancel(sender, instance, **kwargs):
    message_id = (sender, instance.pk)
    message_queue.cancel(message_id)

class Event(models.Model):
    signal = models.CharField(max_length=75)
    timestamp = models.DateTimeField(default=datetime.now, db_index=True)
    is_pending = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-is_pending', 'timestamp']
        get_latest_by = 'timestamp'

def setup(sender, **kwargs):
    if issubclass(sender, Event):
        signals.post_save.connect(enqueue, sender=sender, dispatch_uid='scheduler.models.enqueue')
        signals.post_delete.connect(cancel, sender=sender, dispatch_uid='scheduler.models.cancel')

signals.class_prepared.connect(setup, dispatch_uid='scheduler.models.setup')
setup(Event)
