# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BqResults(models.Model):
    store_id = models.CharField(primary_key=True, max_length=19)
    timezone_str = models.CharField(max_length=28, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bq_results'


class MenuHours(models.Model):
    store_id = models.CharField(max_length=19, blank=True, null=True)
    day = models.CharField(max_length=3, blank=True, null=True)
    start_time_local = models.CharField(max_length=16, blank=True, null=True)
    end_time_local = models.CharField(max_length=14, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu_hours'


class StoreStatus(models.Model):
    store_id = models.CharField(max_length=19, blank=True, null=True)
    status = models.CharField(max_length=6, blank=True, null=True)
    timestamp_utc = models.CharField(max_length=30, blank=True, null=True)
    id = models.CharField(max_length=30,primary_key=True)
    class Meta:
        managed = True
        db_table = 'store_status'

class Reports(models.Model):
    report_id = models.CharField(primary_key=True, max_length=90)
    status = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'reports'
