from django.db.models.signals import pre_delete
from django.dispatch import receiver

from www.models import Journal
from reports.models import NAAccident


def clear_journal(instance):
    for record in Journal.objects.by_objects(instance):
        record.remove_related_object(instance)


@receiver(pre_delete, sender=NAAccident)
def clear_journal_vrf(sender, instance, **kwargs):
    clear_journal(instance)
