# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0002_auto_20150715_0747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskexecution',
            name='job',
            field=models.ForeignKey(related_name='task_executions', to='batch.JobExecution'),
        ),
    ]
