"""Migration generated by Django 1.11.29."""
import uuid

import main.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("main", "0076_version_number")]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="event_id",
            field=main.models.UUIDField(
                db_column="eventIdentifierUUID",
                null=True,
                unique=True,
                default=uuid.uuid4,
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="microservicechainlink",
            field=main.models.UUIDField(
                blank=True,
                db_column="MicroServiceChainLinksPK",
                null=True,
                default=uuid.uuid4,
            ),
        ),
        migrations.AlterField(
            model_name="siparrange",
            name="file_uuid",
            field=main.models.UUIDField(
                blank=True, default=uuid.uuid4, null=True, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="siparrange",
            name="transfer_uuid",
            field=main.models.UUIDField(blank=True, default=uuid.uuid4, null=True),
        ),
        migrations.AlterField(
            model_name="unitvariable",
            name="microservicechainlink",
            field=main.models.UUIDField(
                blank=True,
                db_column="microServiceChainLink",
                null=True,
                default=uuid.uuid4,
            ),
        ),
    ]
