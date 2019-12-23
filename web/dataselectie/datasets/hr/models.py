from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class DataSelectie(models.Model):

    uid = models.CharField(
        max_length=21,
        db_index=True,
        unique=True,
    )

    nummeraanduiding = models.ForeignKey(
        'bag.Nummeraanduiding',
        to_field='landelijk_id',
        db_column='bag_numid',
        on_delete=models.DO_NOTHING,
        blank=True, null=True,
    )

    api_json = JSONField()

    class Meta(object):
        managed = False

    @property
    def bag_numid(self):
        """
        The actual DB column is named "bag_numid".
        Django provides access through it via the _id field.
        """
        return self.nummeraanduiding_id
