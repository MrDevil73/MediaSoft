from django.db import models


class City(models.Model):
    name = models.TextField()


class Street(models.Model):
    name = models.TextField()
    id_city = models.ForeignKey(City, on_delete=models.PROTECT, db_column="id_city")


class Shop(models.Model):
    name = models.TextField()
    id_city = models.ForeignKey(City, on_delete=models.PROTECT, db_column="id_city")
    id_street = models.ForeignKey(Street, on_delete=models.PROTECT, db_column="id_street")
    house_number = models.IntegerField()
    time_open = models.TimeField()
    time_close = models.TimeField()
